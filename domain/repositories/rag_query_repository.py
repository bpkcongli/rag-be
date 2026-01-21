from __future__ import annotations

from abc import ABC, abstractmethod


class RagQueryRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        query_text: str,
        scope: dict,
        embedding_model: str,
        llm_model: str,
    ) -> int:
        """Returns created rag_queries.id"""
        raise NotImplementedError


