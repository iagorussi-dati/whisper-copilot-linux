"""Voice bank — cosine similarity matching using MAX similarity."""
import numpy as np


class VoiceMatch:
    def __init__(self, voice_label: str, is_new: bool, similarity: float):
        self.voice_label = voice_label
        self.is_new = is_new
        self.similarity = similarity


class VoiceBank:
    def __init__(self, threshold: float = 0.30):
        self.threshold = threshold
        self._voices: list[tuple[str, list[np.ndarray]]] = []
        self._next_id = 1
        self._name_map: dict[str, str] = {}

    def match_or_create(self, embedding: np.ndarray) -> VoiceMatch:
        best_idx, best_sim = None, 0.0
        for i, (_, embs) in enumerate(self._voices):
            # MAX similarity: compare against each individual embedding
            for bank_emb in embs:
                sim = self._cosine_sim(embedding, bank_emb)
                if sim > self.threshold and sim > best_sim:
                    best_idx, best_sim = i, sim

        if best_idx is not None:
            label = self._voices[best_idx][0]
            return VoiceMatch(label, False, best_sim)

        label = f"Voz {self._next_id}"
        self._next_id += 1
        self._voices.append((label, [embedding.copy()]))
        return VoiceMatch(label, True, 0.0)

    def update_embedding(self, voice_label: str, embedding: np.ndarray):
        for label, embs in self._voices:
            if label == voice_label:
                embs.append(embedding.copy())
                return

    def display_name(self, voice_label: str) -> str:
        return self._name_map.get(voice_label, voice_label)

    def set_name_map(self, mapping: dict[str, str]):
        self._name_map.update(mapping)

    def speakers(self) -> list[tuple[str, str | None]]:
        return [(label, self._name_map.get(label)) for label, _ in self._voices]

    def has_unnamed(self) -> bool:
        return any(label not in self._name_map for label, _ in self._voices)

    def build_context(self) -> str:
        lines = ["Vozes detectadas por embedding de voz:"]
        for label, embs in self._voices:
            lines.append(f"- {label}: {len(embs)} amostras de fala")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        dot = np.dot(a, b)
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(dot / (na * nb))
