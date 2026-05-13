"""Visualization schemas."""
from pydantic import BaseModel
from typing import Any


class VisualStep(BaseModel):
    """执行步骤快照."""
    step_no: int
    line: int  # 当前行号
    description: str
    variables: dict[str, Any]  # 变量状态
    visual_state: dict[str, Any]  # 可视化数据（节点/数组/树结构）


class VisualizeExecuteResponse(BaseModel):
    """代码执行可视化响应."""
    execution_id: str
    language: str
    steps: list[VisualStep]
    total_steps: int
