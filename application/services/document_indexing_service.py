from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

import faiss
import numpy as np

from application.ports.embedding_model import EmbeddingModel
from application.services.document_chunking_service import DocumentChunkingService
from domain.entities.document_chunk import DocumentChunk
from domain.entities.vector_index import VectorIndex
from domain.repositories.document_chunk_repository import DocumentChunkRepository
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.vector_index_repository import VectorIndexRepository
from domain.valueobjects.enums import ChunkingStrategy, DocumentStatus, VectorIndexStatus
from infrastructure.secondary.parsing.document_parser import extract_text
from infrastructure.secondary.storage.local_file_storage import LocalFileStorage


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _token_count(text: str) -> int:
    return len(text.split())


@dataclass
class DocumentIndexingService:
    document_repo: DocumentRepository
    chunk_repo: DocumentChunkRepository
    vector_index_repo: VectorIndexRepository
    storage: LocalFileStorage
    embedding_model: EmbeddingModel
    chunking_service: DocumentChunkingService

    def index_document(self, *, document_id: str, chunking_strategy: ChunkingStrategy) -> None:
        """
        Full indexing pipeline:
        - Parse document to text
        - Chunk (semantic sliding-window)
        - Embed chunks
        - Build FAISS index, save to local FS
        - Persist chunks + vector index metadata
        - Update document status
        """
        doc = self.document_repo.get_by_id(document_id)
        if doc is None:
            raise ValueError(f"Document not found: {document_id}")

        vector_index_id = str(uuid4())
        created_at = _utcnow()
        index_path = self.storage.get_faiss_index_path(
            document_id=document_id, chunking_strategy=chunking_strategy.value
        )

        try:
            # mark index metadata as building
            self.vector_index_repo.create(
                VectorIndex(
                    id=vector_index_id,
                    document_id=document_id,
                    chunking_strategy=chunking_strategy,
                    embedding_model=self.embedding_model.name(),
                    index_path=index_path,
                    status=VectorIndexStatus.BUILDING,
                    created_at=created_at,
                )
            )

            # parse
            file_path = self.storage.get_uploaded_file_path(document_id=document_id)
            text = extract_text(file_path, doc.file_type)

            # chunk
            chunks = self.chunking_service.semantic_sliding_window(text=text)

            # embed
            chunk_emb = self.embedding_model.encode([f"chunk: {c}" for c in chunks])
            if chunk_emb.size == 0:
                raise ValueError("No embeddings produced (empty document?)")

            # build FAISS
            emb = chunk_emb.astype(np.float32, copy=True)
            faiss.normalize_L2(emb)
            index = faiss.IndexFlatIP(emb.shape[1])
            index.add(emb)

            # store index file
            stored_index_path = self.storage.save_faiss_index(
                document_id=document_id, chunking_strategy=chunking_strategy.value, index=index
            )

            # store chunks (replace existing)
            self.chunk_repo.delete_by_document_id(document_id)
            chunk_entities: list[DocumentChunk] = []
            for i, content in enumerate(chunks):
                chunk_entities.append(
                    DocumentChunk(
                        id=str(uuid4()),
                        document_id=document_id,
                        chunk_index=i,
                        content=content,
                        token_count=_token_count(content),
                        embedding_model=self.embedding_model.name(),
                        created_at=created_at,
                    )
                )
            if chunk_entities:
                self.chunk_repo.bulk_create(chunk_entities)

            # mark index ready & doc indexed
            self.vector_index_repo.update_status(vector_index_id=vector_index_id, status=VectorIndexStatus.READY)
            self.document_repo.update_status(document_id=document_id, status=DocumentStatus.INDEXED)
        except Exception:
            # mark failed (best-effort)
            try:
                self.vector_index_repo.update_status(
                    vector_index_id=vector_index_id, status=VectorIndexStatus.FAILED
                )
            except Exception:
                pass
            self.document_repo.update_status(document_id=document_id, status=DocumentStatus.FAILED)
            raise


