"""add document_chunks and vector_indexes

Revision ID: 3d2a9e12c1a7
Revises: 089d84553cd8
Create Date: 2026-01-18
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import mysql


revision: str = "3d2a9e12c1a7"
down_revision: Union[str, None] = "089d84553cd8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "vector_indexes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("chunking_strategy", sa.String(length=50), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("index_path", sa.Text(), nullable=False),
        sa.Column("status", mysql.ENUM("BUILDING", "READY", "FAILED"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("vector_indexes")
    op.drop_table("document_chunks")


