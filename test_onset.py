"""Test: detectar onset de fala em buffers de áudio pra ordenar mic vs monitor."""
import sys, os, wave, struct
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))

SAMPLE_RATE = 16000
FRAME_MS = 30  # 30ms frames
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)
RMS_THRESHOLD = 0.01  # threshold pra considerar "fala"
MIN_SPEECH_FRAMES = 3  # precisa de 3 frames consecutivos pra confirmar fala

def read_wav(path):
    with wave.open(path, "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        return np.frombuffer(raw, dtype=np.int16)

def detect_speech_onset(samples: np.ndarray) -> float | None:
    """Detecta em que segundo a fala começa no buffer.
    Retorna offset em segundos, ou None se silêncio total."""
    float_samples = samples.astype(np.float32) / 32768.0
    consecutive = 0
    for i in range(0, len(float_samples) - FRAME_SAMPLES, FRAME_SAMPLES):
        frame = float_samples[i:i + FRAME_SAMPLES]
        rms = float(np.sqrt(np.mean(frame ** 2)))
        if rms >= RMS_THRESHOLD:
            consecutive += 1
            if consecutive >= MIN_SPEECH_FRAMES:
                # Onset é onde a sequência começou
                onset_sample = i - (MIN_SPEECH_FRAMES - 1) * FRAME_SAMPLES
                return max(0, onset_sample) / SAMPLE_RATE
        else:
            consecutive = 0
    return None

# Testar com os WAVs
print("=" * 60)
print("TEST: Detecção de onset de fala")
print("=" * 60)

# Monitor: fala começa logo no início
mon_samples = read_wav("/tmp/test_mon.wav")
mon_onset = detect_speech_onset(mon_samples)
print(f"\nMonitor (15s, fala desde o início):")
print(f"  Onset: {mon_onset:.2f}s" if mon_onset else "  Onset: None (silêncio)")

# Mic LATE: 8s silêncio + fala
mic_late_samples = read_wav("/tmp/test_mic_late.wav")
mic_late_onset = detect_speech_onset(mic_late_samples)
print(f"\nMic LATE (8s silêncio + 5s fala):")
print(f"  Onset: {mic_late_onset:.2f}s" if mic_late_onset else "  Onset: None (silêncio)")

# Mic EARLY: fala desde o início
mic_early_samples = read_wav("/tmp/test_mic_early.wav")
mic_early_onset = detect_speech_onset(mic_early_samples)
print(f"\nMic EARLY (fala desde o início):")
print(f"  Onset: {mic_early_onset:.2f}s" if mic_early_onset else "  Onset: None (silêncio)")

# Teste de ordenação
print(f"\n{'=' * 60}")
print("CENÁRIO 1: Mic fala DEPOIS do monitor")
print(f"  Monitor onset: {mon_onset:.2f}s, Mic onset: {mic_late_onset:.2f}s")
if mon_onset is not None and mic_late_onset is not None:
    order = "monitor → mic" if mon_onset <= mic_late_onset else "mic → monitor"
    expected = "monitor → mic"
    print(f"  Ordem: {order} {'✅' if order == expected else '❌'}")

print(f"\nCENÁRIO 2: Mic fala ANTES/junto do monitor")
print(f"  Monitor onset: {mon_onset:.2f}s, Mic onset: {mic_early_onset:.2f}s")
if mon_onset is not None and mic_early_onset is not None:
    order = "monitor → mic" if mon_onset <= mic_early_onset else "mic → monitor"
    # Ambos falam desde o início, qualquer ordem é aceitável
    print(f"  Ordem: {order} (ambos falam cedo, OK)")
