from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.vector_index import VectorIndex
from domain.valueobjects.enums import VectorIndexStatus


class VectorIndexRepository(ABC):
    @abstractmethod
    def create(self, vector_index: VectorIndex) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, *, vector_index_id: str, status: VectorIndexStatus) -> None:
        raise NotImplementedError


