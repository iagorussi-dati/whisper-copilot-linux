"""Groq Whisper API client — replicates the Rust GroqClient."""
import time
import threading
from dataclasses import dataclass

import httpx

BASE_URL = "https://api.groq.com/openai/v1"


@dataclass
class GroqSegment:
    start: float
    end: float
    text: str


class GroqError(Exception):
    pass


class GroqClient:
    def __init__(self, api_key: str, model: str = "whisper-large-v3-turbo",
                 language: str = "pt"):
        self.api_key = api_key
        self.model = model
        self.language = language
        self._http = httpx.Client(timeout=30)
        self._wait_until: float | None = None
        self._lock = threading.Lock()

    def _wait_for_rate_limit(self):
        with self._lock:
            if self._wait_until and time.time() < self._wait_until:
                wait = self._wait_until - time.time()
                time.sleep(max(0, wait))

    def _update_rate_limit(self, response: httpx.Response):
        remaining = response.headers.get("x-ratelimit-remaining-requests")
        reset = response.headers.get("x-ratelimit-reset-requests")
        with self._lock:
            if remaining == "0" and reset:
                secs = _parse_duration(reset) or 3.0
                self._wait_until = time.time() + secs
            else:
                self._wait_until = None

    def validate(self) -> bool:
        resp = self._http.get(f"{BASE_URL}/models",
                              headers={"Authorization": f"Bearer {self.api_key}"})
        return resp.status_code == 200

    def transcribe(self, wav_bytes: bytes) -> str:
        """Simple transcription — returns text string."""
        self._wait_for_rate_limit()
        resp = self._http.post(
            f"{BASE_URL}/audio/transcriptions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            data={"model": self.model, "language": self.language,
                  "response_format": "text"},
        )
        self._update_rate_limit(resp)
        if resp.status_code == 401:
            raise GroqError("API key do Groq inválida")
        if resp.status_code == 429:
            raise GroqError(f"Rate limit atingido")
        if resp.status_code >= 500:
            raise GroqError(f"Erro do servidor Groq: HTTP {resp.status_code}")
        resp.raise_for_status()
        return resp.text.strip()

    def transcribe_verbose(self, wav_bytes: bytes) -> list[GroqSegment]:
        """Verbose transcription — returns segments with timestamps."""
        self._wait_for_rate_limit()
        resp = self._http.post(
            f"{BASE_URL}/audio/transcriptions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            data={"model": self.model, "language": self.language,
                  "response_format": "verbose_json",
                  "timestamp_granularities[]": "segment"},
        )
        self._update_rate_limit(resp)
        if not resp.is_success:
            raise GroqError(f"HTTP {resp.status_code}")
        data = resp.json()
        return [GroqSegment(s["start"], s["end"], s["text"])
                for s in data.get("segments", [])]


def _parse_duration(s: str) -> float | None:
    s = s.strip()
    if s.endswith("s"):
        rest = s[:-1]
        if "m" in rest:
            parts = rest.split("m")
            try:
                return float(parts[0]) * 60 + float(parts[1] or 0)
            except ValueError:
                return None
        try:
            return float(rest)
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None
