"""Chat Session ORM Model."""
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), nullable=False)
    question_id = Column(String(32))
    status = Column(String(20), default="active")  # active/completed/abandoned
    messages = Column(JSON, default=list)  # [{role, content, timestamp, stage}]
    current_stage = Column(String(20), default="QUESTION")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
