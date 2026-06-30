"""Diagnosis API - 薄弱点诊断.

使用统一响应格式和依赖注入。
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_user_id, get_response_meta
from app.api.response import success, ResponseMeta
from app.services.diagnosis_service import diagnosis_service
from app.api.utils import format_agent_result
from app.agents.diagnostician import diagnostician_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report")
async def get_diagnosis_report(
    user_id: str = Depends(get_current_user_id),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """获取薄弱点诊断报告.

    使用统一响应格式，包含请求追踪信息。
    """
    logger.info(f"Diagnosis: 生成诊断报告 - user={user_id}")

    raw_result = await diagnostician_agent.diagnose(user_id=user_id)
    result = format_agent_result(raw_result)

    return success(
        data={
            "user_id": user_id,
            "scores": result.get("radar_scores", {}),
            "weak_points": result.get("weak_points", []),
            "recommendations": result.get("study_plan", []),
        },
        message="诊断报告生成成功",
        meta=meta,
    )


@router.get("/practice")
async def get_recommended_practice(
    db: Session = Depends(get_db_session),
    user_id: str = Depends(get_current_user_id),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """获取针对性练习推荐."""
    logger.info(f"Diagnosis: 获取练习推荐 - user={user_id}")

    practices = await diagnosis_service.get_practice(db, user_id)

    if not practices:
        practices = [
            {"id": "p_default_001", "type": "专项练习", "title": "基础知识巩固练习", "count": 10},
        ]

    return success(
        data={"user_id": user_id, "practices": practices},
        message="获取练习推荐成功",
        meta=meta,
    )