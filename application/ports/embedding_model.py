from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class EmbeddingModel(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def encode(self, texts: list[str]) -> np.ndarray:
        """Return embeddings as float32 numpy array shape (n, d)."""
        raise NotImplementedError


