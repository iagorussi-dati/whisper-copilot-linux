"""Voice Activity Detection using Silero VAD — detects utterance boundaries."""
import logging
import threading
import numpy as np

log = logging.getLogger("whisper-copilot")

class VoiceActivityDetector:
    """Detects speech start/end in real-time audio stream using Silero VAD."""

    def __init__(self, sample_rate: int = 16000, silence_threshold_ms: int = 1500,
                 speech_threshold: float = 0.5, max_utterance_s: int = 30):
        self._rate = sample_rate
        self._silence_ms = silence_threshold_ms
        self._speech_thresh = speech_threshold
        self._max_samples = max_utterance_s * sample_rate
        self._model = None
        self._lock = threading.Lock()

        # State
        self._is_speaking = False
        self._speech_buffer = []  # PCM int16 chunks during speech
        self._silence_frames = 0
        self._chunk_size = 512  # Silero VAD expects 512 samples at 16kHz (32ms)
        self._frames_for_silence = int(silence_threshold_ms / (self._chunk_size / sample_rate * 1000))
        self._total_speech_samples = 0
        self._leftover = b""  # leftover bytes from previous feed

    def _ensure_model(self):
        if self._model is None:
            try:
                from silero_vad import load_silero_vad
                self._model = load_silero_vad()
                log.info("[VAD] Silero VAD loaded")
            except ImportError:
                log.error("[VAD] silero-vad not installed. pip install silero-vad")
                raise

    def feed(self, pcm_bytes: bytes) -> list[bytes]:
        """Feed raw PCM int16 mono 16kHz bytes. Returns list of complete utterances (WAV-ready PCM bytes)."""
        self._ensure_model()
        import torch

        utterances = []
        data = self._leftover + pcm_bytes
        self._leftover = b""
        chunk_bytes = self._chunk_size * 2  # int16 = 2 bytes per sample

        offset = 0
        while offset + chunk_bytes <= len(data):
            chunk = data[offset:offset + chunk_bytes]
            offset += chunk_bytes

            # Run VAD
            samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
            tensor = torch.from_numpy(samples)
            with self._lock:
                prob = self._model(tensor, self._rate).item()

            if prob >= self._speech_thresh:
                # Speech detected
                if not self._is_speaking:
                    self._is_speaking = True
                    self._speech_buffer = []
                    self._total_speech_samples = 0
                    self._silence_frames = 0
                    log.debug("[VAD] Speech started")
                self._speech_buffer.append(chunk)
                self._total_speech_samples += self._chunk_size
                self._silence_frames = 0

                # Force flush if too long
                if self._total_speech_samples >= self._max_samples:
                    utt = b"".join(self._speech_buffer)
                    utterances.append(utt)
                    log.info(f"[VAD] Utterance (max {self._max_samples/self._rate:.0f}s): {len(utt)//2/self._rate:.1f}s")
                    self._speech_buffer = []
                    self._total_speech_samples = 0
            else:
                # Silence
                if self._is_speaking:
                    self._speech_buffer.append(chunk)  # include trailing silence
                    self._total_speech_samples += self._chunk_size
                    self._silence_frames += 1

                    if self._silence_frames >= self._frames_for_silence:
                        # End of utterance
                        utt = b"".join(self._speech_buffer)
                        dur = len(utt) // 2 / self._rate
                        if dur >= 0.8:  # min 0.8s
                            utterances.append(utt)
                            log.info(f"[VAD] Utterance complete: {dur:.1f}s")
                        else:
                            log.debug(f"[VAD] Utterance too short ({dur:.1f}s), discarding")
                        self._is_speaking = False
                        self._speech_buffer = []
                        self._total_speech_samples = 0
                        self._silence_frames = 0

        # Save leftover
        if offset < len(data):
            self._leftover = data[offset:]

        return utterances

    def flush(self) -> bytes | None:
        """Flush any remaining speech buffer. Call when recording stops."""
        if self._speech_buffer:
            utt = b"".join(self._speech_buffer)
            dur = len(utt) // 2 / self._rate
            self._speech_buffer = []
            self._is_speaking = False
            self._total_speech_samples = 0
            self._silence_frames = 0
            if dur >= 0.8:
                log.info(f"[VAD] Flush: {dur:.1f}s")
                return utt
        return None

    def reset(self):
        """Reset state."""
        self._is_speaking = False
        self._speech_buffer = []
        self._silence_frames = 0
        self._total_speech_samples = 0
        self._leftover = b""
        if self._model is not None:
            self._model.reset_states()
