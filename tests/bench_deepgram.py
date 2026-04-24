"""Benchmark: Deepgram diarização vs Groq+Bedrock."""
import time, os, json, httpx

DEEPGRAM_KEY = "71b16793b6b1e6cda1887ee66b53d503b6c00d25"
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

# Testar com chunks de diferentes tamanhos
FILES = [
    ("4min-teste.wav", "4min completo"),
    ("discovery-chunk-0.wav", "Discovery 2min"),
    ("discovery-chunk-1.wav", "Discovery 2min #2"),
]


def test_deepgram(filepath, label):
    """Deepgram com diarização."""
    with open(filepath, "rb") as f:
        audio = f.read()

    t0 = time.time()
    r = httpx.post(
        "https://api.deepgram.com/v1/listen",
        headers={"Authorization": f"Token {DEEPGRAM_KEY}", "Content-Type": "audio/wav"},
        params={
            "model": "nova-3",
            "language": "pt-BR",
            "diarize": "true",
            "punctuate": "true",
            "smart_format": "true",
        },
        content=audio,
        timeout=60,
    )
    elapsed = time.time() - t0

    if r.status_code != 200:
        return {"error": r.text[:200], "elapsed": elapsed}

    data = r.json()
    words = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("words", [])

    # Agrupar por speaker
    segments = []
    current_speaker = None
    current_text = []
    for w in words:
        sp = w.get("speaker", 0)
        if sp != current_speaker:
            if current_text:
                segments.append({"speaker": f"Speaker {current_speaker}", "text": " ".join(current_text)})
            current_speaker = sp
            current_text = [w["word"]]
        else:
            current_text.append(w["word"])
    if current_text:
        segments.append({"speaker": f"Speaker {current_speaker}", "text": " ".join(current_text)})

    return {"segments": segments, "elapsed": elapsed, "n_speakers": len(set(w.get("speaker", 0) for w in words))}


if __name__ == "__main__":
    print("=" * 60)
    print("BENCHMARK: DEEPGRAM DIARIZAÇÃO (nova-3, pt-BR)")
    print("=" * 60)

    for filename, label in FILES:
        filepath = os.path.join(FIXTURES, filename)
        if not os.path.exists(filepath):
            print(f"\n❌ {label}: arquivo não encontrado")
            continue

        size_mb = os.path.getsize(filepath) / 1024 / 1024
        print(f"\n{'─'*60}")
        print(f"📌 {label} ({size_mb:.1f}MB)")

        result = test_deepgram(filepath, label)

        if "error" in result:
            print(f"  ❌ Erro: {result['error']}")
            print(f"  ⏱️ {result['elapsed']:.1f}s")
            continue

        print(f"  ⏱️ {result['elapsed']:.1f}s")
        print(f"  👥 {result['n_speakers']} speakers detectados")
        print(f"  📝 {len(result['segments'])} segmentos")

        for seg in result["segments"][:10]:
            print(f"  [{seg['speaker']}] {seg['text'][:80]}")
        if len(result["segments"]) > 10:
            print(f"  ... +{len(result['segments'])-10} segmentos")
