from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from domain.entities.document import Document
from domain.valueobjects.enums import DocumentStatus, FileType


class DocumentDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=lambda s: s.split("_")[0] + "".join(
            p[:1].upper() + p[1:] for p in s.split("_")[1:]
        ),
        populate_by_name=True,
    )

    id: str
    filename: str
    file_type: FileType = Field(..., description="Document file type")
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_domain(doc: Document) -> "DocumentDTO":
        return DocumentDTO(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            status=doc.status,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
