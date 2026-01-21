from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RagAnswer:
    id: int
    rag_query_id: int
    answer: str
    prompt_tokens: int | None
    completion_tokens: int | None
    latency_ms: int | None


