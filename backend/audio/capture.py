"""Audio capture — mic and monitor, Linux version.

Uses parec/pw-cat for PulseAudio/PipeWire monitors,
sounddevice for regular input devices.
"""
import sys
import subprocess
import threading
import time
import logging
from typing import Callable

import numpy as np

from .wav import pcm_to_wav

SAMPLE_RATE = 16000
RMS_INTERVAL_SAMPLES = SAMPLE_RATE // 10  # 100ms
SILENCE_THRESHOLD = 0.005
SILENCE_TIMEOUT = 30  # seconds

log = logging.getLogger("whisper-copilot")


class AudioCapture:
    def __init__(self, device_id: str, source_type: str, chunk_seconds: int,
                 on_chunk: Callable[[bytes, str], None],
                 on_level: Callable[[str, float], None] | None = None,
                 on_status: Callable[[str, str], None] | None = None,
                 manual_mode: bool = False):
        self.device_id = device_id
        self.source_type = source_type
        self.chunk_samples = SAMPLE_RATE * chunk_seconds if not manual_mode else float('inf')
        self.manual_mode = manual_mode
        self.on_chunk = on_chunk
        self.on_level = on_level
        self.on_status = on_status
        self._running = threading.Event()
        self._thread: threading.Thread | None = None
        self._pcm_buf: list[int] = []
        self._buf_lock = threading.Lock()

    def start(self):
        self._running.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=5)

    def flush(self):
        """Manual mode: send accumulated buffer now."""
        with self._buf_lock:
            if len(self._pcm_buf) < SAMPLE_RATE:  # need at least 1s
                return
            chunk = np.array(self._pcm_buf, dtype=np.int16)
            self._pcm_buf.clear()
        
        chunk_rms = float(np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2)))
        if chunk_rms < SILENCE_THRESHOLD:
            return
        
        wav_bytes = pcm_to_wav(chunk, SAMPLE_RATE)
        self.on_chunk(wav_bytes, self.source_type)

    def _run(self):
        # Linux: use parec/pw-cat for PulseAudio/PipeWire devices
        if self.device_id.startswith("alsa_") or ".monitor" in self.device_id or self.source_type == "monitor":
            log.info(f"[Capture] Using parec/pw-cat for {self.device_id}")
            self._capture_parec()
        else:
            log.info(f"[Capture] Using sounddevice for {self.device_id}")
            self._capture_sounddevice()

    def _emit_level(self, rms_samples: list[float]) -> float:
        if not rms_samples:
            return 0.0
        arr = np.array(rms_samples)
        rms = float(np.sqrt(np.mean(arr ** 2)))
        if self.on_level:
            self.on_level(self.source_type, rms)
        return rms

    def _process_buffer(self, pcm_buf: list[int], rms_buf: list[float],
                        silence_tracker: dict):
        if len(rms_buf) >= RMS_INTERVAL_SAMPLES:
            rms = self._emit_level(rms_buf[:RMS_INTERVAL_SAMPLES])
            del rms_buf[:RMS_INTERVAL_SAMPLES]

            if rms >= SILENCE_THRESHOLD:
                silence_tracker["last_signal"] = time.time()
                silence_tracker["notified"] = False
            elif (time.time() - silence_tracker["last_signal"] > SILENCE_TIMEOUT
                  and not silence_tracker["notified"]):
                silence_tracker["notified"] = True
                log.warning(f"{self.source_type} silent for {SILENCE_TIMEOUT}s")
                if self.on_status:
                    self.on_status(self.source_type, "silent")

        # In manual mode, just accumulate — flush() sends it
        if self.manual_mode:
            with self._buf_lock:
                self._pcm_buf.extend(pcm_buf)
            pcm_buf.clear()
            return

        if len(pcm_buf) >= self.chunk_samples:
            chunk = np.array(pcm_buf[:self.chunk_samples], dtype=np.int16)
            del pcm_buf[:self.chunk_samples]

            # Skip silent chunks
            chunk_rms = float(np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2)))
            if chunk_rms < SILENCE_THRESHOLD:
                return

            wav_bytes = pcm_to_wav(chunk, SAMPLE_RATE)
            self.on_chunk(wav_bytes, self.source_type)

    def _capture_parec(self):
        """Capture from PulseAudio/PipeWire device using parec or pw-cat."""
        is_monitor = ".monitor" in self.device_id
        source = self.device_id

        # If it's a monitor source type but doesn't have .monitor suffix, add it
        if not is_monitor and self.source_type == "monitor" and not source.startswith("alsa_input."):
            source = f"{self.device_id}.monitor"
            is_monitor = True

        if is_monitor:
            cmd = ["parec", f"--device={source}", "--format=s16le", "--channels=1",
                   f"--rate={SAMPLE_RATE}", "--latency-msec=1"]
        else:
            cmd = ["pw-cat", "--record", f"--target={source}", "--format=s16",
                   "--channels=1", f"--rate={SAMPLE_RATE}", "-"]

        log.info(f"[Capture] Command: {' '.join(cmd)}")

        while self._running.is_set():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                log.error(f"[Capture] Command not found: {cmd[0]}")
                if self.on_status:
                    self.on_status(self.source_type, "error")
                time.sleep(1)
                continue

            pcm_buf: list[int] = []
            rms_buf: list[float] = []
            silence = {"last_signal": time.time(), "notified": False}

            try:
                while self._running.is_set():
                    data = proc.stdout.read(3200)  # 100ms at 16kHz mono 16bit
                    if not data:
                        break
                    samples = np.frombuffer(data[:len(data) - len(data) % 2], dtype=np.int16)
                    pcm_buf.extend(samples.tolist())
                    rms_buf.extend((samples.astype(np.float32) / 32768.0).tolist())
                    self._process_buffer(pcm_buf, rms_buf, silence)
            finally:
                proc.kill()
                proc.wait()

            if not self._running.is_set():
                break
            time.sleep(0.5)

    def _capture_sounddevice(self):
        """Capture from sounddevice (regular input devices)."""
        import sounddevice as sd

        dev_id = self.device_id
        dev_idx = int(dev_id) if dev_id.isdigit() else dev_id
        pcm_buf: list[int] = []
        rms_buf: list[float] = []
        silence = {"last_signal": time.time(), "notified": False}
        lock = threading.Lock()

        def callback(indata, frames, time_info, status):
            with lock:
                samples_i16 = (np.clip(indata[:, 0], -1.0, 1.0) * 32767).astype(np.int16)
                pcm_buf.extend(samples_i16.tolist())
                rms_buf.extend(indata[:, 0].tolist())

        try:
            with sd.InputStream(device=dev_idx, channels=1, samplerate=SAMPLE_RATE,
                                blocksize=1600, callback=callback):
                while self._running.is_set():
                    time.sleep(0.05)
                    with lock:
                        self._process_buffer(pcm_buf, rms_buf, silence)
        except Exception as e:
            log.error(f"[Capture] sounddevice error: {e}")
            if self.on_status:
                self.on_status(self.source_type, "error")
