from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from application.services.document_management_service import DocumentManagementService
from infrastructure.config.database import SessionLocal
from infrastructure.config.settings import get_settings
from infrastructure.secondary.persistence.document_repository_sqlalchemy import (
    SqlAlchemyDocumentRepository,
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
