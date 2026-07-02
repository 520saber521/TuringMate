"""Thinking Tracer - 思维过程追踪（已弃用）.

本模块为历史占位符。思维回放功能已下线，保留文件以保证其他模块的导入兼容。
"""

from enum import Enum
from typing import Any


class StepType(str, Enum):
    """思考步骤类型（占位）."""
    QUESTION = "question"
    ANSWER = "answer"
    HINT = "hint"
    CORRECTION = "correction"
    PRACTICE = "practice"


class ThinkingTracer:
    """占位实现 — 实际追踪已下线，但保留接口以保证旧代码不报错."""

    def __init__(self, session_id: str = "", question_id: str = "", user_id: str = ""):
        self.session_id = session_id
        self.question_id = question_id
        self.user_id = user_id
        self._steps: list = []

    def record_step(self, *args: Any, **kwargs: Any) -> None:
        return None

    def build_path(self) -> dict:
        return {"session_id": self.session_id, "steps": []}

    def generate_weekly_report(self, historical: list | None = None) -> dict:
        return {"user_id": self.user_id, "weekly_stats": []}


def create_tracer(session_id: str = "", question_id: str = "", user_id: str = "") -> ThinkingTracer:
    return ThinkingTracer(session_id, question_id, user_id)
