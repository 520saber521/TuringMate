"""Learning Path API — 动态学习路径规划器端点.

POST /api/v1/learning-path/generate   — 生成学习路径
POST /api/v1/learning-path/adjust    — 动态调整路径
GET  /api/v1/learning-path/:plan_id  — 获取路径详情
"""

import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.learning_path_planner import learning_path_planner
from app.schemas.learning_path import StudentProfile
from app.api.utils import format_agent_result

logger = logging.getLogger(__name__)
router = APIRouter()


class GeneratePathRequest(BaseModel):
    user_id: str
    target_score: int = 360
    target_school: str = ""
    current_level: str = "intermediate"
    available_days: int = 90
    daily_hours: float = 4.0
    weak_subjects: list[str] = []
    strong_subjects: list[str] = []


@router.post("/generate")
async def generate_learning_path(body: GeneratePathRequest):
    """生成动态学习路径."""
    logger.info(f"LearningPath: 生成路径 - user={body.user_id}, target={body.target_score}")
    
    profile = StudentProfile(
        user_id=body.user_id,
        target_score=body.target_score,
        target_school=body.target_school,
        current_level=body.current_level,
        available_days=body.available_days,
        daily_hours=body.daily_hours,
        weak_subjects=body.weak_subjects,
        strong_subjects=body.strong_subjects,
    )
    
    result = await learning_path_planner.generate_path(profile)
    return format_agent_result(result)


class AdjustPathRequest(BaseModel):
    plan_id: str
    trigger_type: str
    new_diagnosis: dict | None = None
    feedback: str = ""


@router.post("/adjust")
async def adjust_learning_path(body: AdjustPathRequest):
    """动态调整已有学习路径."""
    result = await learning_path_planner.adjust_path(
        body.plan_id, body.trigger_type,
        body.new_diagnosis, body.feedback,
    )
    return format_agent_result(result)
