"""TuringMate Core - LLM Gateway + Tools + Prompts.

模块:
  - llm_gateway:   LangChain ChatOpenAI 多模型网关 (DeepSeek/OpenAI/Qwen)
  - tools:         @tool 装饰器的工具集 (image_ocr/question_search/code_executor/knowledge_graph)
  - prompts:       集中式 Prompt 模板管理 (ChatPromptTemplate 注册表)
"""

from app.core.llm_gateway import llm_gateway, get_llm
from app.core.tools import (
    ALL_TOOLS,
    TOOL_NAMES,
    image_ocr,
    question_search,
    code_executor,
    knowledge_graph,
)
from app.core.prompts import (
    PromptRegistry,
    STAGE_INSTRUCTIONS,
    get_prompt,
    list_prompts,
)

__all__ = [
    # LLM Gateway
    "llm_gateway",
    "get_llm",
    # Tools
    "ALL_TOOLS",
    "TOOL_NAMES",
    "image_ocr",
    "question_search",
    "code_executor",
    "knowledge_graph",
    # Prompts
    "PromptRegistry",
    "STAGE_INSTRUCTIONS",
    "get_prompt",
    "list_prompts",
]
