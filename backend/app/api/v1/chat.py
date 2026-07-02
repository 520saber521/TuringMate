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
    try:
        q = await question_service.get_question(body.question_id)
        if q:
            question_context = {
                "question_id": q["id"],
                "subject": q["subject"],
                "knowledge_tags": q["knowledge_tags"],
                "difficulty": q["difficulty"],
            }
    except Exception as e:
        # 数据库不可用时使用默认上下文，不影响主流程
        logger.warning(f"Chat: 获取题目上下文失败，使用默认 - {e}")

    # 尝试调用 LangGraph Agent，失败时使用降级方案
    try:
        result = await socratic_tutor_agent.generate_first_message(session_id, question_context)
        return ChatStartResponse(
            session_id=session_id,
            first_message=result["message"],
            stage=result["stage"],
        )
    except Exception as e:
        # LLM 不可用时（API Key 未配置、网络问题等），返回友好的降级响应
        logger.error(f"Chat: Agent 调用失败，使用降级方案 - {e}")
        from app.config import settings
        model_name = settings.DEFAULT_LLM_MODEL or "deepseek"
        # 降级方案：生成苏格拉底式开场白
        # 根据难度和知识点动态生成引导
        difficulty_word = "简单" if question_context.get("difficulty", 3) <= 2 else ("有一定挑战" if question_context.get("difficulty", 3) <= 4 else "颇具挑战")
        subject = question_context.get("subject", "数据结构")
        tags = question_context.get("knowledge_tags", [])
        tags_text = "、".join(tags) if tags else "核心算法"
        fallback_message = (
            f"你好！我是图灵老师 👋\n\n"
            f"我们一起来分析这道**{difficulty_word}**的 {subject} 题目。\n\n"
            f"📌 **第一步**：先别急着动手。请你用一句话告诉我：\n"
            f"1. **题目要求你做什么**？\n"
            f"2. **给了你什么条件**？\n\n"
            f"把这道题用你自己的话**复述一遍**给我听，我们就从这里开始 ✨\n\n"
            f"💡 *小提示：这题涉及 {tags_text}，你可以先想想这些概念哦~*"
        )
        return ChatStartResponse(
            session_id=session_id,
            first_message=fallback_message,
            stage="question",
        )


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(body: ChatMessageRequest):
    """发送用户消息，获取AI引导回复.

    LangGraph SocraticTutor 根据学生回复判断理解程度，
    通过状态机流转生成下一步引导。
    """
    logger.info(f"Chat: 收到消息 - session={body.session_id}, len={len(body.message)}")

    # 尝试调用 Agent，失败时使用降级方案
    try:
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
    except Exception as e:
        # LLM 不可用时返回苏格拉底式降级响应
        logger.error(f"Chat: Agent 调用失败，使用降级方案 - {e}")
        # 根据用户回答长度动态调整
        msg = body.message.strip()
        msg_preview = msg[:30] + "..." if len(msg) > 30 else msg
        fallback_content = (
            f"收到你的回答啦！📝\n\n"
            f"> {msg_preview}\n\n"
            f"很好，我们继续往下走 👇\n\n"
            f"🤔 **思考一下**：\n"
            f"- 你刚才提到的关键概念是什么？\n"
            f"- 接下来你打算**怎么做**？\n"
            f"- 有没有可能存在**另一种思路**？\n\n"
            f"把你的想法告诉我，我们一起把它理清楚 ✨"
        )
        return ChatMessageResponse(
            session_id=body.session_id,
            content=fallback_content,
            stage="guidance",
            hint_available=True,
        )


@router.post("/stream")
async def stream_chat_message(body: ChatMessageRequest):
    """流式引导对话 (SSE).

    使用 create_sse_response() 统一 SSE 格式和 headers，
    通过 LangGraph astream 流式返回 AI 引导内容。
    """
    logger.info(f"Chat: 流式对话 - session={body.session_id}")

    # 流式响应使用降级方案：直接 yield 友好提示，避免 SSE 中断
    async def fallback_stream():
        from app.config import settings
        model_name = settings.DEFAULT_LLM_MODEL or "deepseek"
        text = (
            f"我已收到你的消息。\n\n"
            f"> 💡 当前使用模型：`{model_name}`，如需 AI 引导请配置对应的 API Key。"
        )
        for ch in text:
            yield f"data: {ch}\n\n"
        yield "data: [DONE]\n\n"

    try:
        # 尝试创建一个简单的流
        return create_sse_response(
            socratic_tutor_agent.stream_response(
                session_id=body.session_id,
                user_message=body.message,
            )
        )
    except Exception as e:
        logger.error(f"Chat: 流式调用失败，使用降级 - {e}")
        from fastapi.responses import StreamingResponse
        return StreamingResponse(fallback_stream(), media_type="text/event-stream")
