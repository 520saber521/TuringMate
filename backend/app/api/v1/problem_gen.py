"""Problem Generation API — 「举一反三」题目生成器端点.

POST /api/v1/problem-gen/generate      — 基于原题生成变式题
POST /api/v1/problem-gen/validate      — 验证掌握程度
GET  /api/v1/problem-gen/templates     — 列出内置模板
"""

import logging
from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.problem_generator import problem_generator
from app.api.utils import format_agent_result

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateVariantsRequest(BaseModel):
    original_question: str
    topic: str
    subject: str = ""
    count: int = 3
    difficulty: str = "medium"


@router.post("/generate")
async def generate_variants(body: GenerateVariantsRequest):
    """基于原题生成变式练习题."""
    result = await problem_generator.generate_variants(
        original_question=body.original_question,
        topic=body.topic,
        subject=body.subject,
        count=body.count,
        difficulty=body.difficulty,
    )
    return format_agent_result(result)


class ValidateMasteryRequest(BaseModel):
    topic: str
    attempt_results: list[dict] = [
        # {"problem_id": "...", "passed": true/false, "time_seconds": 120}
    ]


@router.post("/validate")
async def validate_mastery(body: ValidateMasteryRequest):
    """验证知识点掌握程度."""
    result = await problem_generator.validate_mastery(
        topic=body.topic,
        attempt_results=body.attempt_results,
    )
    return format_agent_result(result)


@router.get("/templates")
async def list_templates():
    """列出内置题目模板."""
    from app.agents.problem_generator import BUILTIN_TEMPLATES
    templates = []
    for t in BUILTIN_TEMPLATES:
        templates.append({
            "id": t["template_id"],
            "subject": t["subject"],
            "topic": t["topic"],
            "difficulty": t["difficulty"],
            "parameters": list(t["parameters"].keys()),
        })
    return {"templates": templates, "count": len(templates)}
