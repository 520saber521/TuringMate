"""Socratic guided chat API - 苏格拉底式引导对话.

基于 LangGraph SocraticTutorAgent 实现。
"""

import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import (
    ChatStartRequest,
    ChatStartResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.agents.socratic_tutor import socratic_tutor_agent

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

    # 构建题目上下文（TODO: 从数据库获取真实题目信息）
    question_context = {
        "question_id": body.question_id,
        "subject": "数据结构",
        "knowledge_tags": ["链表", "指针操作"],
        "difficulty": 3,
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
        hint_available=True,  # LangGraph Agent 总是可提供提示
    )


@router.post("/stream")
async def stream_chat_message(body: ChatMessageRequest):
    """流式引导对话 (SSE).

    通过 LangGraph astream 流式返回 AI 引导内容，
    前端逐字渲染提升交互体验。
    """
    logger.info(f"Chat: 流式对话 - session={body.session_id}")

    async def generate():
        try:
            async for chunk in socratic_tutor_agent.stream_response(
                session_id=body.session_id,
                user_message=body.message,
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Chat: 流式输出异常 - {e}")
            yield f"data: [错误] 生成回复时出现问题，请重试\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
