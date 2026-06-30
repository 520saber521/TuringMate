"""Question parsing API - 图片/文本题目识别.

使用统一响应格式和依赖注入。
"""

import os
import uuid
import tempfile
import logging

from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_response_meta, get_optional_user_id, get_db_session
from app.api.response import success, ResponseMeta
from app.agents.question_parser import question_parser_agent
from app.api.utils import format_agent_result
from app.services.question_service import question_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/parse")
async def parse_question_image(
    image: UploadFile = File(...),
    user_id: str | None = Depends(get_optional_user_id),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """上传图片，识别并解析题目内容."""
    logger.info(f"Question: 解析题目图片 - user={user_id}")

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

        return success(
            data={
                "question_id": result.get("question_id") or f"q_{uuid.uuid4().hex[:8]}",
                "subject": result.get("subject", "未识别"),
                "knowledge_tags": result.get("knowledge_tags", []),
                "difficulty": result.get("difficulty", 3),
                "content": result.get("content", ""),
                "image_url": f"/uploads/{image.filename}",
            },
            message="题目解析成功",
            meta=meta,
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/subjects")
async def get_subject_list(
    meta: ResponseMeta = Depends(get_response_meta),
):
    """获取支持的科目列表."""
    return success(
        data={
            "subjects": [
                {"id": "ds", "name": "数据结构", "icon": "Tree"},
                {"id": "co", "name": "计组", "icon": "Cpu"},
                {"id": "os", "name": "操作系统", "icon": "Monitor"},
                {"id": "cn", "name": "计算机网络", "icon": "Globe"},
            ]
        },
        message="获取科目列表成功",
        meta=meta,
    )


@router.get("/list")
async def list_questions(
    db: Session = Depends(get_db_session),
    subject: str | None = Query(default=None),
    difficulty: int | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """获取题目列表."""
    questions = await question_service.list_questions(
        db, subject=subject, difficulty=difficulty, limit=limit
    )

    return success(
        data=questions,
        message="获取题目列表成功",
        meta=meta,
    )