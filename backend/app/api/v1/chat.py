"""Socratic guided chat API - 苏格拉底式引导对话.

基于 LangGraph SocraticTutorAgent 实现.
使用统一的 SSE 流式输出工具 (api.utils.create_sse_response).
"""

import logging

from fastapi import APIRouter

from app.schemas.chat import (
    ChatStartRequest,
    ChatStartResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.agents.socratic_tutor import socratic_tutor_agent
from app.api.utils import create_sse_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/start", response_model=ChatStartResponse)
async def start_guided_chat(body: ChatStartRequest):
    """开始引导对话.

    初始化 LangGraph SocraticTutor，创建对话会话，
    返回第一条引导提问（不直接给答案）。
    """
    logger.info(f"Chat: 启动引导对话 - question_id={body.question_id}")

    session_id = f"session_{body.question_id}_{body.user_id}"

    # 从数据库获取真实题目信息
    from app.services.question_service import question_service
    question_context = {
        "question_id": body.question_id,
        "subject": "数据结构",
        "knowledge_tags": ["链表", "指针操作"],
        "difficulty": 3,
    }
    q = await question_service.get_question(body.question_id)
    if q:
        question_context = {
            "question_id": q["id"],
            "subject": q["subject"],
            "knowledge_tags": q["knowledge_tags"],
            "difficulty": q["difficulty"],
        }

    result = await socratic_tutor_agent.generate_first_message(session_id, question_context)

    return ChatStartResponse(
        session_id=session_id,
        first_message=result["message"],
        stage=result["stage"],
    )


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(body: ChatMessageRequest):
    """发送用户消息，获取AI引导回复.

    LangGraph SocraticTutor 根据学生回复判断理解程度，
    通过状态机流转生成下一步引导。
    """
    logger.info(f"Chat: 收到消息 - session={body.session_id}, len={len(body.message)}")

    result = await socratic_tutor_agent.generate_response(
        session_id=body.session_id,
        user_message=body.message,
    )

    return ChatMessageResponse(
        session_id=body.session_id,
        content=result["message"],
        stage=result["stage"],
        hint_available=True,
    )


@router.post("/stream")
async def stream_chat_message(body: ChatMessageRequest):
    """流式引导对话 (SSE).

    使用 create_sse_response() 统一 SSE 格式和 headers，
    通过 LangGraph astream 流式返回 AI 引导内容。
    """
    logger.info(f"Chat: 流式对话 - session={body.session_id}")

    return create_sse_response(
        socratic_tutor_agent.stream_response(
            session_id=body.session_id,
            user_message=body.message,
        )
    )
