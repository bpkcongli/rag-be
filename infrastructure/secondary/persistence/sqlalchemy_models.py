from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.mysql import ENUM as MYSQL_ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    file_type: Mapped[str | None] = mapped_column(
        MYSQL_ENUM("PDF", "DOCX", "HTML", name="file_type"),
        nullable=True,
    )
    status: Mapped[str | None] = mapped_column(
        MYSQL_ENUM("UPLOADED", "INDEXING", "INDEXED", "FAILED", name="document_status"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
