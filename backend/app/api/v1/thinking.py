"""Thinking Trace API — 思维过程可视化回放端点.

GET  /api/v1/thinking/:session_id/path     — 获取思考路径图
GET  /api/v1/thinking/:user_id/report    — 获取思维成长报告
POST /api/v1/thinking/record              — 手动记录一步思考
"""

import logging
from fastapi import APIRouter

from app.agents.thinking_tracer import create_tracer
from app.schemas.thinking import StepType

logger = logging.getLogger(__name__)
router = APIRouter()

# 内存缓存（生产环境应使用数据库）
_tracers: dict[str, object] = {}


@router.post("/record")
async def record_thinking_step(
    session_id: str,
    content: str,
    role: str = "user",
    step_type: str = "input",
    question_id: str = "",
    user_id: str = "",
):
    """记录一步思考."""
    key = f"{session_id}:{question_id}"
    if key not in _tracers:
        _tracers[key] = create_tracer(session_id, question_id or "", user_id or "")
    
    tracer = _tracers[key]
    try:
        stype = StepType(step_type)
    except ValueError:
        stype = StepType.INPUT
    
    step = tracer.record_step(content, role, stype)
    return {"step": step.model_dump(), "total_steps": len(tracer._steps)}


@router.get("/{session_id}/path")
async def get_thinking_path(session_id: str, question_id: str = ""):
    """获取完整思考路径图."""
    key = f"{session_id}:{question_id}"
    tracer = _tracers.get(key)
    if not tracer:
        return {"error": "No thinking session found", "path": None}
    return {"path": tracer.build_path()}


@router.get("/{user_id}/report")
async def get_thinking_report(user_id: str):
    """获取思维成长报告."""
    # 收集所有该用户的历史路径
    historical = []
    for key, t in _tracers.items():
        if hasattr(t, 'user_id') and t.user_id == user_id:
            try:
                historical.append(t.build_path())
            except Exception:
                pass
    
    # 用最新的 tracer 生成报告
    sample_tracer = create_tracer(f"report_{user_id}", "", user_id)
    report = sample_tracer.generate_weekly_report(historical)
    return report
