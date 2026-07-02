"""add_knowledge_tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-11

Create knowledge_nodes and cross_subject_edges tables.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_nodes",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("subject", sa.String(20), nullable=False, index=True),
        sa.Column("category", sa.String(50), server_default=""),
        sa.Column("difficulty", sa.Integer(), server_default="1"),
        sa.Column("prerequisites", sa.JSON(), server_default="[]"),
        sa.Column("concept_explanation", sa.Text(), nullable=True),
        sa.Column("common_pitfalls", sa.JSON(), server_default="[]"),
        sa.Column("related_question_ids", sa.JSON(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_knowledge_nodes_subject", "knowledge_nodes", ["subject"])

    op.create_table(
        "cross_subject_edges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(20), nullable=False, index=True),
        sa.Column("target", sa.String(20), nullable=False, index=True),
        sa.Column("relation", sa.String(500), server_default=""),
    )


def downgrade() -> None:
    op.drop_table("cross_subject_edges")
    op.drop_table("knowledge_nodes")
