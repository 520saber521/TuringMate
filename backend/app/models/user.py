"""User ORM Model."""
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, default="")
    name = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), default="")
    target_school = Column(String(100), default="")
    weak_subjects = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user")
    mistakes = relationship("Mistake", back_populates="user")
    diagnosis_reports = relationship("DiagnosisReport", back_populates="user")
