"""Question Search Tool - 题库检索工具.

从题库中检索相似题目或按知识点/科目筛选题目。
已接入 RAG 检索管线。
"""

import logging

from app.core.tools import BaseTool, ToolResult
from app.rag.retriever import retriever

logger = logging.getLogger(__name__)


class QuestionSearchTool(BaseTool):
    """题库检索工具 - 接入 RAG 检索."""

    name = "question_search"
    description = "从408题库中检索相似题目，支持按知识点、科目、难度筛选"

    async def execute(
        self,
        query: str | None = None,
        subject: str | None = None,
        tags: list[str] | None = None,
        difficulty: int | None = None,
        limit: int = 5,
        **kwargs,
    ) -> ToolResult:
        """执行题库检索.

        Args:
            query: 搜索关键词
            subject: 科目过滤
            tags: 知识点标签
            difficulty: 难度等级
            limit: 返回数量

        Returns:
            检索结果
        """
        if not query:
            return ToolResult(
                success=False,
                error="必须提供 query 参数",
            )

        try:
            results = await retriever.retrieve(query, top_k=limit)

            # 如果有科目过滤，过滤结果
            if subject:
                results = [
                    r for r in results
                    if r.get("metadata", {}).get("subject", "").lower() == subject.lower()
                    or subject in r.get("content", "")
                ]

            if not results:
                logger.info(f"QuestionSearchTool: 未找到相关题目 - query={query}")
                return ToolResult(
                    success=True,
                    data={"results": [], "total": 0},
                )

            return ToolResult(
                success=True,
                data={
                    "results": [
                        {
                            "content": r.get("content", ""),
                            "score": r.get("score", 0),
                            "metadata": r.get("metadata", {}),
                        }
                        for r in results
                    ],
                    "total": len(results),
                },
            )

        except Exception as e:
            logger.error(f"QuestionSearchTool: 检索失败 - {e}")
            return ToolResult(
                success=False,
                error=f"题库检索失败: {str(e)[:100]}",
            )


from app.core.tools import tool_registry
tool_registry.register(QuestionSearchTool())
