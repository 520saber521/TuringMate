"""Thinking Trace API - 思维回放端点（已弃用）.

功能已下线，保留路由以保证 API 兼容性。
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ThinkingPathResponse(BaseModel):
    session_id: str
    path: Optional[dict] = None


class ThinkingReportResponse(BaseModel):
    user_id: str
    report: Optional[dict] = None


@router.post("/record", response_model=dict)
async def record_thinking_step():
    """[已弃用] 手动记录思考步骤 — 思维回放功能已下线。"""
    return {"deprecated": True, "message": "思维回放功能已下线"}


@router.get("/{session_id}/path", response_model=ThinkingPathResponse)
async def get_thinking_path(session_id: str):
    """[已弃用] 获取思考路径图。"""
    return ThinkingPathResponse(session_id=session_id, path=None)


@router.get("/{user_id}/report", response_model=ThinkingReportResponse)
async def get_thinking_report(user_id: str):
    """[已弃用] 获取思维成长报告。"""
    return ThinkingReportResponse(user_id=user_id, report=None)
