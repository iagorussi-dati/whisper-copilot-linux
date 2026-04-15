"""WAV encoding utilities."""
import io
import struct
import wave

import numpy as np


def pcm_to_wav(samples: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert PCM int16 numpy array to WAV bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.astype(np.int16).tobytes())
    return buf.getvalue()


def wav_to_pcm(wav_bytes: bytes) -> np.ndarray:
    """Convert WAV bytes to PCM int16 numpy array."""
    buf = io.BytesIO(wav_bytes)
    with wave.open(buf, "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        return np.frombuffer(raw, dtype=np.int16)
