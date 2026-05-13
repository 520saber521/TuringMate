"""Agent Tool Base - 工具注册基类."""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any


class ToolResult(BaseModel):
    """工具执行结果."""
    success: bool
    data: Any | None = None
    error: str | None = None


class BaseTool(ABC):
    """Agent 工具基类."""

    name: str = "base_tool"
    description: str = "Base tool description"

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具."""
        ...


class ToolRegistry:
    """工具注册表 - 管理所有可用工具."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        """注册工具."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """获取工具."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """列出所有工具（供 Agent 使用）."""
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]


# 全局单例
tool_registry = ToolRegistry()
