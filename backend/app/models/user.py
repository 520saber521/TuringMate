"""User ORM Model."""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.sql import func
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True)
    name = Column(String(50), nullable=False)
    avatar = Column(String(255), default="")
    target_school = Column(String(100), default="")
    weak_subjects = Column(String(255), default="")  # JSON array string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
