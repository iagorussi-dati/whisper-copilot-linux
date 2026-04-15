"""Speaker embedding extraction using SpeechBrain ECAPA-TDNN.

Replaces the Rust native-pyannote-rs DiarizationEngine.
"""
import numpy as np

SAMPLE_RATE = 16000
_model = None


def _get_model():
    global _model
    if _model is None:
        import os
        from pathlib import Path
        from speechbrain.inference.speaker import EncoderClassifier
        from speechbrain.utils.fetching import LocalStrategy
        
        cache_dir = Path.home() / ".cache" / "speechbrain"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Use COPY strategy to avoid symlink issues on Windows
        _model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=str(cache_dir),
            run_opts={"device": "cpu"},
            local_strategy=LocalStrategy.COPY,
        )
    return _model


def extract_embedding(samples_i16: np.ndarray) -> np.ndarray | None:
    """Extract voice embedding from PCM int16 samples at 16kHz.

    Returns a 1D numpy float32 array, or None if segment too short.
    """
    if len(samples_i16) < SAMPLE_RATE // 2:  # < 0.5s
        return None

    import torch
    model = _get_model()
    audio = samples_i16.astype(np.float32) / 32768.0
    tensor = torch.tensor(audio).unsqueeze(0)
    with torch.no_grad():
        emb = model.encode_batch(tensor)
    return emb.squeeze().cpu().numpy()
