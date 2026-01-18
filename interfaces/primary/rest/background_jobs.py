from __future__ import annotations

from application.services.document_chunking_service import DocumentChunkingService
from application.services.document_indexing_service import DocumentIndexingService
from domain.valueobjects.enums import ChunkingStrategy, DocumentStatus
from infrastructure.config.database import SessionLocal
from infrastructure.config.settings import get_settings
from infrastructure.secondary.embedding.sentence_transformer_embedding import (
    SentenceTransformerEmbeddingModel,
)
from infrastructure.secondary.persistence.document_chunk_repository_sqlalchemy import (
    SqlAlchemyDocumentChunkRepository,
)
from infrastructure.secondary.persistence.document_repository_sqlalchemy import (
    SqlAlchemyDocumentRepository,
)
from infrastructure.secondary.persistence.vector_index_repository_sqlalchemy import (
    SqlAlchemyVectorIndexRepository,
)
from infrastructure.secondary.storage.local_file_storage import LocalFileStorage


def run_document_indexing_job(*, document_id: str, chunking_strategy: ChunkingStrategy) -> None:
    """
    Background job entrypoint.
    Creates its own DB session to avoid depending on request-scoped sessions.
    """
    settings = get_settings()
    storage = LocalFileStorage(base_dir=settings.storage_dir)
    embed_model = SentenceTransformerEmbeddingModel(settings.embedding_model_name, device="cpu")

    session = SessionLocal()
    try:
        doc_repo = SqlAlchemyDocumentRepository(session)
        chunk_repo = SqlAlchemyDocumentChunkRepository(session)
        vector_repo = SqlAlchemyVectorIndexRepository(session)

        chunking_service = DocumentChunkingService(embedding_model=embed_model)
        indexing_service = DocumentIndexingService(
            document_repo=doc_repo,
            chunk_repo=chunk_repo,
            vector_index_repo=vector_repo,
            storage=storage,
            embedding_model=embed_model,
            chunking_service=chunking_service,
        )

        indexing_service.index_document(document_id=document_id, chunking_strategy=chunking_strategy)
        session.commit()
    except Exception:
        session.rollback()
        # try to mark document failed if possible
        try:
            SqlAlchemyDocumentRepository(session).update_status(document_id=document_id, status=DocumentStatus.FAILED)
            session.commit()
        except Exception:
            session.rollback()
        raise
    finally:
        session.close()


