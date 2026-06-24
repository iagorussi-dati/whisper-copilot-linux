#!/usr/bin/env python3
"""Whisper Copilot Lite — lightweight meeting copilot."""
import atexit
import logging
import os
import sys
from datetime import datetime

# Configure HuggingFace to use copy instead of symlinks (Windows compatibility)
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

import webview

from backend.api import Api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

# Save logs to file with timestamp
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(message)s"))
logging.getLogger().addHandler(file_handler)
logging.getLogger("whisper-copilot").info(f"Log file: {log_filename}")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")


def upload_log_to_s3():
    """Upload session log to S3 on exit."""
    log = logging.getLogger("whisper-copilot")
    try:
        if not os.path.exists(log_filename) or os.path.getsize(log_filename) < 100:
            return
        import boto3
        from dotenv import load_dotenv
        load_dotenv()

        bucket = os.getenv("AWS_LOG_BUCKET", "")
        region = os.getenv("AWS_REGION", "us-east-1")
        profile = os.getenv("AWS_LOG_PROFILE", "")

        if not bucket:
            log.info("[S3] AWS_LOG_BUCKET not set, skipping log upload")
            return

        if profile:
            session = boto3.Session(profile_name=profile)
            s3 = session.client("s3", region_name=region)
        else:
            s3 = boto3.client("s3", region_name=region)

        key = f"logs/{os.path.basename(log_filename)}"
        s3.upload_file(log_filename, bucket, key)
        log.info(f"[S3] Log uploaded: s3://{bucket}/{key}")
    except Exception as e:
        log.warning(f"[S3] Failed to upload log: {e}")


atexit.register(upload_log_to_s3)


def main():
    api = Api()
    is_windows = sys.platform == "win32"
    window = webview.create_window(
        "Whisper Copilot",
        url=os.path.join(FRONTEND_DIR, "index.html"),
        js_api=api,
        width=900,
        height=700,
        min_size=(700, 500),
        background_color="#0f172a",
        frameless=is_windows,
        easy_drag=False,
    )
    api.set_window(window)
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
