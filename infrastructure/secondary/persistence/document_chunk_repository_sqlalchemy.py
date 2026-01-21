from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from domain.entities.document_chunk import DocumentChunk
from domain.repositories.document_chunk_repository import DocumentChunkRepository
from infrastructure.secondary.persistence.sqlalchemy_models import DocumentChunkModel


class SqlAlchemyDocumentChunkRepository(DocumentChunkRepository):
    def __init__(self, session: Session):
        self._session = session

    def delete_by_document_id(self, document_id: str) -> None:
        self._session.execute(delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id))

    def bulk_create(self, chunks: list[DocumentChunk]) -> None:
        models = [
            DocumentChunkModel(
                id=c.id,
                document_id=c.document_id,
                chunk_index=c.chunk_index,
                content=c.content,
                token_count=c.token_count,
                embedding_model=c.embedding_model,
                created_at=c.created_at,
            )
            for c in chunks
        ]
        self._session.add_all(models)

    def list_by_document_id(self, document_id: str) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index.asc())
        )
        rows = self._session.execute(stmt).scalars().all()
        return [
            DocumentChunk(
                id=r.id,
                document_id=r.document_id,
                chunk_index=int(r.chunk_index),
                content=r.content,
                token_count=int(r.token_count),
                embedding_model=r.embedding_model,
                created_at=r.created_at,
            )
            for r in rows
        ]


