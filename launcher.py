"""Whisper Copilot — standalone launcher with embedded config."""
import os
import sys
import base64

# Embedded API keys (base64 encoded)
_K = {
    "B": "QUJTS1FtVmtjbTlqYTBGUVNVdGxlUzFtTWpjeUxXRjBMVFkxTkRZMU5ESXpNekE1TmpwbFMwYzRXa2hRSzJZd00yNTJPVWN2ZFdNMFUxWkdPVTFHYVc5RmR5OTVPRGhHVUVOUVNIRnJjWEZFWldadllXdEljQ3R3YWxGNVJVcEJRVDA9",
    "R": "us-east-1",
}


def _d(s):
    return base64.b64decode(s).decode()


def main():
    os.environ.setdefault("AWS_BEARER_TOKEN_BEDROCK", _d(_K["B"]))
    os.environ.setdefault("AWS_REGION", _K["R"])

    # Set base path for PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base)

    # Import and run
    from backend.api import Api
    import webview
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    api = Api()
    frontend = os.path.join(base, "frontend", "index.html")
    window = webview.create_window(
        "Whisper Copilot",
        url=frontend,
        js_api=api,
        width=900,
        height=700,
        min_size=(700, 500),
        background_color="#0f172a",
        frameless=True,
        easy_drag=False,
    )
    api.set_window(window)
    webview.start()


if __name__ == "__main__":
    main()
