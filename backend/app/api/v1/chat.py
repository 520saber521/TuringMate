"""Socratic guided chat API - 苏格拉底式引导对话.

使用统一响应格式和依赖注入。
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatStartRequest,
    ChatMessageRequest,
)
from app.api.deps import get_current_user_id, get_response_meta, get_db_session
from app.api.response import success, ResponseMeta
from app.api.utils import create_sse_response
from app.services.chat_service import chat_service
from app.services.question_service import question_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start")
async def start_guided_chat(
    body: ChatStartRequest,
    db: Session = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """开始引导对话.

    初始化对话会话，返回第一条引导提问。
    """
    logger.info(f"Chat: 启动引导对话 - question_id={body.question_id}")

    result = await chat_service.start_session(body.question_id, user_id)

    # 获取题目上下文
    q = await question_service.get_question(db, body.question_id)
    if q:
        result["question_context"] = {
            "subject": q["subject"],
            "knowledge_tags": q["knowledge_tags"],
            "difficulty": q["difficulty"],
        }

    return success(
        data=result,
        message="对话会话已启动",
        meta=meta,
    )


@router.post("/message")
async def send_chat_message(
    body: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """发送用户消息，获取AI引导回复."""
    logger.info(f"Chat: 收到消息 - session={body.session_id}")

    result = await chat_service.send_message(body.session_id, body.message)

    return success(
        data=result,
        message="消息处理成功",
        meta=meta,
    )


@router.post("/stream")
async def stream_chat_message(body: ChatMessageRequest):
    """流式引导对话 (SSE)."""
    logger.info(f"Chat: 流式对话 - session={body.session_id}")

    return create_sse_response(
        chat_service.stream_message(
            session_id=body.session_id,
            user_message=body.message,
        )
    )