from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.vector_index import VectorIndex
from domain.repositories.vector_index_repository import VectorIndexRepository
from domain.valueobjects.enums import VectorIndexStatus
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


