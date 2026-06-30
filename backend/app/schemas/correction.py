"""Correction schemas."""
from pydantic import BaseModel
from typing import Optional


class CorrectionRequest(BaseModel):
    """批改请求."""
    image_url: str
    question_id: Optional[str] = None


class CorrectionStep(BaseModel):
    """批改步骤."""
    step_no: int
    content: str
    is_correct: bool
    error_type: Optional[str] = None
    hint: Optional[str] = None


class CorrectionAnalyzeResponse(BaseModel):
    """手写批改分析结果."""
    correction_id: str
    question_id: str
    steps: list[CorrectionStep]
    overall_feedback: str
