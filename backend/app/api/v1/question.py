"""Question API - 题库查询与题目识别."""
import os
import uuid
import tempfile

from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.question import question_crud
from app.schemas.question import (
    QuestionParseResponse, QuestionItem, QuestionDetail,
    QuestionListResponse,
)
from app.agents.question_parser import question_parser_agent
from app.api.utils import format_agent_result

router = APIRouter()

SUBJECT_MAP = {
    "ds": "数据结构", "co": "计组", "os": "操作系统", "cn": "计算机网络",
    "数据结构": "数据结构", "计组": "计组", "操作系统": "操作系统", "计算机网络": "计算机网络",
}


# ── 题库查询端点 ──

@router.get("/questions", response_model=QuestionListResponse)
def list_questions(
    subject: str | None = Query(None, description="科目: ds/co/os/cn 或中文名"),
    tag: str | None = Query(None, description="知识点标签"),
    difficulty: int | None = Query(None, ge=1, le=5),
    year: int | None = Query(None, description="年份"),
    keyword: str | None = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = question_crud.list_paginated(
        db, subject=subject, tag=tag, difficulty=difficulty,
        year=year, keyword=keyword, page=page, page_size=page_size,
    )
    return QuestionListResponse(
        items=[QuestionItem.model_validate(it) for it in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/questions/search", response_model=list[QuestionItem])
def search_questions(
    q: str = Query(..., description="搜索关键词"),
    subject: str | None = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    items = question_crud.search_by_keywords(db, q=q, subject=subject, limit=limit)
    return [QuestionItem.model_validate(it) for it in items]


@router.get("/questions/years")
def get_years(db: Session = Depends(get_db)):
    return {"years": question_crud.get_distinct_years(db)}


@router.get("/questions/by-year/{year}", response_model=QuestionListResponse)
def get_by_year(
    year: int,
    subject: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = question_crud.get_by_year(db, year, subject=subject, page=page, page_size=page_size)
    return QuestionListResponse(
        items=[QuestionItem.model_validate(it) for it in items],
        total=total, page=page, page_size=page_size,
    )


@router.get("/questions/tags")
def get_tags(subject: str | None = Query(None), db: Session = Depends(get_db)):
    return {"tags": question_crud.get_distinct_tags(db, subject=subject)}


@router.get("/questions/{question_id}", response_model=QuestionDetail)
def get_question(question_id: str, db: Session = Depends(get_db)):
    q = question_crud.get_by_id(db, question_id)
    if not q:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="题目不存在")
    return QuestionDetail.model_validate(q)


# ── 题目识别端点 (保留原有功能) ──

@router.post("/parse", response_model=QuestionParseResponse)
async def parse_question_image(image: UploadFile = File(...)):
    ext = os.path.splitext(image.filename or "upload.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"turingmate_q_{filename}")

    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)

        raw_result = await question_parser_agent.parse_image(image_url=file_path)
        result = format_agent_result(raw_result)

        return QuestionParseResponse(
            question_id=result.get("question_id") or f"q_{uuid.uuid4().hex[:8]}",
            subject=result.get("subject", "未识别"),
            knowledge_tags=result.get("knowledge_tags", []),
            difficulty=result.get("difficulty", 3),
            content=result.get("content", ""),
            image_url=f"/uploads/{image.filename}",
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/subjects")
async def get_subject_list():
    return {
        "subjects": [
            {"id": "ds", "name": "数据结构", "icon": "Tree"},
            {"id": "co", "name": "计组", "icon": "Cpu"},
            {"id": "os", "name": "操作系统", "icon": "Monitor"},
            {"id": "cn", "name": "计算机网络", "icon": "Globe"},
        ]
    }
