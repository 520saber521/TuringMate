"""Emotion & State Schemas — 情绪感知与状态调节数据模型."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EmotionState(str, Enum):
    """检测到的情绪状态."""
    NEUTRAL = "neutral"           # 平静/正常
    CONFIDENT = "confident"      # 自信/顺畅
    FRUSTRATED = "frustrated"    # 沮丧/受挫
    ANXIOUS = "anxious"          # 焦虑/紧张
    FATIGUED = "fatigued"        # 疲劳/困倦
    BORED = "bored"              # 无聊/走神
    EXCITED = "excited"          # 兴奋/有动力


class TeachingMode(str, Enum):
    """教学模式（根据情绪切换）."""
    NORMAL = "normal"                    # 标准 苏格拉底模式
    CONFIDENCE_BUILDING = "confidence"    # 信心构建模式（沮丧时）
    RELAXED_REVIEW = "relaxed"           # 轻松复习模式（疲劳时）
    CHALLENGE = "challenge"               # 挑战模式（自信时）
    ENGAGEMENT = "engagement"             # 吸引注意力模式（走神时）
    DEEP_DIVE = "deep_dive"               # 深入探讨模式（兴奋时）


class EmotionDetectionResult(BaseModel):
    """单次情绪检测结果."""
    emotion: EmotionState = Field(default=EmotionState.NEUTRAL)
    confidence: float = Field(default=0.5, description="置信度 0-1", ge=0, le=1)

    # 检测依据
    detected_by: str = Field(default="", description="检测方式: keyword / pattern / response_quality / typing_speed")
    triggers: list[str] = Field(default_factory=list, description="触发的关键词或信号")

    # 建议的教学策略
    suggested_mode: TeachingMode = Field(default=TeachingMode.NORMAL)
    adaptation_hints: list[str] = Field(default_factory=list, description="适配建议")


class EmotionEvent(BaseModel):
    """情绪事件记录（用于追踪和学习）."""
    event_id: str = Field(description="事件ID")
    session_id: str = Field(description="会话ID")
    timestamp: str = Field(default="")
    emotion_before: EmotionState = Field(default=EmotionState.NEUTRAL)
    emotion_after: Optional[EmotionState] = None
    trigger_message: str = Field(default="", description="触发消息")
    mode_switch: Optional[TeachingMode] = None
    intervention: str = Field(default="", description="采取的干预措施")
    effectiveness: Optional[str] = None  # "improved" / "no_change" / "worsened"
