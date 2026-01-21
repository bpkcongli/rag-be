from __future__ import annotations

from sqlalchemy.orm import Session

from domain.repositories.rag_answer_repository import RagAnswerRepository
from infrastructure.secondary.persistence.sqlalchemy_models import RagAnswerModel


class SqlAlchemyRagAnswerRepository(RagAnswerRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        *,
        rag_query_id: int,
        answer: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        latency_ms: int | None,
    ) -> int:
        model = RagAnswerModel(
            rag_query_id=rag_query_id,
            answer=answer,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
        )
        self._session.add(model)
        self._session.flush()
        return int(model.id)


