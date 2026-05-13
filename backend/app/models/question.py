"""Question ORM Model."""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(32), primary_key=True)
    subject = Column(String(20), nullable=False)  # 数据结构/计组/OS/网络
    knowledge_tags = Column(JSON, default=list)
    difficulty = Column(Integer, default=3)  # 1-5
    content = Column(Text, nullable=False)
    image_url = Column(String(500), default="")
    solution_steps = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
