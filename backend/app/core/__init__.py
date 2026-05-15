"""TuringMate Core - LangChain 核心模块.

基于 LangChain 全栈重构:
  - llm_gateway:  ChatOpenAI 多模型网关
  - tools:        @tool 工具集 (image_ocr, question_search, code_executor, knowledge_graph)
"""

from app.core.llm_gateway import llm_gateway, LLMGateway, get_llm
from app.core.tools import (
    ALL_TOOLS,
    TOOL_NAMES,
    langchain_tools,
    image_ocr,
    question_search,
    code_executor,
    knowledge_graph,
)

__all__ = [
    "llm_gateway",
    "LLMGateway",
    "get_llm",
    "ALL_TOOLS",
    "TOOL_NAMES",
    "langchain_tools",
]
