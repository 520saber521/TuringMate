"""Emotion & State API — 情绪感知与状态调节端点.

POST /api/v1/emotion/detect          — 检测消息中的情绪
GET  /api/v1/emotion/:session/state  — 获取会话情绪状态
GET  /api/v1/emotion/:session/events — 获取情绪事件日志
POST /api/v1/emotion/:session/reset  — 重置会话状态
"""

import logging
from fastapi import APIRouter

from app.agents.emotion_detector import emotion_detector

logger = logging.getLogger(__name__)
router = APIRouter()


class DetectRequest(BaseModel):
    message: str
    session_id: str


@router.post("/detect")
async def detect_emotion(body: DetectRequest):
    """检测消息情绪并返回教学策略建议."""
    result = emotion_detector.detect(body.message, body.session_id)
    prompt_override = emotion_detector.get_mode_prompt_override(body.session_id)
    return {
        **result.model_dump(),
        "prompt_override": prompt_override,
        "current_state": emotion_detector.get_current_state(body.session_id),
    }


@router.get("/{session_id}/state")
async def get_emotion_state(session_id: str):
    """获取当前会话的情绪状态快照."""
    return emotion_detector.get_current_state(session_id)


@router.get("/{session_id}/events")
async def get_emotion_events(session_id: str):
    """获取会话的情绪事件日志."""
    return {"events": emotion_detector.get_session_events(session_id)}


@router.post("/{session_id}/reset")
async def reset_emotion_session(session_id: str):
    """重置会话状态."""
    emotion_detector.reset_session(session_id)
    return {"status": "reset"}
