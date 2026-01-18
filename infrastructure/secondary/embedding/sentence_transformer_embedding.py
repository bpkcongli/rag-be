from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from application.ports.embedding_model import EmbeddingModel


class SentenceTransformerEmbeddingModel(EmbeddingModel):
    def __init__(self, model_name: str, device: str = "cpu"):
        self._model_name = model_name
        self._model = SentenceTransformer(model_name, device=device)

    def name(self) -> str:
        return self._model_name

    def encode(self, texts: list[str]) -> np.ndarray:
        # SentenceTransformer returns numpy by default if convert_to_numpy=True.
        emb = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return emb.astype(np.float32)


