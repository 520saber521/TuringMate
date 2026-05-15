"""Diagnosis API - 薄弱点诊断."""

import logging

from fastapi import APIRouter

from app.schemas.diagnosis import DiagnosisReportResponse
from app.agents.diagnostician import diagnostician

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report", response_model=DiagnosisReportResponse)
async def get_diagnosis_report(user_id: str = "user_001"):
    """获取薄弱点诊断报告.

    Diagnostician Agent 分析用户的错题记录，
    结合 LLM 生成四科能力雷达图和弱点列表。
    """
    logger.info(f"Diagnosis: 生成诊断报告 - user={user_id}")

    result = await diagnostician.generate_report(user_id)

    return DiagnosisReportResponse(
        user_id=result.get("user_id", user_id),
        scores=result.get("scores", {}),
        weak_points=result.get("weak_points", []),
        recommendations=result.get("recommendations", []),
    )


@router.get("/practice")
async def get_recommended_practice(user_id: str = "user_001"):
    """获取针对性练习推荐."""
    logger.info(f"Diagnosis: 获取练习推荐 - user={user_id}")

    result = await diagnostician.generate_report(user_id)

    # 从推荐中提取练习项
    practices = []
    for rec in result.get("recommendations", []):
        practices.append({
            "id": f"p_{hash(rec.get('title', '')) % 10000:04d}",
            "type": rec.get("type", "专项练习"),
            "title": rec.get("title", "推荐练习"),
            "count": rec.get("count", 5),
        })

    # 如果推荐为空，添加默认推荐
    if not practices:
        practices = [
            {
                "id": "p_default_001",
                "type": "专项练习",
                "title": "基础知识巩固练习",
                "count": 10,
            },
        ]

    return {
        "user_id": user_id,
        "practices": practices,
    }
