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
        self._lock = threading.Lock()
        self._monitor_threads: dict[str, threading.Event] = {}

    def set_window(self, window):
        self._window = window

    def _emit(self, event: str, data):
        """Send event to frontend via evaluate_js."""
        if self._window:
            payload = json.dumps(data, ensure_ascii=False)
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
        proxy_url = os.getenv("BEDROCK_PROXY_URL",
                              "https://i1pktfzmo0.execute-api.us-east-1.amazonaws.com/chat")
        proxy_key = os.getenv("BEDROCK_PROXY_KEY", "whisper-copilot-2026")
        client = BedrockClient(proxy_url, proxy_key)
        return client.validate()

    # ── Config ──

    def save_config(self, config_dict: dict):
        cfg = AppConfig.from_dict(config_dict)
        save_config(cfg)

    def load_config(self) -> dict | None:
        cfg = load_config()
        return cfg.to_dict() if cfg else None

    # ── Meeting lifecycle ──

    def start_meeting(self, config_dict: dict):
        cfg = AppConfig.from_dict(config_dict)

        # Init Groq
        api_key = cfg.groq_api_key or os.getenv("GROQ_API_KEY", "")
        self._groq = GroqClient(api_key, cfg.whisper_model, cfg.language)

        # Init Bedrock
        proxy_url = os.getenv("BEDROCK_PROXY_URL",
                              "https://i1pktfzmo0.execute-api.us-east-1.amazonaws.com/chat")
        proxy_key = os.getenv("BEDROCK_PROXY_KEY", "whisper-copilot-2026")
        self._bedrock = BedrockClient(proxy_url, proxy_key)

        # Init voice bank
        self._diarization_enabled = cfg.diarization_provider != "none"
        self._voice_bank = VoiceBank(cfg.diarization_threshold)
        
        # Pre-load SpeechBrain model if diarization enabled (in background)
        if self._diarization_enabled:
            def preload_model():
                log.info("Pre-loading SpeechBrain model...")
                try:
                    from .diarization.engine import _get_model
                    import time
                    start = time.time()
                    _get_model()
                    elapsed = time.time() - start
                    log.info(f"SpeechBrain model loaded in {elapsed:.1f}s")
                except Exception as e:
                    log.warning(f"Failed to pre-load SpeechBrain: {e}. Will load on first use.")
            
            threading.Thread(target=preload_model, daemon=True).start()

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
        self._transcript = []
        self._suggestions = []
        self._start_time = time.time()

        chunk_dur = cfg.chunk_seconds

        # Start mic capture
        if cfg.mic_device_id:
            self._mic_capture = AudioCapture(
                cfg.mic_device_id, "mic", chunk_dur,
                on_chunk=self._on_mic_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
            )
            self._mic_capture.start()

        # Start monitor capture
        if cfg.monitor_device_id:
            self._monitor_capture = AudioCapture(
                cfg.monitor_device_id, "monitor", chunk_dur,
                on_chunk=self._on_monitor_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
            )
            self._monitor_capture.start()

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
            # Step 1: Groq verbose transcription
            t1 = time.time()
            segments = self._groq.transcribe_verbose(wav_bytes)
            if not segments:
                return
            log.info(f"Transcription took {time.time() - t1:.2f}s")

            # Step 2: Extract embeddings per segment (parallelized)
            t2 = time.time()
            pcm = wav_to_pcm(wav_bytes)
            voice_labels: list[str | None] = []

            if self._diarization_enabled and len(pcm) > 0:
                # Process embeddings in parallel for speed
                import concurrent.futures
                
                # Filter and prepare segments (skip very short ones)
                segments_to_process = []
                for i, seg in enumerate(segments):
                    dur = seg.end - seg.start
                    if dur >= 1.5:  # Only >= 1.5s for better accuracy
                        s = int(seg.start * 16000)
                        e = min(int(seg.end * 16000), len(pcm))
                        if e > s and e - s >= 12000:
                            segments_to_process.append((i, seg, s, e))
                
                log.info(f"Processing {len(segments_to_process)}/{len(segments)} segments")
                
                def process_segment(item):
                    idx, seg, s, e = item
                    emb = extract_embedding(pcm[s:e])
                    return (idx, emb)
                
                # Use 6 workers for better performance
                embeddings_map = {}
                if segments_to_process:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                        results = executor.map(process_segment, segments_to_process)
                        for idx, emb in results:
                            if emb is not None:
                                embeddings_map[idx] = emb
                
                # Assign voice labels
                for i, seg in enumerate(segments):
                    if i in embeddings_map:
                        emb = embeddings_map[i]
                        dur = seg.end - seg.start
                        with self._lock:
                            match = self._voice_bank.match_or_create(emb)
                            if not match.is_new and dur >= 2.0:
                                self._voice_bank.update_embedding(match.voice_label, emb)
                        voice_labels.append(match.voice_label)
                    else:
                        voice_labels.append(None)
                
                log.info(f"Diarization took {time.time() - t2:.2f}s ({len(embeddings_map)} embeddings)")
            else:
                voice_labels = [None] * len(segments)

            # Step 3: Build and emit transcript entries
            entries: list[tuple[str, str]] = []
            for i, seg in enumerate(segments):
                text = seg.text.strip()
                if not text:
                    continue
                if self._diarization_enabled:
                    raw = voice_labels[i] or "OUTROS"
                    with self._lock:
                        speaker = self._voice_bank.display_name(raw)
                else:
                    speaker = "OUTROS"
                entries.append((speaker, text))

            # Merge consecutive same-speaker
            merged: list[tuple[str, str]] = []
            for sp, text in entries:
                if merged and merged[-1][0] == sp:
                    merged[-1] = (sp, merged[-1][1] + " " + text)
                else:
                    merged.append((sp, text))

            for speaker, text in merged:
                self._emit_transcript(speaker, text)
            
            log.info(f"Monitor chunk processed in {time.time() - start_time:.2f}s total")

            # Step 4: Ask Claude to identify speakers if needed
            if (self._diarization_enabled and self._participants_context
                    and self._voice_bank.has_unnamed()):
                voice_ctx = self._voice_bank.build_context()
                existing = {k: v for k, v in self._voice_bank.speakers() if v}
                existing_str = f"\nMapeamento já identificado: {existing}\n" if existing else ""

                recent = "\n".join(f"[{sp}] {txt}" for sp, txt in merged)
                earlier = "\n".join(
                    f"[{e['speaker']}] {e['text']}"
                    for e in self._transcript[-30:]
                )

                prompt = (
                    f"{self._participants_context}\n\n{voice_ctx}{existing_str}"
                    f"Transcrição:\n{earlier}\n{recent}\n\n"
                    f'Identifique cada Voz. JSON: {{"Voz 1": "Nome", "Voz 2": "Nome"}}'
                )

                try:
                    mapping = self._bedrock.identify_speakers(prompt)
                    if mapping:
                        with self._lock:
                            self._voice_bank.set_name_map(mapping)
                        self._emit("speaker_map", mapping)
                except Exception as e:
                    log.error(f"Speaker ID error: {e}")

            # Step 5: Suggestions
            self._request_suggestions()

        except GroqError as e:
            self._emit("error", {"code": "groq_error", "message": str(e)})
        except Exception as e:
            log.error(f"Monitor chunk error: {e}")

    def _emit_transcript(self, speaker: str, text: str):
        entry = {"speaker": speaker, "text": text, "timestamp": int(time.time())}
        self._transcript.append(entry)
        self._emit("transcript", entry)

    def _request_suggestions(self):
        context = self._build_context()
        if not context or not self._bedrock:
            return
        try:
            result = self._bedrock.suggest(context)
            if result and result.get("suggestions"):
                self._suggestions.extend(result["suggestions"])
                self._emit("suggestions", result)
        except Exception as e:
            log.error(f"Bedrock suggest error: {e}")

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

        self._voice_bank = VoiceBank(0.20)
        self._start_time = None

        return {"transcript": transcript, "suggestions": suggestions, "summary": summary}

    def generate_summary(self, transcript_text: str, suggestions: list[str]) -> str:
        if not self._bedrock:
            return "Bedrock não disponível."
        return self._bedrock.generate_summary(transcript_text, suggestions)
