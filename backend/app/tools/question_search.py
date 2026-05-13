"""Question Search Tool - 题库检索工具.

从题库中检索相似题目或按知识点/科目筛选题目。
MVP 阶段使用 Mock 数据。
"""

from app.core.tools import BaseTool, ToolResult


class QuestionSearchTool(BaseTool):
    """题库检索工具."""

    name = "question_search"
    description = "从408题库中检索相似题目，支持按知识点、科目、难度筛选"

    async def execute(
        self,
        query: str | None = None,
        subject: str | None = None,
        tags: list[str] | None = None,
        difficulty: int | None = None,
        limit: int = 10,
    ) -> ToolResult:
        """执行题库检索."""
        # TODO: 接入 RAG 检索 或 数据库查询
        return ToolResult(
            success=True,
            data={
                "results": [
                    {
                        "id": "q_001",
                        "subject": subject or "数据结构",
                        "content": "[Mock] 相似题目...",
                        "difficulty": difficulty or 3,
                    }
                ],
                "total": 1,
            },
        )


from app.core.tools import tool_registry
tool_registry.register(QuestionSearchTool())
