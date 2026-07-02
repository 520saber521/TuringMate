"""Thinking Trace Schemas - 已弃用（思维回放功能已下线）.

保留此文件以保证旧代码的导入兼容，所有类都是最小占位实现。
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class StepType(str, Enum):
    """思考步骤类型."""
    QUESTION = "question"
    ANSWER = "answer"
    HINT = "hint"
    CORRECTION = "correction"
    PRACTICE = "practice"


class ThinkingStep(BaseModel):
    """单步思考记录."""
    step_id: str = Field(default="", description="步骤ID")
    step_type: StepType = Field(default=StepType.QUESTION, description="步骤类型")
    content: str = Field(default="", description="步骤内容")
    timestamp: str = Field(default="", description="时间戳")


class ThinkingPath(BaseModel):
    """完整思考路径."""
    session_id: str = Field(default="", description="会话ID")
    steps: list[ThinkingStep] = Field(default_factory=list, description="步骤序列")


class ThinkingWeaknessTag(str, Enum):
    """思维弱点标签."""
    CONCEPT_CONFUSION = "concept_confusion"
    LOGIC_GAP = "logic_gap"
    RIGOROUS_LACK = "rigorous_lack"
    OVERLOOK_EDGE_CASE = "overlook_edge_case"
    WRONG_METHOD_CHOICE = "wrong_method_choice"
    CALCULATION_ERROR = "calculation_error"
    READING_MISTAKE = "reading_mistake"
    MEMORY_FAILURE = "memory_failure"


class DeviationLevel(str, Enum):
    """偏离程度."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class WeeklyThinkingStats(BaseModel):
    """周统计."""
    week_start: str = Field(default="", description="周起始日期")
    total_steps: int = Field(default=0, description="总步数")
    deviations: int = Field(default=0, description="偏离次数")


class ThinkingGrowthReport(BaseModel):
    """思维成长报告."""
    user_id: str = Field(default="", description="用户ID")
    weekly_stats: list[WeeklyThinkingStats] = Field(
        default_factory=list, description="周统计列表"
    )
