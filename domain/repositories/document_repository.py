from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.document import Document
from domain.valueobjects.enums import DocumentStatus, FileType


class DocumentRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, document_id: str) -> Document | None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, *, document_id: str, status: DocumentStatus) -> None:
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


