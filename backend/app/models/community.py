"""Community ORM Models."""
from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.models.database import Base


class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(String(32), primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(20), default="")
    tags = Column(JSON, default=list)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_reply_id = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Reply(Base):
    __tablename__ = "replies"

    id = Column(String(32), primary_key=True)
    content = Column(Text, nullable=False)
    discussion_id = Column(String(32), ForeignKey("discussions.id"), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    parent_reply_id = Column(String(32), nullable=True, index=True)
    like_count = Column(Integer, default=0)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiscussionLike(Base):
    __tablename__ = "discussion_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discussion_id = Column(String(32), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HotTopic(Base):
    __tablename__ = "hot_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, default="")
    discussion_ids = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
