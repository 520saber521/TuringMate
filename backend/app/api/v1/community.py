"""Community API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.crud.community import community_crud
from app.schemas.community import (
    DiscussionCreate, DiscussionItem, DiscussionListResponse,
    DiscussionDetail, ReplyCreate, ReplyItem, LikeResponse, HotTopicItem,
)

router = APIRouter()


@router.get("/discussions", response_model=DiscussionListResponse)
def list_discussions(
    subject: str = "",
    tag: str = "",
    sort: str = "latest",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items, total = community_crud.list_discussions(
        db, subject=subject, tag=tag, sort=sort, page=page, page_size=page_size
    )
    return DiscussionListResponse(
        items=[DiscussionItem.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/discussions", response_model=DiscussionItem)
def create_discussion(
    body: DiscussionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    disc = community_crud.create_discussion(
        db, user_id=user.id, title=body.title, content=body.content,
        subject=body.subject, tags=body.tags,
    )
    return DiscussionItem.model_validate(disc)


@router.get("/discussions/{discussion_id}", response_model=DiscussionDetail)
def get_discussion(discussion_id: str, db: Session = Depends(get_db)):
    disc = community_crud.get_discussion(db, discussion_id)
    if not disc:
        raise HTTPException(status_code=404, detail="帖子不存在")
    replies = community_crud.list_replies(db, discussion_id)
    result = DiscussionDetail.model_validate(disc)
    result.replies = [ReplyItem.model_validate(r) for r in replies]
    return result


@router.post("/discussions/{discussion_id}/replies", response_model=ReplyItem)
def create_reply(
    discussion_id: str,
    body: ReplyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    disc = community_crud.get_discussion(db, discussion_id)
    if not disc:
        raise HTTPException(status_code=404, detail="帖子不存在")
    reply = community_crud.create_reply(
        db, user_id=user.id, discussion_id=discussion_id,
        content=body.content, parent_reply_id=body.parent_reply_id,
    )
    return ReplyItem.model_validate(reply)


@router.post("/discussions/{discussion_id}/like", response_model=LikeResponse)
def toggle_like(
    discussion_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    disc = community_crud.get_discussion(db, discussion_id)
    if not disc:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return community_crud.toggle_like(db, discussion_id, user.id)


@router.post("/replies/{reply_id}/accept", response_model=ReplyItem)
def accept_reply(
    reply_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reply = community_crud.accept_reply(db, reply_id)
    if not reply:
        raise HTTPException(status_code=404, detail="回复不存在")
    return ReplyItem.model_validate(reply)


@router.get("/hot-topics", response_model=list[HotTopicItem])
def get_hot_topics(limit: int = Query(5, ge=1, le=10), db: Session = Depends(get_db)):
    topics = community_crud.get_hot_topics(db, limit=limit)
    return [HotTopicItem.model_validate(t) for t in topics]
