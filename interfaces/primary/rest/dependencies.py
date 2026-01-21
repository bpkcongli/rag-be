from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from application.services.answer_generation_service import (
    AnswerGenerationConfig,
    AnswerGenerationService,
)
from application.services.document_management_service import DocumentManagementService
from infrastructure.config.database import SessionLocal
from infrastructure.config.settings import get_settings
from infrastructure.secondary.persistence.document_repository_sqlalchemy import (
    SqlAlchemyDocumentRepository,
)
from infrastructure.secondary.persistence.document_chunk_repository_sqlalchemy import (
    SqlAlchemyDocumentChunkRepository,
)
from infrastructure.secondary.persistence.vector_index_repository_sqlalchemy import (
    SqlAlchemyVectorIndexRepository,
)
from infrastructure.secondary.persistence.rag_answer_repository_sqlalchemy import (
    SqlAlchemyRagAnswerRepository,
)
from infrastructure.secondary.persistence.rag_query_repository_sqlalchemy import (
    SqlAlchemyRagQueryRepository,
)
from infrastructure.secondary.storage.local_file_storage import LocalFileStorage


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_storage() -> LocalFileStorage:
    settings = get_settings()
    return LocalFileStorage(base_dir=settings.storage_dir)


def get_document_service(
    db: Session = Depends(get_db_session),
    storage: LocalFileStorage = Depends(get_storage),
) -> DocumentManagementService:
    repo = SqlAlchemyDocumentRepository(db)
    return DocumentManagementService(repo=repo, storage=storage)


def get_answer_generation_service(
    request: Request,
    db: Session = Depends(get_db_session),
) -> AnswerGenerationService:
    settings = get_settings()

    # loaded once at startup, see interfaces.primary.rest.app.create_app()
    embed_model = request.app.state.embedding_model
    reranker = request.app.state.reranker
    llm = request.app.state.llm

    rag_query_repo = SqlAlchemyRagQueryRepository(db)
    rag_answer_repo = SqlAlchemyRagAnswerRepository(db)
    chunk_repo = SqlAlchemyDocumentChunkRepository(db)
    vector_repo = SqlAlchemyVectorIndexRepository(db)

    cfg = AnswerGenerationConfig(
        retrieve_top_n=settings.retrieve_top_n,
        rerank_top_k=settings.rerank_top_k,
        max_context_chunks=settings.max_context_chunks,
        max_new_tokens=settings.max_new_tokens,
        temperature=settings.temperature,
        top_p=settings.top_p,
    )

    return AnswerGenerationService(
        rag_query_repo=rag_query_repo,
        rag_answer_repo=rag_answer_repo,
        chunk_repo=chunk_repo,
        vector_index_repo=vector_repo,
        embedding_model=embed_model,
        reranker=reranker,
        llm=llm,
        config=cfg,
    )
