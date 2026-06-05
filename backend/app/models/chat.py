"""Chat Session ORM Model."""
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String(32))
    status = Column(String(20), default="active")
    messages = Column(JSON, default=list)
    current_stage = Column(String(20), default="QUESTION")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="chat_sessions")
