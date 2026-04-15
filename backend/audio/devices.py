"""Audio device listing and testing — cross-platform."""
import sys
import subprocess
import threading
import time
from typing import Callable

import sounddevice as sd
import numpy as np


def list_audio_devices() -> list[dict]:
    """List available audio devices."""
    devices = []
    
    # Get sounddevice devices for inputs
    all_devs = sd.query_devices()
    default_in = sd.default.device[0]
    
    external_keywords = ["usb", "headset", "wireless", "bluetooth", "dell", "logitech"]
    
    input_devices = []
    
    for i, d in enumerate(all_devs):
        if d["max_input_channels"] > 0:
            name_lower = d["name"].lower()
            # Skip stereo mix - we'll use PyAudioWPatch loopback instead
            if any(kw in name_lower for kw in ["stereo mix", "mixagem", "wave out"]):
                continue
            
            is_external = any(kw in name_lower for kw in external_keywords)
            
            input_devices.append({
                "id": str(i),
                "name": f"🎙️ {d['name']}",
                "deviceType": "input",
                "isDefault": i == default_in,
                "isExternal": is_external,
                "recommended": False,
            })
    
    # Mark recommended input
    for dev in input_devices:
        if dev.get("isExternal"):
            dev["recommended"] = True
            break
    else:
        if input_devices:
            input_devices[0]["recommended"] = True
    
    devices.extend(input_devices)
    
    # Get PyAudioWPatch loopback devices
    try:
        import pyaudiowpatch as pyaudio
        p = pyaudio.PyAudio()
        
        loopback_devices = []
        for i in range(p.get_device_count()):
            try:
                dev = p.get_device_info_by_index(i)
                if dev.get("isLoopbackDevice", False):
                    loopback_devices.append({
                        "id": f"wasapi:{i}",
                        "name": f"🔊 {dev['name']}",
                        "deviceType": "monitor",
                        "isDefault": False,
                        "recommended": False,
                    })
            except:
                pass
        
        # Mark first loopback as recommended
        if loopback_devices:
            loopback_devices[0]["recommended"] = True
            devices.extend(loopback_devices)
        
        p.terminate()
    except:
        pass
    
    return devices


def test_device(device_id: str, device_type: str, duration: int = 3,
                on_level: Callable[[float], None] | None = None) -> float:
    """Test a device for `duration` seconds, return peak RMS level."""
    if device_id.startswith("wasapi:"):
        # Use PyAudioWPatch in subprocess
        return _test_wasapi_subprocess(device_id, duration, on_level)
    
    # Regular sounddevice
    return _test_sounddevice(device_id, duration, on_level)


def _test_wasapi_subprocess(device_id: str, duration: int, on_level) -> float:
    """Test WASAPI device in subprocess to avoid GIL issues."""
    dev_idx = int(device_id.replace("wasapi:", ""))
    
    script = f"""
import sys
import time
import numpy as np
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
    stream.stop_stream()
    stream.close()
    p.terminate()
    print(f"PEAK:{{peak}}", flush=True)
except Exception as e:
    print(f"ERROR:{{e}}", file=sys.stderr, flush=True)
"""
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        peak = 0.0
        for line in proc.stdout:
            line = line.strip()
            if line.startswith("PEAK:"):
                peak = float(line.replace("PEAK:", ""))
            elif line and not line.startswith("ERROR"):
                try:
                    level = float(line)
                    if on_level:
                        on_level(level)
                except:
                    pass
        
        proc.wait(timeout=duration + 2)
        return peak
    except:
        return 0.0


def _test_sounddevice(device_id: str, duration: int, on_level) -> float:
    """Test regular sounddevice."""
    dev_idx = int(device_id)
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
    except:
        pass
    return peak
