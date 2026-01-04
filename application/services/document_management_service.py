from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from domain.exceptions import UnsupportedFileTypeError
from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository
from domain.valueobjects.enums import DocumentStatus, FileType
from infrastructure.secondary.storage.local_file_storage import LocalFileStorage


def _detect_file_type(filename: str) -> FileType:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return FileType.PDF
    if lowered.endswith(".docx"):
        return FileType.DOCX
    if lowered.endswith(".html") or lowered.endswith(".htm"):
        return FileType.HTML
    raise UnsupportedFileTypeError(f"Unsupported file type: {filename}")


@dataclass
class DocumentManagementService:
    repo: DocumentRepository
    storage: LocalFileStorage

    def list_documents(self):
        return self.repo.list_all()

    def upload_document(self, *, original_filename: str, file_obj) -> Document:
        """
        Persist file to local storage and create DB record.

        Parameters
        - original_filename: uploaded filename
        - file_obj: a readable binary file-like object (e.g. UploadFile.file)

        Returns
        - Document
        """
        file_type = _detect_file_type(original_filename)
        document_id = str(uuid4())

        # Save file first; if it fails, don't create DB record.
        self.storage.save(document_id=document_id, original_filename=original_filename, file_obj=file_obj)

        try:
            return self.repo.create(
                document_id=document_id,
                filename=original_filename,
                file_type=file_type,
                status=DocumentStatus.UPLOADED,
            )
        except Exception:
            # If DB write fails, try to cleanup stored file to avoid orphaned storage.
            self.storage.delete_document(document_id=document_id)
            raise
