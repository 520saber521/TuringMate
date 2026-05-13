"""Diagnosis API - 薄弱点诊断."""
from fastapi import APIRouter
from app.schemas.diagnosis import DiagnosisReportResponse

router = APIRouter()


@router.get("/report", response_model=DiagnosisReportResponse)
async def get_diagnosis_report(user_id: str = "user_001"):
    """获取薄弱点诊断报告.

    Diagnostician Agent 分析用户的错题记录，
    结合 RAG 检索关联知识点，生成四科能力雷达图和弱点列表。
    """
    # TODO: 调用 Diagnostician Agent 生成报告
    return DiagnosisReportResponse(
        user_id=user_id,
        scores={
            "数据结构": 72,
            "计组": 65,
            "操作系统": 78,
            "网络": 58,
        },
        weak_points=[
            {
                "subject": "计算机网络",
                "topic": "TCP拥塞控制",
                "score": 45,
                "description": "慢开始、拥塞避免、快重传的阈值变化规律掌握不牢",
            },
            {
                "subject": "计算机组成原理",
                "topic": "流水线冒险",
                "score": 52,
                "description": "数据冒险、控制冒险的解决策略混淆",
            },
        ],
        recommendations=[
            {"type": "专项练习", "title": "TCP 拥塞控制专项训练", "count": 10},
            {"type": "知识点回顾", "title": "流水线冒险机制详解", "count": 1},
        ],
    )


@router.get("/practice")
async def get_recommended_practice(user_id: str = "user_001"):
    """获取针对性练习推荐."""
    # TODO: 基于诊断报告推荐题目
    return {
        "user_id": user_id,
        "practices": [
            {
                "id": "p_001",
                "subject": "计算机网络",
                "topic": "TCP拥塞控制",
                "difficulty": 3,
                "recommended_reason": "该知识点正确率低于50%，需要重点突破",
            },
        ],
    }
