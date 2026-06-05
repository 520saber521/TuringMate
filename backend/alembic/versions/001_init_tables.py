"""init_tables

Revision ID: 001
Revises:
Create Date: 2026-05-28

Initial schema: users, questions, chat_sessions, mistakes, diagnosis_reports
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(100), unique=True, default=""),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("avatar", sa.String(255), default=""),
        sa.Column("target_school", sa.String(100), default=""),
        sa.Column("weak_subjects", mysql.JSON, default=list),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("subject", sa.String(20), nullable=False, index=True),
        sa.Column("knowledge_tags", mysql.JSON, default=list),
        sa.Column("difficulty", sa.Integer, default=3),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("image_url", sa.String(500), default=""),
        sa.Column("solution_steps", mysql.JSON, default=list),
        sa.Column("source_question_id", sa.String(32), nullable=True),
        sa.Column("variant_of", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("question_id", sa.String(32)),
        sa.Column("status", sa.String(20), default="active"),
        sa.Column("messages", mysql.JSON, default=list),
        sa.Column("current_stage", sa.String(20), default="QUESTION"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "mistakes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("question_id", sa.String(32), sa.ForeignKey("questions.id"), nullable=True),
        sa.Column("user_answer", sa.Text),
        sa.Column("error_step", sa.Integer),
        sa.Column("error_type", sa.String(50), default=""),
        sa.Column("knowledge_tags", mysql.JSON, default=list),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "diagnosis_reports",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("user_id", sa.String(32), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("scores", mysql.JSON),
        sa.Column("weak_points", mysql.JSON, default=list),
        sa.Column("recommendations", mysql.JSON, default=list),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("diagnosis_reports")
    op.drop_table("mistakes")
    op.drop_table("chat_sessions")
    op.drop_table("questions")
    op.drop_table("users")
