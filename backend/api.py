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
        self._recording = False
        self._hotkey_stop = threading.Event()
        self._start_hotkey_watcher()

    def set_window(self, window):
        self._window = window

    HOTKEY_FILE = "/tmp/whisper-copilot-toggle"
    _hotkey_key: str = ""

    def _start_hotkey_watcher(self):
        """Watch /tmp/whisper-copilot-toggle for global hotkey signals."""
        import pathlib
        pathlib.Path(self.HOTKEY_FILE).unlink(missing_ok=True)

        def watch():
            while not self._hotkey_stop.is_set():
                try:
                    p = pathlib.Path(self.HOTKEY_FILE)
                    if p.exists():
                        p.unlink(missing_ok=True)
                        log.info("[Hotkey] Global toggle received")
                        self.toggle_recording()
                except Exception as e:
                    log.error(f"[Hotkey] Error: {e}")
                self._hotkey_stop.wait(0.2)

        threading.Thread(target=watch, daemon=True).start()

    def register_global_hotkey(self, key: str):
        """Register SUPER+key as global hotkey via hyprctl."""
        self.unregister_global_hotkey()
        if not key:
            return
        self._hotkey_key = key
        import subprocess
        toggle_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "whisper-toggle.sh")
        cmd = f"SUPER,{key},exec,{toggle_script}"
        try:
            subprocess.run(["hyprctl", "keyword", "bind", cmd],
                           capture_output=True, timeout=3)
            log.info(f"[Hotkey] Registered SUPER+{key}")
        except Exception as e:
            log.error(f"[Hotkey] Failed to register: {e}")

    def unregister_global_hotkey(self):
        """Remove global hotkey bind."""
        if not self._hotkey_key:
            return
        import subprocess
        try:
            subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{self._hotkey_key}"],
                           capture_output=True, timeout=3)
            log.info(f"[Hotkey] Unregistered SUPER+{self._hotkey_key}")
        except Exception:
            pass
        self._hotkey_key = ""

    def toggle_recording(self):
        """Toggle recording state (called from JS or global hotkey)."""
        if not self._start_time:
            return
        if self._recording:
            self._recording = False
            self._emit("recording_state", {"recording": False})
            self.stop_recording()
        else:
            self._recording = True
            self._emit("recording_state", {"recording": True})
            self.start_recording()

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
        for p in cfg.participants:
            name = p.name if isinstance(p, Participant) else p.get("name", "")
            role = p.role if isinstance(p, Participant) else p.get("role", "")
            if not name:
                continue
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

        if cfg.mic_device_id and cfg.mic_device_id != "none":
            self._mic_capture = AudioCapture(
                cfg.mic_device_id, "mic", chunk_dur,
                on_chunk=self._on_mic_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
                manual_mode=manual_mode,
            )
            if not manual_mode:
                self._mic_capture.start()

        # Start monitor capture
        if cfg.monitor_device_id and cfg.monitor_device_id != "none":
            self._monitor_capture = AudioCapture(
                cfg.monitor_device_id, "monitor", chunk_dur,
                on_chunk=self._on_monitor_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
                manual_mode=manual_mode,
            )
            if not manual_mode:
                self._monitor_capture.start()

        # Register global hotkey
        if cfg.global_hotkey:
            self.register_global_hotkey(cfg.global_hotkey)

    def start_recording(self):
        """Manual mode: start capturing audio."""
        log.info("[Manual] Start recording")
        if self._mic_capture:
            self._mic_capture.start()
        if self._monitor_capture:
            self._monitor_capture.start()

    def stop_recording(self):
        """Manual mode: stop capturing and transcribe."""
        log.info("[Manual] Stop recording, flushing...")
        mic_pcm = None
        mon_pcm = None
        if self._mic_capture:
            mic_pcm = self._mic_capture.flush_pcm()
            self._mic_capture.stop()
        if self._monitor_capture:
            mon_pcm = self._monitor_capture.flush_pcm()
            self._monitor_capture.stop()

        if mic_pcm is None and mon_pcm is None:
            log.info("[Manual] No audio captured")
            self._emit("recording_done", {"had_audio": False})
            return

        if mic_pcm is not None and mon_pcm is not None:
            max_len = max(len(mic_pcm), len(mon_pcm))
            mic_f = np.zeros(max_len, dtype=np.float32)
            mon_f = np.zeros(max_len, dtype=np.float32)
            mic_f[:len(mic_pcm)] = mic_pcm.astype(np.float32)
            mon_f[:len(mon_pcm)] = mon_pcm.astype(np.float32)
            mixed = np.clip(mic_f + mon_f, -32768, 32767).astype(np.int16)
        else:
            mixed = mic_pcm if mic_pcm is not None else mon_pcm

        from .audio.wav import pcm_to_wav
        wav_bytes = pcm_to_wav(mixed, 16000)
        log.info(f"[Manual] Audio: {len(mixed)} samples ({len(mixed)/16000:.1f}s)")
        threading.Thread(target=self._process_monitor_chunk, args=(wav_bytes,), daemon=True).start()

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

            self._process_monitor_text(transcript_text, segments)

        except GroqError as e:
            log.error(f"[ERRO] Groq: {e}")
            self._emit("error", {"code": "groq_error", "message": str(e)})
        except Exception as e:
            log.error(f"[ERRO] Monitor chunk: {e}", exc_info=True)

    def _process_monitor_text(self, transcript_text: str, segments: list | None = None):
        """Process transcribed text: Bedrock attributes speakers + generates suggestions."""
        import time
        start_time = time.time()

        earlier_ctx = "\n".join(f"[{e['speaker']}] {e['text'][:80]}" for e in self._transcript[-20:])

        try:
            participants_str = self._participants_context or "Participantes não informados. Deduza pelos conteúdos."
            earlier_block = f"\nContexto anterior:\n{earlier_ctx}\n" if earlier_ctx else ""

            # Single Bedrock call: attribute speakers + generate suggestions
            speaker_instruction = (
                "\n\nCOMO IDENTIFICAR QUEM FALA:\n"
                "- Analise o PAPEL de cada participante para atribuir as falas\n"
                "- Quem conduz a reunião (faz perguntas, propõe soluções) geralmente é o organizador\n"
                "- Quem responde sobre sua empresa/situação geralmente é o cliente\n"
                "- Quem PERGUNTA 'vocês são de [cidade]?' NÃO é dessa cidade\n"
                "- Quem RESPONDE 'sim, somos de [cidade]' É dessa cidade\n"
                "- Quem se apresenta ('eu sou...', 'moro em...') fala de si mesmo\n"
                "- Frases de condução ('a ideia é entender', 'montar uma proposta') = organizador\n\n"
                "IMPORTANTE: Inclua TODAS as falas, não pule nenhuma.\n"
                "Agrupe APENAS falas consecutivas do mesmo speaker.\n"
                'Formato JSON obrigatório: {"transcript": [{"speaker": "Nome", "text": "fala"}], "suggestions": ["sugestão"]}\n'
                "Se não tiver sugestões relevantes, retorne suggestions como array vazio."
            )

            system = self._custom_system_prompt or ""
            system += (
                "\nVocê atribui falas aos participantes de reuniões e gera sugestões. "
                "Responda SOMENTE JSON puro sem markdown, sem explicações."
            )

            user_msg = (
                f"{participants_str}{earlier_block}\n"
                f"[INSTRUÇÃO] Sugestões direcionadas para: {self._suggestions_target}\n"
                f"{speaker_instruction}\n\n"
                f"Transcrição do trecho atual:\n{transcript_text}"
            )

            log.info(f"[STEP 2] System prompt: {len(system)} chars")
            log.info(f"[STEP 2] User msg: {len(user_msg)} chars, target={self._suggestions_target}")
            log.info(f"[STEP 2] Enviando pro Bedrock...")

            t2 = time.time()
            result_text = self._bedrock.call_raw(system, user_msg, max_tokens=4096)

            log.info(f"[STEP 2] Bedrock respondeu em {time.time() - t2:.2f}s")
            log.info(f"[STEP 2] Resposta ({len(result_text)} chars): {repr(result_text[:300])}")

            # Parse JSON response — find JSON object in response (may have markdown/text around it)
            transcript_entries = []
            suggestions = []
            depth = 0
            start = None
            for i, c in enumerate(result_text):
                if c == '{':
                    if depth == 0: start = i
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0 and start is not None:
                        try:
                            parsed = json.loads(result_text[start:i+1])
                            transcript_entries = parsed.get("transcript", [])
                            suggestions = parsed.get("suggestions", [])
                            break
                        except json.JSONDecodeError:
                            start = None
            if not transcript_entries:
                log.warning(f"[STEP 2] JSON parse failed, emitting raw")

            # Emit transcript with speakers
            if transcript_entries:
                for item in transcript_entries:
                    sp = item.get("speaker", "OUTROS")
                    txt = item.get("text", "").strip()
                    if txt:
                        self._emit_transcript(sp, txt)
                log.info(f"[STEP 3] {len(transcript_entries)} entradas com speakers")
            else:
                # Fallback: emit without speaker attribution
                for line in transcript_text.split("\n"):
                    line = line.strip()
                    if line:
                        self._emit_transcript("CONVERSA", line)

            # Emit suggestions
            if suggestions:
                log.info(f"[STEP 4] {len(suggestions)} sugestões")
                self._suggestions.extend(suggestions)
                self._emit("suggestions", {"suggestions": suggestions})
            else:
                log.info("[STEP 4] Nenhuma sugestão neste trecho")
                self._emit("processing_done", {"had_suggestions": False})

            log.info(f"[DONE] Chunk processado em {time.time() - start_time:.2f}s total")

        except Exception as e:
            log.error(f"[ERRO] Process text: {e}", exc_info=True)
            # Fallback: emit raw transcript
            for line in transcript_text.split("\n"):
                line = line.strip()
                if line:
                    self._emit_transcript("CONVERSA", line)

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
        self.unregister_global_hotkey()
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
