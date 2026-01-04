from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass

from domain.exceptions import StorageError


def _safe_filename(filename: str) -> str:
    # keep ascii-ish and a few symbols; prevent path traversal
    name = os.path.basename(filename)
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip()
    return name or "uploaded_file"


@dataclass(frozen=True)
class LocalFileStorage:
    base_dir: str

    def _document_dir(self, document_id: str) -> str:
        return os.path.join(self.base_dir, "documents", document_id)

    def delete_document(self, *, document_id: str) -> None:
        """Best-effort delete of a stored document directory."""
        target_dir = self._document_dir(document_id)
        try:
            if os.path.isdir(target_dir):
                shutil.rmtree(target_dir)
        except Exception:
            # best-effort cleanup; ignore
            return

    def save(self, *, document_id: str, original_filename: str, file_obj) -> str:
        """
        Save uploaded file to:
          {base_dir}/documents/{document_id}/{safe_filename}

        Returns absolute path of stored file.
        """
        safe_name = _safe_filename(original_filename)
        target_dir = self._document_dir(document_id)
        target_path = os.path.join(target_dir, safe_name)

        try:
            os.makedirs(target_dir, exist_ok=True)
            with open(target_path, "wb") as f:
                shutil.copyfileobj(file_obj, f)
        except Exception as e:
            raise StorageError(f"Failed to store file: {e}") from e

        return target_path
