"""Community schemas."""
from datetime import datetime
from pydantic import BaseModel, field_validator


def _dt_to_str(v):
    if isinstance(v, datetime):
        return v.isoformat()
    return v


class DiscussionCreate(BaseModel):
    title: str
    content: str
    subject: str = ""
    tags: list[str] = []


class DiscussionItem(BaseModel):
    id: str
    title: str
    content: str
    user_id: str
    subject: str = ""
    tags: list[str] = []
    like_count: int = 0
    reply_count: int = 0
    is_pinned: bool = False
    is_resolved: bool = False
    created_at: str | None = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="before")
    @classmethod
    def coerce_created_at(cls, v):
        return _dt_to_str(v)


class DiscussionListResponse(BaseModel):
    items: list[DiscussionItem]
    total: int
    page: int
    page_size: int


class ReplyCreate(BaseModel):
    content: str
    parent_reply_id: str | None = None


class ReplyItem(BaseModel):
    id: str
    content: str
    discussion_id: str
    user_id: str
    parent_reply_id: str | None = None
    like_count: int = 0
    is_accepted: bool = False
    created_at: str | None = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="before")
    @classmethod
    def coerce_created_at(cls, v):
        return _dt_to_str(v)


class DiscussionDetail(BaseModel):
    id: str
    title: str
    content: str
    user_id: str
    subject: str = ""
    tags: list[str] = []
    like_count: int = 0
    reply_count: int = 0
    is_pinned: bool = False
    is_resolved: bool = False
    resolved_reply_id: str | None = None
    created_at: str | None = None
    replies: list[ReplyItem] = []

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="before")
    @classmethod
    def coerce_created_at(cls, v):
        return _dt_to_str(v)


class LikeResponse(BaseModel):
    liked: bool
    like_count: int


class HotTopicItem(BaseModel):
    id: int
    title: str
    summary: str
    discussion_ids: list[str] = []
    created_at: str | None = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="before")
    @classmethod
    def coerce_created_at(cls, v):
        return _dt_to_str(v)
