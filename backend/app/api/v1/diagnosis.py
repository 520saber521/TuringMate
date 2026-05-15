"""Diagnosis API - 薄弱点诊断.

基于 LangChain DiagnosticianAgent.
"""

import logging

from fastapi import APIRouter

from app.schemas.diagnosis import DiagnosisReportResponse
from app.agents.diagnostician import diagnostician_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report", response_model=DiagnosisReportResponse)
async def get_diagnosis_report(user_id: str = "user_001"):
    """获取薄弱点诊断报告.

    LangChain DiagnosticianAgent 分析用户的错题记录，
    结合知识图谱和 LLM 生成四科能力雷达图和弱点列表。
    """
    logger.info(f"Diagnosis: 生成诊断报告 - user={user_id}")

    result = await diagnostician_agent.diagnose(user_id=user_id)

    return DiagnosisReportResponse(
        user_id=user_id,
        scores=result.get("radar_scores", {}),
        weak_points=result.get("weak_points", []),
        recommendations=result.get("study_plan", []),
    )


@router.get("/practice")
async def get_recommended_practice(user_id: str = "user_001"):
    """获取针对性练习推荐."""
    logger.info(f"Diagnosis: 获取练习推荐 - user={user_id}")

    result = await diagnostician_agent.diagnose(user_id=user_id)

    # 从诊断报告的 study_plan 中提取练习项
    practices = []
    for plan in result.get("study_plan", []):
        for task in plan.get("tasks", []):
            practices.append({
                "id": f"p_{hash(task) % 10000:04d}",
                "type": "专项练习",
                "title": task,
                "count": 5,
            })

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
