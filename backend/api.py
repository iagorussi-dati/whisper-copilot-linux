"""API bridge exposed to the frontend via pywebview js_api.

Replicates all Tauri commands from commands.rs.
"""
import json
import logging
import os
import threading
import time
from dataclasses import asdict

import numpy as np
from dotenv import load_dotenv

from .audio import list_audio_devices, test_device, AudioCapture, wav_to_pcm
from .transcription import GroqClient, GroqError
from .diarization import VoiceBank, extract_embedding
from .llm import BedrockClient
from .config import AppConfig, Participant, load_config, save_config

load_dotenv()
log = logging.getLogger("whisper-copilot")

MAX_CONTEXT_LINES = 50


class Api:
    """Exposed to JS via window.pywebview.api.*"""

    def __init__(self):
        self._window = None  # set by main.py after window creation
        self._mic_capture: AudioCapture | None = None
        self._monitor_capture: AudioCapture | None = None
        self._transcript: list[dict] = []
        self._suggestions: list[str] = []
        self._groq: GroqClient | None = None
        self._bedrock: BedrockClient | None = None
        self._voice_bank: VoiceBank | None = None
        self._participants_context: str = ""
        self._my_label: str = "EU"
        self._start_time: float | None = None
        self._diarization_enabled: bool = True
        self._custom_system_prompt: str = ""
        self._suggestions_target: str = ""
        self._lock = threading.Lock()
        self._monitor_threads: dict[str, threading.Event] = {}

    def set_window(self, window):
        self._window = window

    def _emit(self, event: str, data):
        """Send event to frontend via evaluate_js."""
        if self._window:
            payload = json.dumps(data, ensure_ascii=True)
            self._window.evaluate_js(f"window.__emit('{event}', {payload})")

    # ── Device management ──

    def list_audio_devices(self) -> list[dict]:
        return list_audio_devices()

    def test_device(self, device_id: str, device_type: str) -> float:
        def on_level(level):
            self._emit("test_level", {"deviceId": device_id, "level": level})
        return test_device(device_id, device_type, duration=3, on_level=on_level)

    def start_monitor(self, device_id: str, device_type: str):
        self.stop_monitor(device_id)
        stop_event = threading.Event()
        self._monitor_threads[device_id] = stop_event

        def run():
            from .audio.devices import test_device as _test
            while not stop_event.is_set():
                try:
                    _test(device_id, device_type, duration=1,
                          on_level=lambda l: self._emit("audio_level", {"deviceId": device_id, "level": l}))
                except Exception:
                    pass
                stop_event.wait(0.1)

        threading.Thread(target=run, daemon=True).start()

    def stop_monitor(self, device_id: str):
        ev = self._monitor_threads.pop(device_id, None)
        if ev:
            ev.set()

    # ── Validation ──

    def validate_groq(self, api_key: str) -> bool:
        client = GroqClient(api_key)
        return client.validate()

    def validate_aws(self, profile: str = "", region: str = "") -> str:
        client = BedrockClient()
        return client.validate()

    # ── Config ──

    def save_config(self, config_dict: dict):
        cfg = AppConfig.from_dict(config_dict)
        save_config(cfg)

    def load_config(self) -> dict | None:
        cfg = load_config()
        return cfg.to_dict() if cfg else None

    def load_prompt_template(self, name: str) -> str:
        """Load a built-in prompt template by name."""
        import pathlib
        base = pathlib.Path(__file__).parent.parent
        paths = {
            "discovery": base / "Prompt_Modelo.md",
            "piadas": base / "prompts" / "piadas.md",
            "vendas": base / "prompts" / "vendas.md",
        }
        path = paths.get(name)
        if path and path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    # ── Meeting lifecycle ──

    def start_meeting(self, config_dict: dict):
        cfg = AppConfig.from_dict(config_dict)

        # Init Groq
        api_key = cfg.groq_api_key or os.getenv("GROQ_API_KEY", "")
        self._groq = GroqClient(api_key, cfg.whisper_model, cfg.language)

        # Init Bedrock
        self._bedrock = BedrockClient()

        # Pre-warm prompt cache in background
        if self._custom_system_prompt:
            def prewarm():
                log.info("Pre-warming prompt cache...")
                try:
                    self._bedrock.call_raw(self._custom_system_prompt, "Aguarde.", max_tokens=10)
                    log.info("Prompt cache warmed")
                except Exception as e:
                    log.warning(f"Cache warm failed: {e}")
            threading.Thread(target=prewarm, daemon=True).start()

        # Build participants context
        ctx_parts = []
        if cfg.my_name:
            ctx_parts.append(f"- EU (microfone): {cfg.my_name}")
        for p in cfg.participants:
            name = p.name if isinstance(p, Participant) else p.get("name", "")
            role = p.role if isinstance(p, Participant) else p.get("role", "")
            desc = f"{name} - {role}" if role else name
            ctx_parts.append(f"- {desc}")
        self._participants_context = (
            f"Participantes da reunião:\n" + "\n".join(ctx_parts) if ctx_parts else ""
        )

        self._my_label = cfg.my_name or "EU"
        self._suggestions_target = cfg.suggestions_target or self._my_label
        self._custom_system_prompt = self._build_system_prompt(cfg.custom_system_prompt)
        self._transcript = []
        self._suggestions = []
        self._start_time = time.time()

        chunk_dur = cfg.chunk_seconds

        # Start mic capture
        manual_mode = cfg.chunk_seconds == 0  # 0 = manual mode
        chunk_dur = cfg.chunk_seconds if not manual_mode else 9999

        if cfg.mic_device_id:
            self._mic_capture = AudioCapture(
                cfg.mic_device_id, "mic", chunk_dur,
                on_chunk=self._on_mic_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
                manual_mode=manual_mode,
            )
            self._mic_capture.start()

        # Start monitor capture
        if cfg.monitor_device_id:
            self._monitor_capture = AudioCapture(
                cfg.monitor_device_id, "monitor", chunk_dur,
                on_chunk=self._on_monitor_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
                manual_mode=manual_mode,
            )
            self._monitor_capture.start()

    def trigger_transcription(self):
        """Manual mode: flush audio buffers and process."""
        log.info("[Manual] Trigger transcription requested")
        if self._mic_capture:
            self._mic_capture.flush()
        if self._monitor_capture:
            self._monitor_capture.flush()

    def _on_mic_chunk(self, wav_bytes: bytes, source: str):
        """Process mic chunk: transcribe and emit as [EU]."""
        threading.Thread(target=self._process_mic_chunk, args=(wav_bytes,), daemon=True).start()

    def _process_mic_chunk(self, wav_bytes: bytes):
        try:
            text = self._groq.transcribe(wav_bytes).strip()
            if not text:
                return
            self._emit_transcript(self._my_label, text)
            self._request_suggestions()
        except GroqError as e:
            self._emit("error", {"code": "groq_error", "message": str(e)})
        except Exception as e:
            log.error(f"Mic chunk error: {e}")

    def _on_monitor_chunk(self, wav_bytes: bytes, source: str):
        """Process monitor chunk: verbose transcribe + diarization."""
        threading.Thread(target=self._process_monitor_chunk, args=(wav_bytes,), daemon=True).start()

    def _process_monitor_chunk(self, wav_bytes: bytes):
        import time
        start_time = time.time()
        
        try:
            # Step 1: Groq transcription
            t1 = time.time()
            log.info("[STEP 1] Enviando áudio pro Groq...")
            segments = self._groq.transcribe_verbose(wav_bytes)
            if not segments:
                log.warning("[STEP 1] Groq retornou 0 segmentos, pulando")
                return
            transcript_text = "\n".join(s.text.strip() for s in segments if s.text.strip())
            if not transcript_text:
                log.warning("[STEP 1] Transcrição vazia, pulando")
                return
            log.info(f"[STEP 1] Groq OK: {len(segments)} segs, {len(transcript_text)} chars, {time.time() - t1:.2f}s")
            log.info(f"[STEP 1] Primeiras 150 chars: {transcript_text[:150]}")

            # Step 2: Claude — identify speakers + generate suggestions
            t2 = time.time()
            participants_str = self._participants_context or "Participantes não informados. Deduza pelos conteúdos."
            earlier = "\n".join(f"[{e['speaker']}] {e['text'][:80]}" for e in self._transcript[-20:])
            earlier_ctx = f"\nContexto anterior:\n{earlier}\n" if earlier else ""

            user_msg = (
                f"{participants_str}{earlier_ctx}\n"
                f"[INSTRUÇÃO] Sugestões direcionadas para: {self._suggestions_target}\n\n"
                f"Transcrição do trecho atual:\n{transcript_text}"
            )

            log.info(f"[STEP 2] System prompt: {len(self._custom_system_prompt)} chars ({'VAZIO!' if not self._custom_system_prompt else 'OK'})")
            log.info(f"[STEP 2] User msg: {len(user_msg)} chars, target={self._suggestions_target}")
            log.info(f"[STEP 2] Enviando pro Claude Haiku...")

            result_text = self._bedrock.call_raw(self._custom_system_prompt, user_msg)

            log.info(f"[STEP 2] Claude respondeu em {time.time() - t2:.2f}s")
            log.info(f"[STEP 2] Resposta ({len(result_text)} chars): {repr(result_text[:300])}")

            # Step 3: Parse response — handle both JSON and free-form
            speakers_map = {}
            suggestions = []

            if result_text and result_text.strip() != "{}":
                clean = result_text.strip().strip("`").removeprefix("json").strip()
                
                # Try JSON format first (Haiku sometimes returns JSON)
                try:
                    parsed = json.loads(clean)
                    if isinstance(parsed, dict):
                        if "suggestions" in parsed:
                            suggestions = parsed["suggestions"]
                        if "speakers" in parsed:
                            speakers_map = parsed["speakers"]
                except json.JSONDecodeError:
                    pass
                
                # If no JSON, try free-form with emojis
                if not suggestions:
                    for line in result_text.strip().split("\n"):
                        line = line.strip()
                        if not line: continue
                        if any(line.startswith(e) for e in ["💡", "⚠", "🔴", "✅"]):
                            suggestions.append(line)
                
                # Last resort: treat whole response as suggestion
                if not suggestions and len(clean) > 20:
                    suggestions = [clean]
            
            log.info(f"[STEP 3] Parse: {len(speakers_map)} speakers, {len(suggestions)} sugestões")
            if suggestions:
                for i, s in enumerate(suggestions):
                    log.info(f"[STEP 3] Sugestão {i+1}: {s[:100]}")
            else:
                log.warning(f"[STEP 3] NENHUMA sugestão! Claude retornou: {repr(result_text[:200])}")

            # Step 4: Emit transcript with speaker attribution
            log.info(f"[STEP 4] Atribuindo speakers...")
            if speakers_map:
                log.info(f"[STEP 4] Speakers do Claude: {speakers_map}")
                self._emit("speaker_map", speakers_map)

            # Use participants context if available, otherwise use Claude's identification
            known_speakers = speakers_map
            if not known_speakers and self._participants_context:
                # Extract names from participants context
                import re
                names = re.findall(r'- (\w+)', self._participants_context)
                if names:
                    known_speakers = {f"speaker{i}": n for i, n in enumerate(names)}

            try:
                speaker_hint = json.dumps(known_speakers) if known_speakers else "desconhecidos"
                attr_system = (
                    "Atribua cada fala ao speaker correto baseado no conteúdo. "
                    "Quem conduz/organiza a reunião é o representante. Quem responde sobre sua empresa é o cliente. "
                    "Responda APENAS JSON: [{\"speaker\":\"Nome\",\"text\":\"fala\"}]. "
                    "Agrupe falas consecutivas do mesmo speaker."
                )
                attr_text = self._bedrock.call_raw(
                    attr_system,
                    f"Participantes: {speaker_hint}\n\nTranscrição:\n{transcript_text}",
                    max_tokens=2048, temperature=0.1)
                log.info(f"[STEP 4] Atribuição: {len(attr_text)} chars")
                parsed = json.loads(attr_text.strip().strip("`").removeprefix("json").strip())
                log.info(f"[STEP 4] {len(parsed)} entradas de transcript")
                for item in parsed:
                    sp = item.get("speaker", "OUTROS")
                    txt = item.get("text", "").strip()
                    if txt:
                        self._emit_transcript(sp, txt)
            except Exception as e:
                log.warning(f"[STEP 4] Atribuição falhou: {e}, emitindo como OUTROS")
                for seg in segments:
                    txt = seg.text.strip()
                    if txt:
                        self._emit_transcript("OUTROS", txt)

            # Step 5: Emit suggestions or done signal
            if suggestions:
                log.info(f"[STEP 5] Emitindo {len(suggestions)} sugestões pro frontend")
                self._suggestions.extend(suggestions)
                self._emit("suggestions", {"suggestions": suggestions})
            else:
                log.info("[STEP 5] IA não gerou sugestões neste trecho")
                self._emit("processing_done", {"had_suggestions": False})
            
            log.info(f"[DONE] Chunk processado em {time.time() - start_time:.2f}s total")

        except GroqError as e:
            log.error(f"[ERRO] Groq: {e}")
            self._emit("error", {"code": "groq_error", "message": str(e)})
        except Exception as e:
            log.error(f"[ERRO] Monitor chunk: {e}", exc_info=True)

    def _emit_transcript(self, speaker: str, text: str):
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        self._transcript.append(entry)
        self._emit("transcript", entry)

    def _request_suggestions(self):
        context = self._build_context()
        if not context or not self._bedrock:
            return
        try:
            # Prepend target info to context
            target_info = f"[INSTRUÇÃO] As sugestões são direcionadas para: {self._suggestions_target}\n\n"
            full_context = target_info + context
            result = self._bedrock.suggest(full_context, self._custom_system_prompt)
            if result and result.get("suggestions"):
                self._suggestions.extend(result["suggestions"])
                self._emit("suggestions", result)
        except Exception as e:
            log.error(f"Bedrock suggest error: {e}")

    def _build_system_prompt(self, custom_prompt: str) -> str:
        if not custom_prompt:
            return ""
        # Se o prompt já define formato de resposta, usar direto
        if '"suggestions"' in custom_prompt:
            return custom_prompt
        return (
            f"{custom_prompt}\n\n"
            f"FORMATO DE RESPOSTA (obrigatório):\n"
            f"Se não tiver nada relevante, responda exatamente: {{}}\n"
            f'Quando responder, use este JSON:\n'
            f'{{"suggestions": ["sugestão 1", "sugestão 2"]}}\n'
        )

    def _build_context(self) -> str:
        start = max(0, len(self._transcript) - MAX_CONTEXT_LINES)
        return "\n".join(
            f"[{e['speaker']}] {e['text']}" for e in self._transcript[start:]
        )

    def stop_meeting(self) -> dict:
        if self._mic_capture:
            self._mic_capture.stop()
            self._mic_capture = None
        if self._monitor_capture:
            self._monitor_capture.stop()
            self._monitor_capture = None

        transcript = list(self._transcript)
        suggestions = list(self._suggestions)

        # Generate summary
        full_text = "\n".join(f"[{e['speaker']}] {e['text']}" for e in transcript)
        summary = ""
        if self._bedrock:
            try:
                summary = self._bedrock.generate_summary(full_text, suggestions)
            except Exception as e:
                summary = f"Erro ao gerar resumo: {e}"

        self._voice_bank = VoiceBank(0.30)
        self._start_time = None

        return {"transcript": transcript, "suggestions": suggestions, "summary": summary}

    def generate_summary(self, transcript_text: str, suggestions: list[str]) -> str:
        if not self._bedrock:
            return "Bedrock não disponível."
        return self._bedrock.generate_summary(transcript_text, suggestions)
