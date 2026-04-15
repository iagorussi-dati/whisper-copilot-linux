"""Audio device listing and testing — simplified for Windows."""
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
    all_devs = sd.query_devices()
    default_in = sd.default.device[0]
    
    # Keywords
    external_keywords = ["usb", "headset", "wireless", "bluetooth", "dell", "logitech"]
    stereo_mix_keywords = ["stereo mix", "mixagem", "wave out", "loopback"]
    
    input_devices = []
    monitor_devices = []
    
    for i, d in enumerate(all_devs):
        if d["max_input_channels"] > 0:
            name_lower = d["name"].lower()
            is_stereo_mix = any(kw in name_lower for kw in stereo_mix_keywords)
            
            if is_stereo_mix:
                monitor_devices.append({
                    "id": str(i),
                    "name": f"🔊 {d['name']} (Monitor)",
                    "deviceType": "monitor",
                    "isDefault": False,
                    "recommended": True,
                })
            else:
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
    devices.extend(monitor_devices)
    
    return devices


def test_device(device_id: str, device_type: str, duration: int = 3,
                on_level: Callable[[float], None] | None = None) -> float:
    """Test a device for `duration` seconds, return peak RMS level."""
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
    except Exception as e:
        print(f"Error testing device: {e}")
    return peak
