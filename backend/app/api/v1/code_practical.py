"""Code Practical API — 「代码即题目」实战模块端点.

GET  /api/v1/code/challenges             — 列出代码挑战题
GET  /api/v1/code/challenges/:id         — 获取挑战详情
POST /api/v1/code/execute                 — 执行学生代码
POST /api/v1/code/:id/submit             — 提交答案
GET  /api/v1/code/:id/explanation         — 查看解析
"""

import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.code_practical import (
    code_practical_manager,
    code_practical_execute,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/challenges")
async def list_code_challenges(
    subject: str = "",
    topic: str = "",
    type: str = "",
    difficulty: str = "",
):
    """列出代码挑战题."""
    challenges = code_practical_manager.list_challenges(
        subject=subject, topic=topic,
        challenge_type=type, difficulty=difficulty,
    )
    return {"challenges": challenges, "count": len(challenges)}


@router.get("/challenges/{challenge_id}")
async def get_challenge(challenge_id: str):
    """获取单个挑战详情（不含解析）."""
    challenge = code_practical_manager.get_challenge(challenge_id)
    if not challenge:
        return {"error": "Challenge not found"}
    return challenge


class ExecuteCodeRequest(BaseModel):
    code: str
    challenge_id: str = ""
    language: str = "python"


@router.post("/execute")
async def execute_student_code(body: ExecuteCodeRequest):
    """执行学生代码并返回可视化步骤."""
    result = await code_practical_execute.ainvoke({
        "code": body.code,
        "challenge_id": body.challenge_id,
        "language": body.language,
    })
    return result


@router.post("/challenges/{challenge_id}/submit")
async def submit_answer(challenge_id: str, body: ExecuteCodeRequest):
    """提交答案并自动评测."""
    challenge = code_practical_manager.get_challenge(challenge_id)
    if not challenge:
        return {"error": "Challenge not found"}
    
    result = await code_practical_execute.ainvoke({
        "code": body.code,
        "challenge_id": challenge_id,
        "language": body.language,
    })
    
    evaluation = result.get("evaluation")
    passed = evaluation.get("status") == "passed" if evaluation else False
    
    return {
        **result,
        "submitted_at": __import__("datetime").datetime.now().isoformat(),
        "passed": passed,
        "explanation_available": True,
    }


@router.get("/challenges/{challenge_id}/explanation")
async def get_explanation(challenge_id: str):
    """查看挑战解析（完成后调用）."""
    explanation = code_practical_manager.reveal_explanation(challenge_id)
    if not explanation:
        return {"error": "Not found or already completed"}
    return {"challenge_id": challenge_id, "explanation": explanation}
