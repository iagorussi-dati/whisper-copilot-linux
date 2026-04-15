#!/usr/bin/env python3
"""Whisper Copilot Lite — lightweight meeting copilot."""
import logging
import os
import sys

# Configure HuggingFace to use copy instead of symlinks (Windows compatibility)
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

import webview

from backend.api import Api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")


def main():
    api = Api()
    window = webview.create_window(
        "Whisper Copilot",
        url=os.path.join(FRONTEND_DIR, "index.html"),
        js_api=api,
        width=900,
        height=700,
        min_size=(700, 500),
        background_color="#0f172a",
    )
    api.set_window(window)
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
