from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.document_chunk import DocumentChunk


class DocumentChunkRepository(ABC):
    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def bulk_create(self, chunks: list[DocumentChunk]) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_document_id(self, document_id: str) -> list[DocumentChunk]:
        raise NotImplementedError


