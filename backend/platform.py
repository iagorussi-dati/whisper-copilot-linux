"""Platform detection and OS-specific utilities."""
import os
import sys
import shutil
import subprocess
import logging
import threading

log = logging.getLogger("whisper-copilot")

_platform = None


def detect_platform() -> dict:
    """Detect the current platform and available tools."""
    info = {
        "os": sys.platform,  # linux, win32, darwin
        "windows": sys.platform == "win32",
        "linux": sys.platform == "linux",
        "wsl": False,
        "hyprland": False,
        "has_hyprctl": False,
        "has_keyboard_lib": False,
    }

    if info["linux"]:
        try:
            with open("/proc/version", "r") as f:
                version = f.read().lower()
                info["wsl"] = "microsoft" in version or "wsl" in version
        except Exception:
            pass
        info["hyprland"] = bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"))
        info["has_hyprctl"] = shutil.which("hyprctl") is not None

    try:
        import keyboard
        info["has_keyboard_lib"] = True
    except ImportError:
        pass

    return info


def get_platform() -> dict:
    global _platform
    if _platform is None:
        _platform = detect_platform()
        log.info(f"[Platform] {_platform}")
    return _platform


# ── Global Hotkeys ──

_hotkey_ids = []


def register_global_hotkey(key: str, callback, snapshot_key: str = "", snapshot_callback=None,
                          fullcontext_key: str = "", fullcontext_callback=None):
    """Register global hotkeys. Returns True if successful."""
    unregister_global_hotkeys()
    p = get_platform()

    # Hyprland: use hyprctl + file watcher
    if p["hyprland"] and p["has_hyprctl"]:
        base = os.path.dirname(os.path.abspath(__file__))
        toggle_script = os.path.join(base, "..", "whisper-toggle.sh")
        snapshot_script = os.path.join(base, "..", "whisper-snapshot.sh")
        fullcontext_script = os.path.join(base, "..", "whisper-fullcontext.sh")
        try:
            subprocess.run(["hyprctl", "keyword", "bind", f"SUPER,{key},exec,{toggle_script}"],
                           capture_output=True, timeout=3)
            log.info(f"[Hotkey] Registered SUPER+{key} (toggle) via hyprctl")
            if snapshot_key:
                subprocess.run(["hyprctl", "keyword", "bind", f"SUPER,{snapshot_key},exec,{snapshot_script}"],
                               capture_output=True, timeout=3)
                log.info(f"[Hotkey] Registered SUPER+{snapshot_key} (snapshot) via hyprctl")
            if fullcontext_key:
                subprocess.run(["hyprctl", "keyword", "bind", f"SUPER,{fullcontext_key},exec,{fullcontext_script}"],
                               capture_output=True, timeout=3)
                log.info(f"[Hotkey] Registered SUPER+{fullcontext_key} (fullcontext) via hyprctl")
            _hotkey_ids.append(("hyprctl", key, snapshot_key, fullcontext_key))
            return True
        except Exception as e:
            log.error(f"[Hotkey] hyprctl failed: {e}")

    # Windows/Linux fallback: use keyboard lib
    if p["has_keyboard_lib"]:
        try:
            import keyboard
            key_map = {"space": "space", "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
                       "F5": "f5", "F6": "f6", "F7": "f7", "F8": "f8", "F9": "f9",
                       "F10": "f10", "F11": "f11", "F12": "f12"}
            hotkey_str = f"windows+{key_map.get(key, key.lower())}"
            keyboard.add_hotkey(hotkey_str, callback, suppress=True)
            _hotkey_ids.append(("keyboard", hotkey_str, ""))
            log.info(f"[Hotkey] Registered {hotkey_str} (toggle) via keyboard lib")

            if snapshot_key and snapshot_callback:
                snap_str = f"windows+{key_map.get(snapshot_key, snapshot_key.lower())}"
                keyboard.add_hotkey(snap_str, snapshot_callback, suppress=True)
                _hotkey_ids.append(("keyboard", snap_str, ""))
                log.info(f"[Hotkey] Registered {snap_str} (snapshot) via keyboard lib")

            if fullcontext_key and fullcontext_callback:
                fc_str = f"windows+{key_map.get(fullcontext_key, fullcontext_key.lower())}"
                keyboard.add_hotkey(fc_str, fullcontext_callback, suppress=True)
                _hotkey_ids.append(("keyboard", fc_str, ""))
                log.info(f"[Hotkey] Registered {fc_str} (fullcontext) via keyboard lib")
            return True
        except Exception as e:
            log.error(f"[Hotkey] keyboard lib failed: {e}")

    log.warning("[Hotkey] No global hotkey support. Use in-app keys.")
    return False


def unregister_global_hotkeys():
    """Remove all registered hotkeys."""
    p = get_platform()
    for entry in _hotkey_ids:
        method = entry[0]
        if method == "hyprctl":
            key, snap_key = entry[1], entry[2]
            fc_key = entry[3] if len(entry) > 3 else ""
            try:
                subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{key}"],
                               capture_output=True, timeout=3)
                if snap_key:
                    subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{snap_key}"],
                                   capture_output=True, timeout=3)
                if fc_key:
                    subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{fc_key}"],
                                   capture_output=True, timeout=3)
            except Exception:
                pass
        elif method == "keyboard":
            try:
                import keyboard
                keyboard.remove_hotkey(entry[1])
            except Exception:
                pass
    _hotkey_ids.clear()
    log.info("[Hotkey] Unregistered all")


# ── Window Focus ──

def focus_popup_window():
    """Focus the popup window using OS-specific method."""
    p = get_platform()

    if p["hyprland"] and p["has_hyprctl"]:
        try:
            import json
            r = subprocess.run(["hyprctl", "clients", "-j"],
                               capture_output=True, text=True, timeout=2)
            clients = json.loads(r.stdout)
            our = [c for c in clients if "main.py" in c.get("class", "")]
            if len(our) > 1:
                popup = min(our, key=lambda c: c["size"][0] * c["size"][1])
                subprocess.run(["hyprctl", "dispatch", "focuswindow",
                               f"address:{popup['address']}"],
                               capture_output=True, timeout=2)
                log.info(f"[Focus] hyprctl: {popup['address']}")
                return True
        except Exception as e:
            log.debug(f"[Focus] hyprctl failed: {e}")

    # Windows: pywebview handles focus via show()
    log.debug("[Focus] Using JS fallback")
    return False


# ── Sidebar Positioning ──

def position_sidebar(chat_window):
    """Position chat window as sidebar on the right edge."""
    import time as _time
    p = get_platform()

    if p["hyprland"] and p["has_hyprctl"]:
        def do_position():
            import json as _json
            chat = None
            for attempt in range(10):
                _time.sleep(0.5)
                r = subprocess.run(["hyprctl", "clients", "-j"],
                                   capture_output=True, text=True, timeout=2)
                clients = _json.loads(r.stdout)
                our = [c for c in clients if "main.py" in c.get("class", "")]
                if len(our) >= 2:
                    chat = min(our, key=lambda c: c["size"][0] * c["size"][1])
                    break

            if not chat:
                log.warning("[SIDEBAR] Window not found")
                return

            addr = chat["address"]
            r2 = subprocess.run(["hyprctl", "monitors", "-j"],
                                capture_output=True, text=True, timeout=2)
            monitors = _json.loads(r2.stdout)
            mon = next((m for m in monitors if m.get("focused")), monitors[0])
            mx, my = mon.get("x", 0), mon.get("y", 0)
            mw = int(mon["width"] / mon["scale"])
            mh = int(mon["height"] / mon["scale"])
            sw = 420
            x = mx + mw - sw

            subprocess.run(["hyprctl", "dispatch", f"setfloating address:{addr}"],
                           capture_output=True, timeout=2)
            _time.sleep(0.1)
            subprocess.run(["hyprctl", "dispatch", f"resizewindowpixel exact {sw} {mh},address:{addr}"],
                           capture_output=True, timeout=2)
            subprocess.run(["hyprctl", "dispatch", f"movewindowpixel exact {x} {my},address:{addr}"],
                           capture_output=True, timeout=2)
            subprocess.run(["hyprctl", "dispatch", f"pin address:{addr}"],
                           capture_output=True, timeout=2)
            log.info(f"[SIDEBAR] {sw}x{mh} at ({x},{my}) monitor={mon['name']}")

        threading.Thread(target=do_position, daemon=True).start()
        return

    # Windows: position via pywebview API
    if p["windows"] and chat_window:
        def do_position_win():
            _time.sleep(1)
            try:
                import ctypes
                import ctypes.wintypes

                user32 = ctypes.windll.user32

                # Find the monitor where the main window is
                # EnumWindows to find our main window hwnd
                main_hwnd = None
                WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
                def enum_cb(hwnd, lparam):
                    nonlocal main_hwnd
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        if "Whisper Copilot" in buf.value and "Chat" not in buf.value:
                            main_hwnd = hwnd
                    return True
                user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

                # Get monitor info for that window (or primary if not found)
                MONITOR_DEFAULTTOPRIMARY = 1
                if main_hwnd:
                    hmon = user32.MonitorFromWindow(main_hwnd, MONITOR_DEFAULTTOPRIMARY)
                else:
                    hmon = user32.MonitorFromPoint(ctypes.wintypes.POINT(0, 0), MONITOR_DEFAULTTOPRIMARY)

                class MONITORINFO(ctypes.Structure):
                    _fields_ = [("cbSize", ctypes.wintypes.DWORD),
                                ("rcMonitor", ctypes.wintypes.RECT),
                                ("rcWork", ctypes.wintypes.RECT),
                                ("dwFlags", ctypes.wintypes.DWORD)]

                mi = MONITORINFO()
                mi.cbSize = ctypes.sizeof(MONITORINFO)
                user32.GetMonitorInfoW(hmon, ctypes.byref(mi))

                work = mi.rcWork
                work_x, work_y = work.left, work.top
                work_w = work.right - work.left
                work_h = work.bottom - work.top

                sw = 420
                pad_top = 4
                chat_window.move(work_x + work_w - sw, work_y + pad_top)
                chat_window.resize(sw, work_h - pad_top)
                log.info(f"[SIDEBAR] Windows: {sw}x{work_h - pad_top} at x={work_x + work_w - sw} y={work_y + pad_top} workarea={work_w}x{work_h}")
            except Exception as e:
                log.debug(f"[SIDEBAR] Windows positioning failed: {e}")

        threading.Thread(target=do_position_win, daemon=True).start()
        return

    log.debug("[SIDEBAR] No sidebar positioning available")
