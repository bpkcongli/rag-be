from __future__ import annotations

from sentence_transformers import CrossEncoder

from application.ports.reranker import Reranker


class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str, device: str = "cpu"):
        self._model_name = model_name
        self._model = CrossEncoder(model_name, device=device)

    def name(self) -> str:
        return self._model_name

    def score(self, *, query: str, documents: list[str]) -> list[float]:
        pairs = [(query, d) for d in documents]
        scores = self._model.predict(pairs)
        return [float(s) for s in scores]


