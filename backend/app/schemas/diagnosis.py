"""Diagnosis schemas."""
from pydantic import BaseModel
from typing import Optional


class WeakPoint(BaseModel):
    """薄弱知识点."""
    subject: str
    topic: str
    score: int  # 0-100
    description: str


class Recommendation(BaseModel):
    """练习推荐."""
    type: str  # "专项练习" | "知识点回顾" | "真题演练"
    title: str
    count: int


class DiagnosisReportResponse(BaseModel):
    """诊断报告响应."""
    user_id: str
    scores: dict[str, int]  # 四科分数
    weak_points: list[WeakPoint]
    recommendations: list[Recommendation]
