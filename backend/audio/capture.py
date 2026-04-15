"""Audio capture — mic and monitor, cross-platform.

Replicates the Rust AudioCapture logic: records in a background thread,
emits RMS levels, and fires a callback with WAV bytes every chunk_seconds.
"""
import sys
import subprocess
import threading
import time
from typing import Callable

import numpy as np

from .wav import pcm_to_wav

SAMPLE_RATE = 16000
RMS_INTERVAL_SAMPLES = SAMPLE_RATE // 10  # 100ms
SILENCE_THRESHOLD = 0.001
SILENCE_TIMEOUT = 30  # seconds


class AudioCapture:
    def __init__(self, device_id: str, source_type: str, chunk_seconds: int,
                 on_chunk: Callable[[bytes, str], None],
                 on_level: Callable[[str, float], None] | None = None,
                 on_status: Callable[[str, str], None] | None = None):
        self.device_id = device_id
        self.source_type = source_type
        self.chunk_samples = SAMPLE_RATE * chunk_seconds
        self.on_chunk = on_chunk
        self.on_level = on_level
        self.on_status = on_status
        self._running = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        self._running.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        # Check if it's a WASAPI device
        if self.device_id.startswith("wasapi:"):
            self._capture_wasapi_subprocess()
            return
        
        # Regular sounddevice
        self._capture_sounddevice()

    def _emit_level(self, rms_samples: list[float]):
        if not rms_samples:
            return 0.0
        arr = np.array(rms_samples)
        rms = float(np.sqrt(np.mean(arr ** 2)))
        if self.on_level:
            self.on_level(self.source_type, rms)
        return rms

    def _process_buffer(self, pcm_buf: list[int], rms_buf: list[float],
                        silence_tracker: dict):
        """Process accumulated samples: emit levels, fire chunk callback."""
        if len(rms_buf) >= RMS_INTERVAL_SAMPLES:
            rms = self._emit_level(rms_buf[:RMS_INTERVAL_SAMPLES])
            del rms_buf[:RMS_INTERVAL_SAMPLES]

            if rms >= SILENCE_THRESHOLD:
                silence_tracker["last_signal"] = time.time()
                silence_tracker["notified"] = False
            elif (time.time() - silence_tracker["last_signal"] > SILENCE_TIMEOUT
                  and not silence_tracker["notified"]):
                silence_tracker["notified"] = True
                if self.on_status:
                    self.on_status(self.source_type, "silent")

        if len(pcm_buf) >= self.chunk_samples:
            chunk = np.array(pcm_buf[:self.chunk_samples], dtype=np.int16)
            del pcm_buf[:self.chunk_samples]

            # Skip silent chunks
            chunk_rms = float(np.sqrt(np.mean((chunk.astype(np.float32) / 32768.0) ** 2)))
            if chunk_rms < SILENCE_THRESHOLD:
                return

            wav_bytes = pcm_to_wav(chunk, SAMPLE_RATE)
            self.on_chunk(wav_bytes, self.source_type)

    def _capture_wasapi_subprocess(self):
        """Capture WASAPI in subprocess to avoid GIL issues."""
        dev_idx = int(self.device_id.replace("wasapi:", ""))
        
        script = f"""
import sys
import numpy as np
import logging
logging.basicConfig(level=logging.ERROR)

try:
    import pyaudiowpatch as pyaudio
    p = pyaudio.PyAudio()
    dev = p.get_device_info_by_index({dev_idx})
    rate = int(dev['defaultSampleRate'])
    
    stream = p.open(
        format=pyaudio.paInt16,
        channels=2,
        rate=rate,
        input=True,
        input_device_index={dev_idx},
        frames_per_buffer=rate//10
    )
    
    while True:
        data = stream.read(rate//10, exception_on_overflow=False)
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        
except KeyboardInterrupt:
    pass
finally:
    try:
        stream.stop_stream()
        stream.close()
        p.terminate()
    except:
        pass
"""
        
        import logging
        log = logging.getLogger("whisper-copilot")
        
        while self._running.is_set():
            proc = None
            try:
                proc = subprocess.Popen(
                    [sys.executable, "-c", script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=0
                )
                
                pcm_buf = []
                rms_buf = []
                silence = {"last_signal": time.time(), "notified": False}
                
                log.info(f"WASAPI subprocess started for device {dev_idx}")
                
                # Read in chunks - 48kHz stereo, 100ms = 9600 bytes
                chunk_size = 9600
                chunks_received = 0
                
                while self._running.is_set():
                    try:
                        data = proc.stdout.read(chunk_size)
                        if not data or len(data) == 0:
                            log.warning("No data from subprocess")
                            break
                        
                        chunks_received += 1
                        if chunks_received % 50 == 0:  # Log every 5 seconds
                            log.info(f"Received {chunks_received} chunks from WASAPI")
                        
                        # Convert stereo to mono, resample 48kHz -> 16kHz
                        samples = np.frombuffer(data, dtype=np.int16)
                        if len(samples) == 0:
                            continue
                        
                        # Take left channel (every other sample)
                        samples_mono = samples[::2]
                        
                        # Simple decimation 48kHz -> 16kHz (take every 3rd sample)
                        samples_16k = samples_mono[::3]
                        
                        if len(samples_16k) > 0:
                            pcm_buf.extend(samples_16k.tolist())
                            rms_buf.extend((samples_16k.astype(np.float32) / 32768.0).tolist())
                            self._process_buffer(pcm_buf, rms_buf, silence)
                            
                    except Exception as e:
                        log.error(f"Error reading from subprocess: {e}")
                        break
                
                log.info(f"WASAPI subprocess ended, received {chunks_received} total chunks")
                
            except Exception as e:
                log.error(f"WASAPI subprocess error: {e}")
                if self.on_status:
                    self.on_status(self.source_type, "error")
            finally:
                if proc:
                    try:
                        proc.kill()
                        proc.wait(timeout=1)
                    except:
                        pass
            
            if not self._running.is_set():
                break
            time.sleep(0.5)

    def _capture_parec(self):
        """Capture from WASAPI device using subprocess to avoid GIL issues."""
        capture_script = f"""
import sys
import time
import numpy as np

try:
    import pyaudiowpatch as pyaudio
    
    p = pyaudio.PyAudio()
    dev_info = p.get_device_info_by_index({device_idx})
    is_loopback = dev_info.get("isLoopbackDevice", False)
    
    native_rate = int(dev_info['defaultSampleRate'])
    channels = 2 if is_loopback else 1
    frames_per_buffer = native_rate // 10
    
    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=native_rate,
        input=True,
        input_device_index={device_idx},
        frames_per_buffer=frames_per_buffer,
    )
    
    while True:
        try:
            data = stream.read(frames_per_buffer, exception_on_overflow=False)
            # Write raw audio data to stdout
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
        except KeyboardInterrupt:
            break
        except:
            pass
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
except Exception as e:
    print(f"ERROR:{{e}}", file=sys.stderr, flush=True)
    sys.exit(1)
"""
        
        while self._running.is_set():
            try:
                proc = subprocess.Popen(
                    [sys.executable, "-c", capture_script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    bufsize=0
                )
                
                pcm_buf: list[int] = []
                rms_buf: list[float] = []
                silence = {"last_signal": time.time(), "notified": False}
                
                # Get device info for resampling
                try:
                    import pyaudiowpatch as pyaudio
                    p = pyaudio.PyAudio()
                    dev_info = p.get_device_info_by_index(device_idx)
                    native_rate = int(dev_info['defaultSampleRate'])
                    is_loopback = dev_info.get("isLoopbackDevice", False)
                    channels = 2 if is_loopback else 1
                    p.terminate()
                except:
                    native_rate = 48000
                    channels = 2
                
                frames_per_buffer = native_rate // 10
                bytes_per_read = frames_per_buffer * channels * 2  # 2 bytes per sample (int16)
                
                while self._running.is_set():
                    try:
                        data = proc.stdout.read(bytes_per_read)
                        if not data:
                            break
                        
                        samples = np.frombuffer(data, dtype=np.int16)
                        
                        # Convert stereo to mono if needed
                        if channels == 2:
                            samples = samples[::2]
                        
                        # Resample to 16kHz if needed
                        if native_rate != SAMPLE_RATE:
                            ratio = SAMPLE_RATE / native_rate
                            new_length = int(len(samples) * ratio)
                            if new_length > 0:
                                indices = np.linspace(0, len(samples) - 1, new_length)
                                samples = np.interp(indices, np.arange(len(samples)), samples).astype(np.int16)
                        
                        pcm_buf.extend(samples.tolist())
                        rms_buf.extend((samples.astype(np.float32) / 32768.0).tolist())
                        self._process_buffer(pcm_buf, rms_buf, silence)
                        
                    except Exception:
                        break
                
                proc.kill()
                proc.wait()
                
            except Exception as e:
                if self.on_status:
                    self.on_status(self.source_type, "error")
            
            if not self._running.is_set():
                break
            time.sleep(0.5)

    def _capture_pyaudio_device(self, device_idx: int):
        """Capture from a PyAudio device (works for both input and loopback)."""
        try:
            import pyaudiowpatch as pyaudio
        except ImportError:
            if self.on_status:
                self.on_status(self.source_type, "error")
            return

        while self._running.is_set():
            p = None
            stream = None
            pcm_buf: list[int] = []
            rms_buf: list[float] = []
            silence = {"last_signal": time.time(), "notified": False}

            try:
                p = pyaudio.PyAudio()
                dev_info = p.get_device_info_by_index(device_idx)
                is_loopback = dev_info.get("isLoopbackDevice", False)
                
                # Use device's native sample rate, then resample to 16kHz
                native_rate = int(dev_info['defaultSampleRate'])
                channels = 2 if is_loopback else 1
                frames_per_buffer = native_rate // 10  # 100ms chunks
                
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=channels,
                    rate=native_rate,
                    input=True,
                    input_device_index=device_idx,
                    frames_per_buffer=frames_per_buffer,
                )

                while self._running.is_set():
                    try:
                        data = stream.read(frames_per_buffer, exception_on_overflow=False)
                        samples = np.frombuffer(data, dtype=np.int16)
                        
                        # Convert stereo to mono if needed
                        if channels == 2:
                            samples = samples[::2]  # Take left channel
                        
                        # Resample to 16kHz if needed
                        if native_rate != SAMPLE_RATE:
                            # Simple decimation/interpolation
                            ratio = SAMPLE_RATE / native_rate
                            new_length = int(len(samples) * ratio)
                            indices = np.linspace(0, len(samples) - 1, new_length)
                            samples = np.interp(indices, np.arange(len(samples)), samples).astype(np.int16)
                        
                        pcm_buf.extend(samples.tolist())
                        rms_buf.extend((samples.astype(np.float32) / 32768.0).tolist())
                        self._process_buffer(pcm_buf, rms_buf, silence)
                    except Exception:
                        pass

            except Exception as e:
                if self.on_status:
                    self.on_status(self.source_type, "error")
            finally:
                # Cleanup in correct order
                if stream is not None:
                    try:
                        stream.stop_stream()
                        stream.close()
                    except:
                        pass
                if p is not None:
                    try:
                        p.terminate()
                    except:
                        pass

            if not self._running.is_set():
                break
            time.sleep(0.5)

    def _capture_parec(self):
        is_monitor = ".monitor" in self.device_id
        source = self.device_id
        if not is_monitor and not source.startswith("alsa_input."):
            source = f"{self.device_id}.monitor"
            is_monitor = True

        cmd = (["parec", f"--device={source}", "--format=s16le", "--channels=1",
                f"--rate={SAMPLE_RATE}", "--latency-msec=1"] if is_monitor
               else ["pw-cat", "--record", f"--target={source}", "--format=s16",
                     "--channels=1", f"--rate={SAMPLE_RATE}", "-"])

        while self._running.is_set():
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                time.sleep(1)
                continue

            pcm_buf: list[int] = []
            rms_buf: list[float] = []
            silence = {"last_signal": time.time(), "notified": False}

            try:
                while self._running.is_set():
                    data = proc.stdout.read(3200)
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
            if self.on_status:
                self.on_status(self.source_type, "error")

    def _capture_wasapi_loopback(self, device_idx: int):
        """Windows WASAPI loopback capture via PyAudioWPatch."""
        try:
            import pyaudiowpatch as pyaudio
        except ImportError:
            if self.on_status:
                self.on_status(self.source_type, "error")
            return

        p = pyaudio.PyAudio()
        pcm_buf: list[int] = []
        rms_buf: list[float] = []
        silence = {"last_signal": time.time(), "notified": False}

        try:
            # Get the default WASAPI loopback device
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(device_idx)
            
            # Check if device supports loopback
            if not default_speakers.get("isLoopbackDevice", False):
                # Try to find the loopback version of this device
                loopback_dev = None
                for i in range(p.get_device_count()):
                    dev = p.get_device_info_by_index(i)
                    if (dev.get("isLoopbackDevice", False) and 
                        dev.get("name", "").lower() in default_speakers.get("name", "").lower()):
                        loopback_dev = dev
                        break
                
                if not loopback_dev:
                    # Use the first available loopback device
                    for i in range(p.get_device_count()):
                        dev = p.get_device_info_by_index(i)
                        if dev.get("isLoopbackDevice", False):
                            loopback_dev = dev
                            break
                
                if not loopback_dev:
                    if self.on_status:
                        self.on_status(self.source_type, "error")
                    return
                
                default_speakers = loopback_dev

            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=default_speakers["index"],
                frames_per_buffer=1600,
            )

            while self._running.is_set():
                try:
                    data = stream.read(1600, exception_on_overflow=False)
                    samples = np.frombuffer(data, dtype=np.int16)
                    pcm_buf.extend(samples.tolist())
                    rms_buf.extend((samples.astype(np.float32) / 32768.0).tolist())
                    self._process_buffer(pcm_buf, rms_buf, silence)
                except Exception as e:
                    # Ignore overflow errors
                    pass

            stream.stop_stream()
            stream.close()
        except Exception as e:
            if self.on_status:
                self.on_status(self.source_type, "error")
        finally:
            p.terminate()
