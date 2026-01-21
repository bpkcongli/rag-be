from __future__ import annotations

from sqlalchemy.orm import Session

from domain.repositories.rag_query_repository import RagQueryRepository
from infrastructure.secondary.persistence.sqlalchemy_models import RagQueryModel


class SqlAlchemyRagQueryRepository(RagQueryRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        *,
        query_text: str,
        scope: dict,
        embedding_model: str,
        llm_model: str,
    ) -> int:
        model = RagQueryModel(
            query_text=query_text,
            scope=scope,
            embedding_model=embedding_model,
            llm_model=llm_model,
        )
        self._session.add(model)
        self._session.flush()
        return int(model.id)


