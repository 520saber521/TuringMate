"""Mistake Book API - 错题本."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.diagnosis import Mistake
from app.crud.diagnosis import diagnosis_crud
from app.api.v1.deps import get_current_user

router = APIRouter()


class MistakeItem(BaseModel):
    id: str
    question_id: str | None
    user_answer: str | None
    error_type: str
    knowledge_tags: list[str] = []
    reviewed: int = 0
    reviewed_at: str | None = None
    created_at: str | None = None

    class Config:
        from_attributes = True


class MistakeListResponse(BaseModel):
    items: list[MistakeItem]
    total: int


# ── 错题 CRUD ──

@router.get("", response_model=MistakeListResponse)
def list_mistakes(
    subject: str | None = Query(None),
    reviewed: int | None = Query(None),
    limit: int = Query(50, le=200),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Mistake).filter(Mistake.user_id == user.id)
    if reviewed is not None:
        q = q.filter(Mistake.reviewed == reviewed)

    # 按科目筛选（通过关联的 question 表）
    if subject:
        from app.models.question import Question
        q = q.join(Question, Mistake.question_id == Question.id).filter(
            Question.subject == subject
        )

    total = q.count()
    items = q.order_by(Mistake.created_at.desc()).limit(limit).all()

    return MistakeListResponse(
        items=[
            MistakeItem(
                id=m.id,
                question_id=m.question_id,
                user_answer=m.user_answer,
                error_type=m.error_type or "",
                knowledge_tags=m.knowledge_tags or [],
                reviewed=m.reviewed or 0,
                reviewed_at=m.reviewed_at.isoformat() if m.reviewed_at else None,
                created_at=m.created_at.isoformat() if m.created_at else None,
            )
            for m in items
        ],
        total=total,
    )


class AddMistakeRequest(BaseModel):
    question_id: str
    user_answer: str | None = None
    error_type: str = ""
    knowledge_tags: list[str] = []


@router.post("", status_code=201)
def add_mistake(
    body: AddMistakeRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 检查是否已存在
    existing = (
        db.query(Mistake)
        .filter(Mistake.user_id == user.id, Mistake.question_id == body.question_id)
        .first()
    )
    if existing:
        return {"id": existing.id, "message": "已存在于错题本"}

    m = diagnosis_crud.create_mistake(
        db,
        user_id=user.id,
        question_id=body.question_id,
        user_answer=body.user_answer,
        error_type=body.error_type,
        knowledge_tags=body.knowledge_tags,
    )
    return {"id": m.id, "message": "已添加到错题本"}


@router.put("/{mistake_id}/review")
def mark_reviewed(
    mistake_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = db.query(Mistake).filter(
        Mistake.id == mistake_id, Mistake.user_id == user.id
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    m.reviewed = 1
    m.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    return {"id": m.id, "reviewed": True}


@router.put("/{mistake_id}/unreview")
def mark_unreviewed(
    mistake_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = db.query(Mistake).filter(
        Mistake.id == mistake_id, Mistake.user_id == user.id
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    m.reviewed = 0
    m.reviewed_at = None
    db.commit()
    return {"id": m.id, "reviewed": False}


@router.delete("/{mistake_id}")
def delete_mistake(
    mistake_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = db.query(Mistake).filter(
        Mistake.id == mistake_id, Mistake.user_id == user.id
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    db.delete(m)
    db.commit()
    return {"id": mistake_id, "deleted": True}
