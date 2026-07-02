"""add_question_fields_and_mistake_reviewed

Revision ID: 002
Revises: 001
Create Date: 2026-06-11

Add year, exam_paper, chapter_order, source_type, ai_analysis to questions.
Add reviewed, reviewed_at to mistakes.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("year", sa.Integer(), nullable=True))
    op.add_column("questions", sa.Column("exam_paper", sa.String(100), server_default=""))
    op.add_column("questions", sa.Column("chapter_order", sa.Integer(), nullable=True))
    op.add_column("questions", sa.Column("source_type", sa.String(20), server_default="manual"))
    op.add_column("questions", sa.Column("ai_analysis", sa.Text(), nullable=True))
    op.create_index("ix_questions_year", "questions", ["year"])

    op.add_column("mistakes", sa.Column("reviewed", sa.Integer(), server_default="0"))
    op.add_column("mistakes", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("mistakes", "reviewed_at")
    op.drop_column("mistakes", "reviewed")

    op.drop_index("ix_questions_year", table_name="questions")
    op.drop_column("questions", "ai_analysis")
    op.drop_column("questions", "source_type")
    op.drop_column("questions", "chapter_order")
    op.drop_column("questions", "exam_paper")
    op.drop_column("questions", "year")
