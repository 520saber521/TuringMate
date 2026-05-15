"""Code Executor Tool - 代码执行沙箱.

使用 LangChain @tool + StructuredTool 定义，支持 Python 代码追踪执行。
完整实现见 app.core.tools.code_executor
"""

from app.core.tools import code_executor

__all__ = ["code_executor"]
