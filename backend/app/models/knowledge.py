"""Knowledge Graph ORM Models."""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(20), nullable=False, index=True)
    category = Column(String(50), default="")
    difficulty = Column(Integer, default=1)
    prerequisites = Column(JSON, default=list)
    concept_explanation = Column(Text, nullable=True)
    common_pitfalls = Column(JSON, default=list)
    related_question_ids = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CrossSubjectEdge(Base):
    __tablename__ = "cross_subject_edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(20), nullable=False, index=True)
    target = Column(String(20), nullable=False, index=True)
    relation = Column(String(500), default="")
