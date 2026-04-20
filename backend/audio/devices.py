"""Audio device listing and testing — cross-platform."""
import sys
import subprocess
import threading
import time
from typing import Callable

import numpy as np


def list_audio_devices() -> list[dict]:
    if sys.platform != "win32":
        devices = _list_linux()
        if devices:
            return devices
    return _list_windows()


def _list_linux() -> list[dict]:
    """List devices via pactl (PulseAudio/PipeWire)."""
    devices = []
    try:
        output = subprocess.check_output(
            ["pactl", "list", "sources", "short"], text=True
        )
        default_source = subprocess.check_output(
            ["pactl", "get-default-source"], text=True
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return _list_sounddevice()

    for line in output.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        pulse_name = parts[1]
        is_monitor = pulse_name.endswith(".monitor")
        device_type = "monitor" if is_monitor else "input"
        is_default = pulse_name == default_source

        raw = (pulse_name.replace("alsa_input.", "").replace("alsa_output.", "")
               .replace(".monitor", "").replace(".analog-stereo", "")
               .replace(".mono-fallback", ""))

        if is_monitor:
            name = f"🔊 {raw.replace('-', ' ').replace('_', ' ')} (Monitor)"
        else:
            name = f"🎙️ {raw.replace('-', ' ').replace('_', ' ')}"

        devices.append({
            "id": pulse_name,
            "name": name,
            "deviceType": device_type,
            "isDefault": is_default,
        })
    return devices


def _list_sounddevice() -> list[dict]:
    """Fallback: list via sounddevice."""
    import sounddevice as sd
    devices = []
    all_devs = sd.query_devices()
    default_in = sd.default.device[0]

    for i, d in enumerate(all_devs):
        if d["max_input_channels"] > 0:
            devices.append({
                "id": str(i),
                "name": f"🎙️ {d['name']}",
                "deviceType": "input",
                "isDefault": i == default_in,
                "recommended": i == default_in,
            })
    return devices


def _list_windows() -> list[dict]:
    """List devices via sounddevice + PyAudioWPatch loopback."""
    import sounddevice as sd
    devices = []
    all_devs = sd.query_devices()
    default_in = sd.default.device[0]

    for i, d in enumerate(all_devs):
        if d["max_input_channels"] > 0:
            name_lower = d["name"].lower()
            if any(kw in name_lower for kw in ["stereo mix", "mixagem", "wave out"]):
                continue
            devices.append({
                "id": str(i),
                "name": f"🎙️ {d['name']}",
                "deviceType": "input",
                "isDefault": i == default_in,
                "recommended": i == default_in,
            })

    try:
        import pyaudiowpatch as pyaudio
        p = pyaudio.PyAudio()
        try:
            default_loopback_idx = p.get_default_wasapi_loopback()["index"]
        except Exception:
            default_loopback_idx = -1
        for i in range(p.get_device_count()):
            try:
                dev = p.get_device_info_by_index(i)
                if dev.get("isLoopbackDevice", False):
                    devices.append({
                        "id": f"wasapi:{i}",
                        "name": f"🔊 {dev['name']}",
                        "deviceType": "monitor",
                        "isDefault": i == default_loopback_idx,
                        "recommended": i == default_loopback_idx,
                    })
            except Exception:
                pass
        p.terminate()
    except ImportError:
        pass

    return devices


def test_device(device_id: str, device_type: str, duration: int = 3,
                on_level: Callable[[float], None] | None = None) -> float:
    if device_id.startswith("wasapi:"):
        return _test_wasapi(device_id, duration, on_level)
    if sys.platform != "win32" and (device_id.startswith("alsa_") or ".monitor" in device_id):
        return _test_parec(device_id, duration, on_level)
    return _test_sounddevice(device_id, duration, on_level)


def _test_parec(device_id: str, duration: int, on_level) -> float:
    """Test Linux PulseAudio/PipeWire device."""
    source = device_id
    is_monitor = ".monitor" in source
    cmd = (["parec", f"--device={source}", "--format=s16le", "--channels=1",
            "--rate=16000", "--latency-msec=1"] if is_monitor
           else ["pw-cat", "--record", f"--target={source}", "--format=s16",
                 "--channels=1", "--rate=16000", "-"])
    peak = 0.0
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        start = time.time()
        while time.time() - start < duration:
            data = proc.stdout.read(3200)
            if not data:
                break
            samples = np.frombuffer(data[:len(data) - len(data) % 2], dtype=np.int16)
            rms = float(np.sqrt(np.mean((samples.astype(np.float32) / 32768.0) ** 2)))
            peak = max(peak, rms)
            if on_level:
                on_level(rms)
        proc.kill()
        proc.wait()
    except FileNotFoundError:
        pass
    return peak


def _test_sounddevice(device_id: str, duration: int, on_level) -> float:
    import sounddevice as sd
    dev_idx = int(device_id) if device_id.isdigit() else device_id
    peak = 0.0
    buf = []
    lock = threading.Lock()

    def callback(indata, frames, time_info, status):
        with lock:
            buf.extend(indata[:, 0].tolist())

    try:
        with sd.InputStream(device=dev_idx, channels=1, samplerate=16000,
                            blocksize=1600, callback=callback):
            start = time.time()
            while time.time() - start < duration:
                time.sleep(0.1)
                with lock:
                    if len(buf) >= 1600:
                        arr = np.array(buf[:1600])
                        rms = float(np.sqrt(np.mean(arr ** 2)))
                        peak = max(peak, rms)
                        if on_level:
                            on_level(rms)
                        del buf[:1600]
    except Exception:
        pass
    return peak


def _test_wasapi(device_id: str, duration: int, on_level) -> float:
    dev_idx = int(device_id.replace("wasapi:", ""))
    script = f"""
import sys, time, numpy as np
try:
    import pyaudiowpatch as pyaudio
    p = pyaudio.PyAudio()
    dev = p.get_device_info_by_index({dev_idx})
    rate = int(dev['defaultSampleRate'])
    stream = p.open(format=pyaudio.paInt16, channels=2, rate=rate,
                    input=True, input_device_index={dev_idx}, frames_per_buffer=rate//10)
    peak = 0.0
    start = time.time()
    while time.time() - start < {duration}:
        data = stream.read(rate//10, exception_on_overflow=False)
        samples = np.frombuffer(data, dtype=np.int16)[::2].astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(samples ** 2)))
        peak = max(peak, rms)
        print(rms, flush=True)
    stream.stop_stream(); stream.close(); p.terminate()
    print(f"PEAK:{{peak}}", flush=True)
except Exception as e:
    print(f"ERROR:{{e}}", file=sys.stderr, flush=True)
"""
    try:
        proc = subprocess.Popen([sys.executable, "-c", script],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        peak = 0.0
        for line in proc.stdout:
            line = line.strip()
            if line.startswith("PEAK:"):
                peak = float(line[5:])
            elif on_level:
                try:
                    on_level(float(line))
                except ValueError:
                    pass
        proc.wait(timeout=duration + 2)
        return peak
    except Exception:
        return 0.0
