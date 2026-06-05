"""Diagnosis ORM Models."""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String(32), ForeignKey("questions.id"), nullable=True)
    user_answer = Column(Text)
    error_step = Column(Integer)
    error_type = Column(String(50), default="")
    knowledge_tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="mistakes")
    question = relationship("Question", back_populates="mistakes")


class DiagnosisReport(Base):
    __tablename__ = "diagnosis_reports"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    scores = Column(JSON)
    weak_points = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diagnosis_reports")
