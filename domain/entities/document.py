from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.valueobjects.enums import DocumentStatus, FileType


@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    file_type: FileType
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
