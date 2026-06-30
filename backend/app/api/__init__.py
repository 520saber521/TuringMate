"""TuringMate API package.

提供统一API管理层基础设施:
- response: 统一响应格式
- deps: 依赖注入
- middleware: 中间件
- utils: 工具函数
"""

from app.api.response import (
    success,
    error,
    paginated,
    APIResponse,
    APIErrorResponse,
    ResponseMeta,
)

__all__ = [
    "success",
    "error",
    "paginated",
    "APIResponse",
    "APIErrorResponse",
    "ResponseMeta",
]