from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RagQuery:
    id: int
    query_text: str
    scope: dict
    embedding_model: str
    llm_model: str
    created_at: datetime


