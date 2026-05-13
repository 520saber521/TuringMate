"""Diagnosis ORM Models."""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class Mistake(Base):
    __tablename__ = "mistakes"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), nullable=False)
    question_id = Column(String(32))
    user_answer = Column(Text)
    error_step = Column(Integer)
    knowledge_tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiagnosisReport(Base):
    __tablename__ = "diagnosis_reports"

    id = Column(String(32), primary_key=True)
    user_id = Column(String(32), nullable=False)
    scores = Column(JSON)  # {ds: 72, co: 65, os: 78, cn: 58}
    weak_points = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
