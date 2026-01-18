from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.valueobjects.enums import ChunkingStrategy, VectorIndexStatus


@dataclass(frozen=True)
class VectorIndex:
    id: str
    document_id: str
    chunking_strategy: ChunkingStrategy
    embedding_model: str
    index_path: str
    status: VectorIndexStatus
    created_at: datetime


