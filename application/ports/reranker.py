from __future__ import annotations

from abc import ABC, abstractmethod


class Reranker(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def score(self, *, query: str, documents: list[str]) -> list[float]:
        """Return relevance scores aligned with documents list."""
        raise NotImplementedError


