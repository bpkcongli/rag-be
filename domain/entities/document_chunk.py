from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    document_id: str
    chunk_index: int
    content: str
    token_count: int
    embedding_model: str
    created_at: datetime


