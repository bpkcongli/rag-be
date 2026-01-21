from __future__ import annotations

from abc import ABC, abstractmethod


class RagAnswerRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        rag_query_id: int,
        answer: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        latency_ms: int | None,
    ) -> int:
        """Returns created rag_answers.id"""
        raise NotImplementedError


