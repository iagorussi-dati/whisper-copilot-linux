"""Platform detection and OS-specific utilities."""
import os
import sys
import shutil
import subprocess
import logging

log = logging.getLogger("whisper-copilot")


def detect_platform() -> dict:
    """Detect the current platform and available tools."""
    info = {
        "os": sys.platform,  # linux, win32, darwin
        "wsl": False,
        "wayland": False,
        "hyprland": False,
        "x11": False,
        "has_hyprctl": False,
        "has_xdotool": False,
        "has_pactl": False,
        "has_pw_cat": False,
    }

    # WSL detection
    if sys.platform == "linux":
        try:
            with open("/proc/version", "r") as f:
                version = f.read().lower()
                info["wsl"] = "microsoft" in version or "wsl" in version
        except Exception:
            pass

    # Display server
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
    info["wayland"] = session_type == "wayland"
    info["x11"] = session_type == "x11" or bool(os.environ.get("DISPLAY"))

    # Hyprland
    info["hyprland"] = bool(os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"))

    # Tools
    info["has_hyprctl"] = shutil.which("hyprctl") is not None
    info["has_xdotool"] = shutil.which("xdotool") is not None
    info["has_pactl"] = shutil.which("pactl") is not None
    info["has_pw_cat"] = shutil.which("pw-cat") is not None

    return info


_platform = None


def get_platform() -> dict:
    global _platform
    if _platform is None:
        _platform = detect_platform()
        log.info(f"[Platform] {_platform}")
    return _platform


def register_global_hotkey(key: str, toggle_script: str) -> bool:
    """Register a global hotkey. Returns True if successful."""
    p = get_platform()

    if p["hyprland"] and p["has_hyprctl"]:
        cmd = f"SUPER,{key},exec,{toggle_script}"
        try:
            subprocess.run(["hyprctl", "keyword", "bind", cmd],
                           capture_output=True, timeout=3)
            log.info(f"[Hotkey] Registered SUPER+{key} via hyprctl")
            return True
        except Exception as e:
            log.error(f"[Hotkey] hyprctl failed: {e}")

    if p["x11"] and p["has_xdotool"]:
        # X11: use xbindkeys or just log that it's not supported
        log.warning("[Hotkey] X11 global hotkeys not implemented. Use in-app Espaço/T.")
        return False

    if p["wsl"]:
        log.warning("[Hotkey] WSL: global hotkeys not available. Use in-app Espaço/T.")
        return False

    log.warning(f"[Hotkey] No global hotkey support for this platform")
    return False


def unregister_global_hotkey(key: str) -> bool:
    """Unregister a global hotkey."""
    p = get_platform()

    if p["hyprland"] and p["has_hyprctl"]:
        try:
            subprocess.run(["hyprctl", "keyword", "unbind", f"SUPER,{key}"],
                           capture_output=True, timeout=3)
            log.info(f"[Hotkey] Unregistered SUPER+{key}")
            return True
        except Exception:
            pass

    return False


def focus_popup_window():
    """Focus the popup window using OS-specific method."""
    p = get_platform()

    if p["hyprland"] and p["has_hyprctl"]:
        try:
            import json
            r = subprocess.run(["hyprctl", "clients", "-j"],
                               capture_output=True, text=True, timeout=2)
            clients = json.loads(r.stdout)
            our_windows = [c for c in clients if "main.py" in c.get("class", "")]
            if len(our_windows) > 1:
                popup = min(our_windows, key=lambda c: c["size"][0] * c["size"][1])
                subprocess.run(["hyprctl", "dispatch", "focuswindow",
                               f"address:{popup['address']}"],
                               capture_output=True, timeout=2)
                log.info(f"[Focus] hyprctl focused: {popup['address']}")
                return True
        except Exception as e:
            log.debug(f"[Focus] hyprctl failed: {e}")

    if p["x11"] and p["has_xdotool"]:
        try:
            subprocess.run(["xdotool", "search", "--name", "Whisper Chat",
                           "windowactivate"], capture_output=True, timeout=2)
            log.info("[Focus] xdotool focused Whisper Chat")
            return True
        except Exception as e:
            log.debug(f"[Focus] xdotool failed: {e}")

    # Fallback: no OS-level focus, rely on JS
    log.debug("[Focus] No OS-level focus available, relying on JS")
    return False
