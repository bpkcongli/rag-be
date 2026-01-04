from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository
from domain.valueobjects.enums import DocumentStatus, FileType
from infrastructure.secondary.persistence.sqlalchemy_models import DocumentModel


class SqlAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: Session):
        self._session = session

    def list_all(self) -> list[Document]:
        stmt = select(DocumentModel).order_by(DocumentModel.created_at.desc())
        rows = self._session.execute(stmt).scalars().all()
        return [
            Document(
                id=r.id,
                filename=r.filename,
                file_type=FileType(r.file_type),
                status=DocumentStatus(r.status),
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in rows
        ]

    def create(
        self,
        *,
        document_id: str,
        filename: str,
        file_type: FileType,
        status: DocumentStatus,
    ) -> Document:
        model = DocumentModel(
            id=document_id,
            filename=filename,
            file_type=file_type.value,
            status=status.value,
        )
        self._session.add(model)
        self._session.flush()  # populate defaults
        self._session.refresh(model)
        return Document(
            id=model.id,
            filename=model.filename,
            file_type=FileType(model.file_type),
            status=DocumentStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
