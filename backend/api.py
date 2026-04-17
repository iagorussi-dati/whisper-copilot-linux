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
        self._chat_window = None
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
        self._pending_wav = None
        self._pending_instruction = ""
        self._chat_history: list[dict] = []
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
                        cmd = p.read_text().strip()
                        p.unlink(missing_ok=True)
                        if cmd == "snapshot":
                            log.info("[Hotkey] Snapshot received")
                            self.snapshot()
                        else:
                            log.info("[Hotkey] Global toggle received")
                            self.toggle_recording()
                except Exception as e:
                    log.error(f"[Hotkey] Error: {e}")
                self._hotkey_stop.wait(0.2)

        threading.Thread(target=watch, daemon=True).start()

    def register_global_hotkey(self, key: str):
        """Register SUPER+key for toggle and SUPER+snapshot_key for snapshot."""
        self.unregister_global_hotkey()
        if not key:
            return
        self._hotkey_key = key
        import subprocess
        base = os.path.dirname(os.path.abspath(__file__))
        toggle_script = os.path.join(base, "..", "whisper-toggle.sh")
        snapshot_script = os.path.join(base, "..", "whisper-snapshot.sh")
        try:
            subprocess.run(["hyprctl", "keyword", "bind", f"SUPER,{key},exec,{toggle_script}"],
                           capture_output=True, timeout=3)
            log.info(f"[Hotkey] Registered SUPER+{key} (toggle)")
            if self._snapshot_key:
                subprocess.run(["hyprctl", "keyword", "bind", f"SUPER,{self._snapshot_key},exec,{snapshot_script}"],
                               capture_output=True, timeout=3)
                log.info(f"[Hotkey] Registered SUPER+{self._snapshot_key} (snapshot)")
        except Exception as e:
            log.error(f"[Hotkey] Failed: {e}")

    def unregister_global_hotkey(self):
        """Remove global hotkey binds."""
        import subprocess
        if self._hotkey_key:
            try:
                subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{self._hotkey_key}"],
                               capture_output=True, timeout=3)
            except Exception:
                pass
        if getattr(self, '_snapshot_key', ''):
            try:
                subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{self._snapshot_key}"],
                               capture_output=True, timeout=3)
            except Exception:
                pass
        log.info(f"[Hotkey] Unregistered all")
        self._hotkey_key = ""

    def toggle_recording(self):
        """Toggle recording: start/stop capture."""
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

    def snapshot(self):
        """Transcribe what's recorded so far WITHOUT stopping. Recording continues."""
        if not self._start_time or not self._recording:
            return
        log.info("[SNAPSHOT] Flushing current audio (recording continues)...")
        self._emit("snapshot_started", {})

        mic_pcm = self._mic_capture.flush_pcm() if self._mic_capture else None
        mon_pcm = self._monitor_capture.flush_pcm() if self._monitor_capture else None
        log.info(f"[SNAPSHOT] mic={'None' if mic_pcm is None else f'{len(mic_pcm)} samples'} mon={'None' if mon_pcm is None else f'{len(mon_pcm)} samples'}")

        if mic_pcm is None and mon_pcm is None:
            log.info("[SNAPSHOT] No audio to flush")
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
        wav = pcm_to_wav(mixed, 16000)
        log.info(f"[SNAPSHOT] {len(mixed)/16000:.1f}s of audio")

        def process():
            self._process_auto_chunk(wav)
            log.info(f"[SNAPSHOT] Done. Transcript: {len(self._transcript)} entries. Recording continues.")
            if self._auto_response:
                self.submit_recording('')
            else:
                self._focus_popup()
                time.sleep(0.3)
                self._emit_to_popup("focus_input", {})

        threading.Thread(target=process, daemon=True).start()

    def _emit(self, event: str, data):
        """Send event to frontend via evaluate_js (non-blocking)."""
        # Save chat-relevant events to history
        if event in ('transcript', 'copilot_response', 'recording_state', 'recording_stopped'):
            self._chat_history.append({"event": event, "data": data})
        payload = json.dumps(data, ensure_ascii=True)
        js = f"window.__emit('{event}', {payload})"
        for w in [self._window, self._chat_window]:
            if w:
                try:
                    w.evaluate_js(js)
                except Exception as e:
                    log.warning(f"[Emit] {event} failed: {e}")

    def get_chat_history(self) -> list[dict]:
        """Return chat history for popup restore."""
        return list(self._chat_history)

    def get_suggestion_format(self) -> str:
        """Return the suggestion format instruction (read-only preview)."""
        return self.APP_FORMAT_SUGGESTION

    def _open_chat_popup(self):
        """Open chat as sidebar on the right."""
        import webview
        if self._chat_window:
            try:
                _ = self._chat_window.title
                return
            except Exception:
                self._chat_window = None

        # Will position as sidebar after window loads
        self._needs_sidebar_position = True

        chat_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "chat-popup.html")
        self._chat_window = webview.create_window(
            "Whisper Chat",
            url=chat_html,
            js_api=self,
            width=420,
            height=1080,
            on_top=True,
            background_color="#0f172a",
        )
        self._chat_window_ready = False
        def on_loaded():
            self._chat_window_ready = True
            log.info("[POPUP] Window loaded and ready")
            if getattr(self, '_needs_sidebar_position', False):
                self._position_sidebar()
        def on_closed():
            self._chat_window = None
            self._chat_window_ready = False
        self._chat_window.events.loaded += on_loaded
        self._chat_window.events.closed += on_closed

    # ── Device management ──

    def list_audio_devices(self) -> list[dict]:
        return list_audio_devices()

    def test_device(self, device_id: str, device_type: str):
        log.info(f"[Test] Starting test: {device_id} ({device_type})")
        def run():
            try:
                def on_level(level):
                    self._emit("test_level", {"deviceId": device_id, "level": level})
                peak = test_device(device_id, device_type, duration=3, on_level=on_level)
                log.info(f"[Test] Done: peak={peak:.6f}")
                self._emit("test_done", {"deviceId": device_id, "type": device_type, "peak": peak})
            except Exception as e:
                log.error(f"[Test] Error: {e}")
                self._emit("test_done", {"deviceId": device_id, "type": device_type, "peak": 0.0})
        threading.Thread(target=run, daemon=True).start()

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
            "conversa": base / "prompts" / "conversa-natural.md",
            "sugestoes": base / "prompts" / "sugestoes.md",
            "assistente": base / "prompts" / "assistente-objetivo.md",
            "pesquisa": base / "prompts" / "pesquisa.md",
            "discovery": base / "Prompt_Modelo.md",
            "tecnico": base / "prompts" / "consultor-tecnico.md",
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
        if cfg.participant_mode == "many":
            ctx = cfg.many_context or ""
            self._participants_context = (
                f"Contexto: {ctx}\n" if ctx else ""
            ) + "Várias pessoas falando. Identifique pelos nomes mencionados na conversa."
        elif cfg.participant_mode == "none":
            identity = cfg.user_identity or ""
            self._participants_context = (
                f"Sobre o usuário: {identity}\n" if identity else ""
            ) + "Identifique os participantes pelos nomes mencionados na conversa. Ajude o usuário diretamente."
        else:
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
        self._raw_system_prompt = cfg.custom_system_prompt or ""
        if cfg.extra_context:
            self._raw_system_prompt += f"\n\nContexto adicional do usuário:\n{cfg.extra_context}"
        self._custom_system_prompt = self._build_system_prompt(self._raw_system_prompt)
        self._response_mode = cfg.response_mode or "short"
        self._auto_response = bool(cfg.auto_response) if not isinstance(cfg.auto_response, str) else cfg.auto_response.lower() == 'true'
        self._transcript = []
        self._suggestions = []
        self._chat_history = []
        self._start_time = time.time()
        self._emit("session_reset", {})

        log.info(f"[START] === MEETING STARTED ===")
        log.info(f"[START] response_mode={self._response_mode}")
        log.info(f"[START] auto_response={self._auto_response}")
        log.info(f"[START] target={self._suggestions_target}")
        log.info(f"[START] system_prompt={len(self._raw_system_prompt)} chars: {self._raw_system_prompt[:80]}")
        log.info(f"[START] participants={self._participants_context[:100]}")
        log.info(f"[START] mic={cfg.mic_device_id[:50] if cfg.mic_device_id else 'none'}")
        log.info(f"[START] monitor={cfg.monitor_device_id[:50] if cfg.monitor_device_id else 'none'}")
        log.info(f"[START] chunk_seconds={cfg.chunk_seconds}")
        log.info(f"[START] hotkey={cfg.global_hotkey}")

        chunk_dur = max(cfg.chunk_seconds, 60)  # min 60s chunks for auto-transcribe

        if cfg.mic_device_id and cfg.mic_device_id != "none":
            self._mic_capture = AudioCapture(
                cfg.mic_device_id, "mic", chunk_dur,
                on_chunk=self._on_mic_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
                manual_mode=False,
            )

        if cfg.monitor_device_id and cfg.monitor_device_id != "none":
            self._monitor_capture = AudioCapture(
                cfg.monitor_device_id, "monitor", chunk_dur,
                on_chunk=self._on_monitor_chunk,
                on_level=lambda src, lvl: self._emit("audio_level", {"source": src, "level": lvl}),
                on_status=lambda src, st: self._emit("status", {"source": src, "status": st}),
                manual_mode=False,
            )

        self._snapshot_key = cfg.snapshot_hotkey or ""
        if cfg.global_hotkey:
            self.register_global_hotkey(cfg.global_hotkey)

        # Open chat popup immediately
        self._open_chat_popup()

    def start_recording(self):
        """Start capturing audio."""
        log.info("[REC] Start recording")
        if self._mic_capture:
            self._mic_capture.start()
        if self._monitor_capture:
            self._monitor_capture.start()

    def stop_recording(self):
        """Stop capturing, flush remaining audio, transcribe it."""
        log.info("[REC] Stop recording")
        # Flush BEFORE stopping (stop clears the thread)
        mic_pcm = self._mic_capture.flush_pcm() if self._mic_capture else None
        mon_pcm = self._monitor_capture.flush_pcm() if self._monitor_capture else None

        if self._mic_capture:
            self._mic_capture.stop()
        if self._monitor_capture:
            self._monitor_capture.stop()

        self._emit("recording_stopped", {"had_audio": mic_pcm is not None or mon_pcm is not None})

        if mic_pcm is None and mon_pcm is None:
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
        wav = pcm_to_wav(mixed, 16000)
        log.info(f"[REC] Flushing remaining {len(mixed)/16000:.1f}s")

        def flush_and_respond():
            self._process_auto_chunk(wav)
            # Wait for popup to be ready
            start_wait = time.time()
            while not getattr(self, '_chat_window_ready', True) and time.time() - start_wait < 5:
                time.sleep(0.1)
            log.info(f"[REC] Popup ready={getattr(self, '_chat_window_ready', '?')} (waited {time.time()-start_wait:.1f}s)")
            log.info(f"[REC] auto_response={self._auto_response}")

            # Focus popup via hyprctl (Wayland)
            time.sleep(0.5)
            self._focus_popup()

            if self._auto_response:
                log.info("[REC] Auto-response: generating response...")
                self.submit_recording('')
            else:
                log.info("[REC] Waiting for user instruction (auto_response=False)")
                # Focus input inside popup AFTER window has focus
                time.sleep(0.3)
                self._emit_to_popup("focus_input", {})

        threading.Thread(target=flush_and_respond, daemon=True).start()



    def _position_sidebar(self):
        """Position the chat popup as a sidebar on the right edge."""
        import shutil
        if not shutil.which("hyprctl"):
            return
        try:
            import subprocess, json as _json
            time.sleep(0.5)  # wait for window to be registered
            r = subprocess.run(["hyprctl", "clients", "-j"], capture_output=True, text=True, timeout=2)
            clients = _json.loads(r.stdout)
            chat = next((c for c in clients if c.get("title") == "Whisper Chat"), None)
            if not chat:
                log.debug("[SIDEBAR] Chat window not found in hyprctl")
                return
            addr = chat["address"]
            r2 = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True, text=True, timeout=2)
            mon = _json.loads(r2.stdout)[0]
            mw = int(mon["width"] / mon["scale"])
            mh = int(mon["height"] / mon["scale"])
            sw = 420
            subprocess.run(["hyprctl", "dispatch", f"setfloating address:{addr}"], capture_output=True, timeout=2)
            time.sleep(0.1)
            subprocess.run(["hyprctl", "dispatch", f"resizewindowpixel exact {sw} {mh},address:{addr}"], capture_output=True, timeout=2)
            subprocess.run(["hyprctl", "dispatch", f"movewindowpixel exact {mw - sw} 0,address:{addr}"], capture_output=True, timeout=2)
            subprocess.run(["hyprctl", "dispatch", f"pin address:{addr}"], capture_output=True, timeout=2)
            log.info(f"[SIDEBAR] Positioned: {sw}x{mh} at x={mw - sw}")
        except Exception as e:
            log.debug(f"[SIDEBAR] Failed: {e}")

    def _focus_popup(self):
        """Focus the popup window via hyprctl (Wayland/Hyprland)."""
        if not self._chat_window:
            return
        try:
            import subprocess, json as _json
            r = subprocess.run(["hyprctl", "clients", "-j"], capture_output=True, text=True, timeout=2)
            clients = _json.loads(r.stdout)
            our_windows = [c for c in clients if "main.py" in c.get("class", "")]
            if len(our_windows) > 1:
                popup = min(our_windows, key=lambda c: c["size"][0] * c["size"][1])
                subprocess.run(["hyprctl", "dispatch", "focuswindow", f"address:{popup['address']}"],
                               capture_output=True, timeout=2)
                log.info(f"[FOCUS] Focused popup: {popup['address']}")
        except Exception as e:
            log.debug(f"[FOCUS] Failed: {e}")

    def _emit_to_popup(self, event, data):
        """Send event only to popup window."""
        if self._chat_window:
            try:
                payload = json.dumps(data, ensure_ascii=True)
                self._chat_window.evaluate_js(f"window.__emit('{event}', {payload})")
            except Exception:
                pass
    APP_FORMAT_SUGGESTION = (
        "\nFORMATO DE RESPOSTA (obrigatório, sem exceção):\n"
        "Cada sugestão = 1 linha com emoji e frase entre aspas.\n"
        "NÃO use markdown, NÃO use títulos, NÃO use listas com -, NÃO use negrito.\n"
        "Emojis: 🔴 erro crítico, ⚠️ atenção, 💡 oportunidade, ✅ pronto pra próximo passo\n"
        "Exemplo:\n"
        '🔴 "Cliente, qual a dor real que motiva essa migração?"\n'
        '💡 "Cliente, qual o volume de requests por segundo hoje?"'
    )

    @staticmethod
    def _trim_to_sentence(text: str) -> str:
        """Trim text at the last complete sentence."""
        text = text.strip()
        if not text:
            return text
        if text[-1] in '.!?")\':':
            return text
        # Find last sentence-ending punctuation
        for i in range(len(text) - 1, -1, -1):
            if text[i] in '.!?':
                return text[:i + 1]
        return text  # no punctuation found, return as-is

    @staticmethod
    def _clean_md(text: str) -> str:
        import re
        text = re.sub(r'#{1,6}\s*', '', text)                    # ### headers
        text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)    # **bold** *italic*
        text = re.sub(r'^-\s+', '', text, flags=re.MULTILINE)    # - list items
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE) # 1. numbered
        text = re.sub(r'`([^`]+)`', r'\1', text)                 # `code`
        # Remove title-like first line (no punctuation, followed by blank line)
        lines = text.strip().split('\n')
        if len(lines) >= 2 and lines[1].strip() == '':
            first = lines[0].strip()
            if first and first[-1] not in '.,;:!?' and len(first) < 80:
                lines = lines[2:]
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def submit_recording(self, user_instruction: str = ""):
        """Submit pending audio for transcription, or chat-only if no audio."""
        wav = self._pending_wav
        self._pending_wav = None

        if user_instruction:
            self._chat_history.append({"event": "user_instruction", "data": {"text": user_instruction}})

        # No audio: chat-only mode
        if not wav:
            if not user_instruction and not self._transcript:
                self._emit("recording_done", {"had_audio": False})
                return
            self._emit("chat_thinking", {})
            effective_instruction = user_instruction or "Analise a conversa e dê sua opinião em poucas frases."
            log.info(f"[Chat] Pure chat: '{effective_instruction[:80]}'")

            RESPONSE_MODES = {
                "short": {"max_tok": 150, "hint": "Seja breve.", "fmt": "\nSem markdown, sem títulos."},
                "full": {"max_tok": 300, "hint": "", "fmt": "\nSem markdown, sem títulos."},
                "research": {"max_tok": 600, "hint": "", "fmt": "\nSem markdown. Parágrafos curtos."},
            }

            def chat_only():
                try:
                    context = self._build_full_context()
                    participants = self._participants_context
                    system = self._raw_system_prompt or "Você é um copiloto de reuniões."
                    mode = RESPONSE_MODES.get(self._response_mode, RESPONSE_MODES["short"])
                    max_tok = mode["max_tok"]
                    hint = mode["hint"] if not user_instruction else ""
                    copilot_fmt = mode["fmt"]
                    no_repeat = "\nNão repita informações que o Copiloto já respondeu no contexto." if "[Copiloto respondeu]" in context else ""
                    user_msg = f"{participants}\n\nContexto da conversa:\n{context}\n\nInstrução: {effective_instruction}\n{hint}{copilot_fmt}{no_repeat}"
                    log.info(f"[Chat] mode={self._response_mode} max_tok={max_tok} context={len(context)} chars")
                    result = self._bedrock.call_raw(system, user_msg, max_tokens=max_tok)
                    result = self._clean_md(result)
                    # Trim at last complete sentence to avoid mid-sentence cutoff
                    result = self._trim_to_sentence(result)
                    log.info(f"[Chat] Response ({len(result)} chars): {result[:150]}")
                    self._emit("copilot_response", {"response": result, "had_instruction": bool(user_instruction)})
                except Exception as e:
                    log.error(f"[Chat] Error: {e}", exc_info=True)
                    self._emit("copilot_response", {"response": f"Erro: {e}", "had_instruction": bool(user_instruction)})
            threading.Thread(target=chat_only, daemon=True).start()
            return

        # Has pending WAV from manual stop — should not happen in new flow
        log.info(f"[Submit] Unexpected wav, processing...")
        self._emit("submit_started", {})
        self._pending_instruction = user_instruction
        threading.Thread(target=self._process_monitor_chunk, args=(wav,), daemon=True).start()

    def _on_mic_chunk(self, wav_bytes: bytes, source: str):
        """Process mic chunk."""
        threading.Thread(target=self._process_auto_chunk, args=(wav_bytes,), daemon=True).start()

    def _process_mic_chunk(self, wav_bytes: bytes):
        try:
            text = self._groq.transcribe(wav_bytes).strip()
            if not text:
                return
            self._emit_transcript(self._my_label, text)
        except GroqError as e:
            self._emit("error", {"code": "groq_error", "message": str(e)})
        except Exception as e:
            log.error(f"Mic chunk error: {e}")

    def _on_monitor_chunk(self, wav_bytes: bytes, source: str):
        """Process monitor chunk."""
        threading.Thread(target=self._process_auto_chunk, args=(wav_bytes,), daemon=True).start()

    def _process_auto_chunk(self, wav_bytes: bytes):
        """Auto mode: Groq transcribes + Bedrock identifies speakers only (no response)."""
        import time as _time
        t0 = _time.time()
        try:
            t1 = _time.time()
            log.info("[AUTO] Enviando áudio pro Groq...")
            segments = self._groq.transcribe_verbose(wav_bytes)
            if not segments:
                return
            transcript_text = "\n".join(s.text.strip() for s in segments if s.text.strip())
            if not transcript_text:
                return
            groq_time = _time.time() - t1
            log.info(f"[AUTO] Groq OK: {len(transcript_text)} chars em {groq_time:.2f}s")

            # Bedrock: identify speakers only
            earlier_ctx = "\n".join(f"[{e['speaker']}] {e['text'][:80]}" for e in self._transcript[-20:])
            participants_str = self._participants_context or "Participantes não informados. Deduza pelos conteúdos."
            earlier_block = f"\nContexto anterior:\n{earlier_ctx}\n" if earlier_ctx else ""

            system = ("Você identifica quem fala em reuniões. "
                      "Se alguém é chamado pelo nome na conversa, use esse nome como speaker. "
                      "Se não souber o nome, use Pessoa 1, Pessoa 2, etc mantendo consistência. "
                      "Responda SOMENTE JSON puro: {\"transcript\": [{\"speaker\": \"Nome\", \"text\": \"fala\"}]}")
            user_msg = (
                f"{participants_str}{earlier_block}\n"
                "Inclua TODAS as falas. Agrupe falas consecutivas do mesmo speaker.\n"
                f"Transcrição:\n{transcript_text}"
            )

            t2 = _time.time()
            log.info(f"[AUTO] Enviando pro Bedrock ({len(user_msg)} chars)...")
            result_text = self._bedrock.call_raw(system, user_msg, max_tokens=2048)
            bedrock_time = _time.time() - t2
            log.info(f"[AUTO] Bedrock OK em {bedrock_time:.2f}s")

            # Parse transcript entries
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
                            entries = parsed.get("transcript", [])
                            for item in entries:
                                sp = item.get("speaker", "OUTROS")
                                txt = item.get("text", "").strip()
                                if txt:
                                    self._emit_transcript(sp, txt)
                            log.info(f"[AUTO] {len(entries)} entradas | Groq={groq_time:.2f}s Bedrock={bedrock_time:.2f}s Total={_time.time()-t0:.2f}s")
                            return
                        except json.JSONDecodeError:
                            start = None

            # Fallback
            for line in transcript_text.split("\n"):
                line = line.strip()
                if line:
                    self._emit_transcript("CONVERSA", line)
            log.info(f"[AUTO] Fallback | Groq={groq_time:.2f}s Bedrock={bedrock_time:.2f}s Total={_time.time()-t0:.2f}s")

        except Exception as e:
            log.error(f"[AUTO] Error: {e}", exc_info=True)

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
        """Process transcribed text: Bedrock attributes speakers + generates response."""
        import time
        start_time = time.time()

        earlier_ctx = "\n".join(f"[{e['speaker']}] {e['text'][:80]}" for e in self._transcript[-20:])
        user_instruction = getattr(self, '_pending_instruction', '') or ''
        self._pending_instruction = ''

        try:
            participants_str = self._participants_context or "Participantes não informados. Deduza pelos conteúdos."
            earlier_block = f"\nContexto anterior:\n{earlier_ctx}\n" if earlier_ctx else ""

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
            )

            # Build format instruction based on whether user gave instruction
            if user_instruction:
                format_instruction = (
                    'Formato JSON obrigatório: {"transcript": [{"speaker": "Nome", "text": "fala"}], "response": "sua resposta aqui"}\n'
                )
                user_instruction_block = (
                    f"\n\n=== INSTRUÇÃO DO USUÁRIO (OBRIGATÓRIO RESPONDER) ===\n"
                    f"{user_instruction}\n"
                    f"=== FIM DA INSTRUÇÃO ===\n"
                    f'Você DEVE responder à instrução acima no campo "response" do JSON. '
                    f"A resposta deve ser completa e útil. NÃO retorne response vazio."
                )
            else:
                format_instruction = (
                    'Formato JSON obrigatório: {"transcript": [{"speaker": "Nome", "text": "fala"}], "response": "sua resposta aqui"}\n'
                    'O campo "response": responda perguntas feitas na conversa, dê sugestões ou observações úteis.\n'
                    'Se alguém fez uma pergunta, RESPONDA a pergunta.\n'
                    'Só retorne response vazio "" se realmente não tiver nada útil a dizer.'
                )
                user_instruction_block = ""

            system = self._custom_system_prompt or ""
            system += (
                "\nVocê é um copiloto de reuniões. Atribui falas aos participantes e responde ao usuário. "
                "Responda SOMENTE JSON puro sem markdown, sem explicações."
            )

            user_msg = (
                f"{participants_str}{earlier_block}\n"
                f"[INSTRUÇÃO] Direcionado para: {self._suggestions_target}\n"
                f"{speaker_instruction}\n{format_instruction}\n"
                f"Transcrição do trecho atual:\n{transcript_text}"
                f"{user_instruction_block}"
            )

            log.info(f"[STEP 2] === BEDROCK REQUEST ===")
            log.info(f"[STEP 2] System prompt ({len(system)} chars): {system[:200]}")
            log.info(f"[STEP 2] User instruction: '{user_instruction}'")
            log.info(f"[STEP 2] Instruction position: AFTER transcription")
            log.info(f"[STEP 2] User msg ({len(user_msg)} chars):")
            for line in user_msg.split('\n')[:30]:
                if line.strip():
                    log.info(f"[STEP 2]   | {line[:150]}")
            log.info(f"[STEP 2] Enviando pro Bedrock...")

            t2 = time.time()
            result_text = self._bedrock.call_raw(system, user_msg, max_tokens=4096)

            log.info(f"[STEP 2] Bedrock respondeu em {time.time() - t2:.2f}s")
            log.info(f"[STEP 2] Resposta ({len(result_text)} chars): {repr(result_text[:300])}")

            # Parse JSON
            transcript_entries = []
            response_text = ""
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
                            response_text = parsed.get("response", "")
                            # Backwards compat: also check "suggestions"
                            if not response_text and "suggestions" in parsed:
                                sug = parsed["suggestions"]
                                if isinstance(sug, list) and sug:
                                    response_text = "\n".join(f"→ {s}" for s in sug)
                            break
                        except json.JSONDecodeError:
                            start = None

            # Emit transcript
            if transcript_entries:
                for item in transcript_entries:
                    sp = item.get("speaker", "OUTROS")
                    txt = item.get("text", "").strip()
                    if txt:
                        self._emit_transcript(sp, txt)
                log.info(f"[STEP 3] {len(transcript_entries)} entradas com speakers")
            else:
                for line in transcript_text.split("\n"):
                    line = line.strip()
                    if line:
                        self._emit_transcript("CONVERSA", line)

            # Emit response (unified)
            # Ensure response_text is a string
            if isinstance(response_text, dict):
                # Bedrock returned object instead of string — extract text
                if "suggestions" in response_text:
                    sug = response_text["suggestions"]
                    response_text = "\n".join(sug) if isinstance(sug, list) else str(sug)
                else:
                    response_text = json.dumps(response_text, ensure_ascii=False)
            response_text = str(response_text)
            log.info(f"[STEP 4] Raw response_text: {repr(response_text[:200])}")
            clean_response = response_text.strip().strip('{}').strip()
            if clean_response:
                log.info(f"[STEP 4] Response: {len(response_text)} chars")
                self._suggestions.append(response_text)
                self._emit("copilot_response", {"response": response_text, "had_instruction": bool(user_instruction)})
            else:
                log.info("[STEP 4] Sem resposta")
                self._emit("copilot_response", {"response": "", "had_instruction": bool(user_instruction)})

            log.info(f"[DONE] Chunk processado em {time.time() - start_time:.2f}s total")

        except Exception as e:
            log.error(f"[ERRO] Process text: {e}", exc_info=True)
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
        return custom_prompt

    def _build_context(self) -> str:
        start = max(0, len(self._transcript) - MAX_CONTEXT_LINES)
        return "\n".join(
            f"[{e['speaker']}] {e['text']}" for e in self._transcript[start:]
        )

    def _build_full_context(self) -> str:
        """Build context including transcripts, user instructions and copilot responses."""
        lines = []
        for entry in self._chat_history[-50:]:
            ev = entry["event"]
            d = entry["data"]
            if ev == "transcript":
                lines.append(f"[{d['speaker']}] {d['text']}")
            elif ev == "user_instruction":
                lines.append(f"[Usuário perguntou] {d['text']}")
            elif ev == "copilot_response" and d.get("response"):
                lines.append(f"[Copiloto respondeu] {d['response'][:300]}")
        return "\n".join(lines)

    def stop_meeting(self) -> dict:
        self.unregister_global_hotkey()
        if self._chat_window:
            try:
                self._chat_window.destroy()
            except Exception:
                pass
            self._chat_window = None
        if self._mic_capture:
            self._mic_capture.stop()
            self._mic_capture = None
        if self._monitor_capture:
            self._monitor_capture.stop()
            self._monitor_capture = None

        transcript = list(self._transcript)
        suggestions = list(self._suggestions)

        self._voice_bank = VoiceBank(0.30)
        self._start_time = None

        return {"transcript": transcript, "suggestions": suggestions, "summary": ""}

    def generate_final_report(self, user_instruction: str = "") -> str:
        """Generate a final MD report based on user instruction."""
        context = self._build_full_context()
        system = self._raw_system_prompt or "Você é um copiloto de reuniões."
        instruction = user_instruction or "Gere um resumo completo da reunião."
        user_msg = f"Contexto completo da reunião:\n{context}\n\nInstrução: {instruction}\nGere um relatório em formato Markdown bem estruturado."

        log.info(f"[Report] Generating with instruction: {instruction[:80]}")
        try:
            result = self._bedrock.call_raw(system, user_msg, max_tokens=4096)
            log.info(f"[Report] Done: {len(result)} chars")
            return result
        except Exception as e:
            log.error(f"[Report] Error: {e}")
            return f"Erro ao gerar relatório: {e}"

        return {"transcript": transcript, "suggestions": suggestions, "summary": summary}

    def generate_summary(self, transcript_text: str, suggestions: list[str]) -> str:
        if not self._bedrock:
            return "Bedrock não disponível."
        return self._bedrock.generate_summary(transcript_text, suggestions)
