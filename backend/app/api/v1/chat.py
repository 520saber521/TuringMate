"""Socratic guided chat API - 苏格拉底式引导对话."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import (
    ChatStartRequest,
    ChatStartResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)

router = APIRouter()


@router.post("/start", response_model=ChatStartResponse)
async def start_guided_chat(body: ChatStartRequest):
    """开始引导对话.

    初始化苏格拉底引导 Agent，创建对话会话，
    返回第一条引导提问（不直接给答案）。
    """
    # TODO: 调用 SocraticTutor Agent 启动对话
    return ChatStartResponse(
        session_id="session_mock_001",
        first_message="同学你好！看到这道题，你觉得它考查的核心知识点是什么呢？\n\n提示：可以想想单链表的遍历和删除操作有什么需要注意的地方~",
        stage="QUESTION",
    )


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(body: ChatMessageRequest):
    """发送用户消息，获取AI引导回复.

    苏格拉底 Agent 根据学生回复判断理解程度，
    生成下一步引导（反问/提示/确认/扩展），不直接给出答案。
    """
    # TODO: 调用 SocraticTutor Agent 处理回复
    return ChatMessageResponse(
        session_id=body.session_id,
        content="很好的思考方向！那我们进一步想一下：在遍历链表时，如果要删除当前结点，我们需要知道什么信息？\n\n💡 提示：想一想删除操作需要的前驱结点...",
        stage="HINT",
        hint_available=True,
    )


@router.post("/stream")
async def stream_chat_message(body: ChatMessageRequest):
    """流式引导对话 (SSE).

    通过 SSE 流式返回 AI 引导内容，
    前端逐字渲染提升交互体验。
    """

    async def generate():
        # TODO: 调用 SocraticTutor Agent 流式输出
        mock_response = ("让我们一步步来分析...\n\n"
                        "首先，这道题的关键在于**如何安全地删除链表中的结点**。\n\n"
                        "你想到的第一个步骤是什么？")
        for char in mock_response:
            yield f"data: {char}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
