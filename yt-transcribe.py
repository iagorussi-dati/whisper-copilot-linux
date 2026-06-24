#!/usr/bin/env python3
"""Transcreve vídeos do YouTube usando yt-dlp + Groq Whisper API."""
import sys
import os
import subprocess
import tempfile
import math
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv
from backend.transcription.groq import GroqClient

load_dotenv(Path(__file__).parent / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHUNK_SECONDS = 600  # 10 min chunks (well under 25MB limit)


def get_video_title(url: str) -> str:
    r = subprocess.run(["yt-dlp", "--print", "title", url], capture_output=True, text=True)
    return r.stdout.strip() or "video"


def download_audio(url: str, outpath: str):
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", outpath,
        url
    ], check=True)


def get_duration(path: str) -> float:
    r = subprocess.run(
        ["ffmpeg", "-i", path, "-f", "null", "-"],
        capture_output=True, text=True
    )
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 0


def split_audio(path: str, chunk_secs: int, tmpdir: str) -> list[str]:
    duration = get_duration(path)
    if duration <= chunk_secs:
        return [path]
    n_chunks = math.ceil(duration / chunk_secs)
    chunks = []
    for i in range(n_chunks):
        out = os.path.join(tmpdir, f"chunk_{i:03d}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", path,
            "-ss", str(i * chunk_secs),
            "-t", str(chunk_secs),
            "-ar", "16000", "-ac", "1",
            out
        ], capture_output=True, check=True)
        chunks.append(out)
    return chunks


def main():
    if len(sys.argv) < 2:
        print("Uso: python yt-transcribe.py <URL_DO_YOUTUBE>")
        sys.exit(1)

    url = sys.argv[1]
    if not GROQ_API_KEY:
        print("Erro: GROQ_API_KEY não encontrada no .env")
        sys.exit(1)

    print(f"🎬 Buscando título...")
    title = get_video_title(url)
    safe_title = re.sub(r'[^\w\s-]', '', title)[:60].strip()
    print(f"📹 {title}")

    client = GroqClient(api_key=GROQ_API_KEY, language="pt")

    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "audio.wav")
        print(f"⬇️  Baixando áudio...")
        download_audio(url, wav_path)

        print(f"✂️  Dividindo em chunks...")
        chunks = split_audio(wav_path, CHUNK_SECONDS, tmpdir)
        print(f"   {len(chunks)} parte(s)")

        full_text = []
        for i, chunk in enumerate(chunks):
            print(f"🎙️  Transcrevendo parte {i+1}/{len(chunks)}...")
            with open(chunk, "rb") as f:
                data = f.read()
            for attempt in range(5):
                try:
                    text = client.transcribe(data)
                    break
                except Exception as e:
                    print(f"   ⚠️  Erro: {e} — tentativa {attempt+1}/5")
                    import time; time.sleep(10 * (attempt + 1))
            else:
                text = f"[ERRO: não conseguiu transcrever parte {i+1}]"
            full_text.append(text)

    transcript = "\n\n".join(full_text)
    out_dir = Path(__file__).parent / "transcricoes"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{safe_title}.md"

    out_file.write_text(f"# {title}\n\n**Fonte:** {url}\n\n---\n\n{transcript}\n")
    print(f"\n✅ Transcrição salva em: {out_file}")


if __name__ == "__main__":
    main()
