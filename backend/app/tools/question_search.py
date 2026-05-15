"""Question Search Tool - 题库检索工具.

使用 LangChain @tool 定义，接入 RAG 检索管线。
完整实现见 app.core.tools.question_search
"""

from app.core.tools import question_search

__all__ = ["question_search"]
