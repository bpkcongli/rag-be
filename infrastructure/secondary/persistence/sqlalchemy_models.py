from __future__ import annotations

from datetime import datetime

import json

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.mysql import ENUM as MYSQL_ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    pass


class JSONText(TypeDecorator):
    """Store JSON as TEXT for broad MySQL compatibility (no native JSON requirement)."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return json.loads(value)


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


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class VectorIndexModel(Base):
    __tablename__ = "vector_indexes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)

    chunking_strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    index_path: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        MYSQL_ENUM("BUILDING", "READY", "FAILED", name="vector_index_status"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class RagQueryModel(Base):
    __tablename__ = "rag_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[dict] = mapped_column(JSONText, nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class RagAnswerModel(Base):
    __tablename__ = "rag_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rag_query_id: Mapped[int] = mapped_column(Integer, ForeignKey("rag_queries.id"), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


