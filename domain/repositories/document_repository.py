from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.document import Document
from domain.valueobjects.enums import DocumentStatus, FileType


class DocumentRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def create(
        self,
        *,
        document_id: str,
        filename: str,
        file_type: FileType,
        status: DocumentStatus,
    ) -> Document:
        raise NotImplementedError
