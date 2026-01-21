from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.vector_index import VectorIndex
from domain.repositories.vector_index_repository import VectorIndexRepository
from domain.valueobjects.enums import ChunkingStrategy, VectorIndexStatus
from infrastructure.secondary.persistence.sqlalchemy_models import VectorIndexModel


class SqlAlchemyVectorIndexRepository(VectorIndexRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(self, vector_index: VectorIndex) -> None:
        model = VectorIndexModel(
            id=vector_index.id,
            document_id=vector_index.document_id,
            chunking_strategy=vector_index.chunking_strategy.value,
            embedding_model=vector_index.embedding_model,
            index_path=vector_index.index_path,
            status=vector_index.status.value,
            created_at=vector_index.created_at,
        )
        self._session.add(model)

    def update_status(self, *, vector_index_id: str, status: VectorIndexStatus) -> None:
        stmt = select(VectorIndexModel).where(VectorIndexModel.id == vector_index_id)
        row = self._session.execute(stmt).scalars().first()
        if row is None:
            return
        row.status = status.value
        self._session.add(row)

    def get_latest_ready(self, *, document_id: str, chunking_strategy: ChunkingStrategy) -> VectorIndex | None:
        stmt = (
            select(VectorIndexModel)
            .where(VectorIndexModel.document_id == document_id)
            .where(VectorIndexModel.chunking_strategy == chunking_strategy.value)
            .where(VectorIndexModel.status == VectorIndexStatus.READY.value)
            .order_by(VectorIndexModel.created_at.desc())
        )
        row = self._session.execute(stmt).scalars().first()
        if row is None:
            return None
        return VectorIndex(
            id=row.id,
            document_id=row.document_id,
            chunking_strategy=ChunkingStrategy(row.chunking_strategy),
            embedding_model=row.embedding_model,
            index_path=row.index_path,
            status=VectorIndexStatus(row.status),
            created_at=row.created_at,
        )


