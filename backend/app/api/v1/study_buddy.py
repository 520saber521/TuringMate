"""Study Buddy API — AI 研友多角色系统端点.

POST /api/v1/buddy/start           — 启动学习小组会话
POST /api/v1/buddy/:session/chat   — 继续讨论
GET  /api/v1/buddy/:session         — 获取会话状态
POST /api/v1/buddy/:session/end     — 结束会话
"""

import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.study_buddy import study_buddy_agent
from app.schemas.emotion import StudyBuddyConfig, StudyBuddyRole
from app.api.utils import format_agent_result

logger = logging.getLogger(__name__)
router = APIRouter()


class StartBuddySessionRequest(BaseModel):
    roles: list[str] = ["scholar"]       # scholar / striver / discussant
    topic: str = ""                       # 讨论主题
    mode: str = "debate"                  # debate / collaborative / quiz
    difficulty: str = "medium"


@router.post("/start")
async def start_buddy_session(body: StartBuddySessionRequest):
    """启动 AI 学习小组会话."""
    role_enums = []
    for r in body.roles:
        try:
            role_enums.append(StudyBuddyRole(r))
        except ValueError:
            pass
    
    config = StudyBuddyConfig(
        roles=role_enums or [StudyBuddyRole.SCHOLAR],
        topic=body.topic,
        mode=body.mode,
        difficulty=body.difficulty,
    )
    
    result = await study_buddy_agent.start_session(config)
    return format_agent_result(result)


class ChatMessage(BaseModel):
    message: str


@router.post("/{session_id}/chat")
async def buddy_chat(session_id: str, body: ChatMessage):
    """继续小组讨论."""
    result = await study_buddy_agent.continue_discussion(
        session_id=session_id,
        user_message=body.message,
    )
    return format_agent_result(result)


@router.get("/{session_id}")
async def get_buddy_session(session_id: str):
    """获取会话状态."""
    return study_buddy_agent.get_session_state(session_id)


@router.post("/{session_id}/end")
async def end_buddy_session(session_id: str):
    """结束会话并获取总结."""
    result = await study_buddy_agent.end_session(session_id)
    return format_agent_result(result)
