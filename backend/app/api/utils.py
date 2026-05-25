"""API 工具模块 — SSE 流式输出 + 异常处理 + Output Parser + RunConfig.

提供可复用的 API 层基础设施，消除各 endpoint 的重复代码。
包含:
  - create_sse_response(): 标准 SSE StreamingResponse 工厂
  - api_exception_handler: FastAPI 全局异常处理
  - retry_async / retry_sync: 统一重试装饰器
  - safe_parse_json / format_agent_result: 结果解析
  - make_config: LangGraph RunConfig 工厂
"""

import asyncio
import functools
import json
import logging
import time
from typing import Any, AsyncIterator, Callable, TypeVar

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

logger = logging.getLogger(__name__)

# ============================================================
# SSE 流式输出工厂
# ============================================================


async def sse_stream(
    async_generator: AsyncIterator[str],
    event_type: str = "message",
) -> AsyncIterator[str]:
    """标准化的 SSE 流式输出包装器.

    统一格式:
      data: {"content": "..."}\n\n
      data: [DONE]\n\n

    错误时自动发送 error 事件.
    """
    try:
        async for chunk in async_generator:
            if chunk:
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
    except Exception as e:
        logger.error(f"SSE stream error: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    finally:
        yield "data: [DONE]\n\n"


def create_sse_response(
    async_generator: AsyncIterator[str],
) -> StreamingResponse:
    """创建标准 SSE StreamingResponse — 统一 headers 和格式."""
    return StreamingResponse(
        sse_stream(async_generator),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ============================================================
# L2: 统一异常处理 + Retry 装饰器
# ============================================================

# 可重试的异常类型（网络超时、LLM 服务不可用等）
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
    ConnectionRefusedError,
    ConnectionResetError,
)


class APIError(Exception):
    """统一 API 业务异常.

    所有业务逻辑错误应抛出此异常（或子类），
    由 api_exception_handler 统一捕获并返回规范响应。
    """

    def __init__(self, message: str, status_code: int = 500, detail: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class AgentError(APIError):
    """Agent 调用失败."""

    def __init__(self, message: str, agent: str = "", detail: dict | None = None):
        _detail = {"agent": agent}
        if detail:
            _detail.update(detail)
        super().__init__(message, status_code=502, detail=_detail)


class RAGError(APIError):
    """RAG 检索失败."""

    def __init__(self, message: str, detail: dict | None = None):
        super().__init__(message, status_code=503, detail=detail or {})


def _is_retryable(exc: Exception) -> bool:
    """判断异常是否可重试."""
    return isinstance(exc, RETRYABLE_EXCEPTIONS) or (
        hasattr(exc, "status_code") and 500 <= getattr(exc, "status_code", 0) < 600
    )


F = TypeVar("F", bound=Callable[..., Any])


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple | None = None,
) -> Callable[[F], F]:
    """异步函数重试装饰器.

    Args:
        max_attempts: 最大重试次数
        delay: 首次重试等待秒数
        backoff: 延迟倍增因子 (delay * backoff^(attempt-1))
        exceptions: 可重试的异常类型元组 (默认使用 RETRYABLE_EXCEPTIONS)

    用法:
        @retry_async(max_attempts=3)
        async def call_llm(...): ...
    """
    exc_types = exceptions or RETRYABLE_EXCEPTIONS

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exc_types as e:
                    last_exc = e
                    if attempt < max_attempts:
                        wait = delay * (backoff ** (attempt - 1))
                        logger.warning(
                            f"Retry {attempt}/{max_attempts} for {func.__name__}: {e} "
                            f"(next in {wait:.1f}s)"
                        )
                        await asyncio.sleep(wait)
                    else:
                        logger.error(
                            f"All {max_attempts} retries exhausted for {func.__name__}: {e}"
                        )
            raise last_exc

        return wrapper  # type: ignore

    return decorator


def retry_sync(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple | None = None,
) -> Callable[[F], F]:
    """同步函数重试装饰器 (与 retry_async 对称)."""
    exc_types = exceptions or RETRYABLE_EXCEPTIONS

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exc_types as e:
                    last_exc = e
                    if attempt < max_attempts:
                        wait = delay * (backoff ** (attempt - 1))
                        logger.warning(
                            f"Retry {attempt}/{max_attempts} for {func.__name__}: {e}"
                        )
                        time.sleep(wait)
                    else:
                        logger.error(
                            f"All {max_attempts} retries exhausted for {func.__name__}: {e}"
                        )
            raise last_exc

        return wrapper  # type: ignore

    return decorator


async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI 全局异常处理器.

    统一捕获所有未处理异常，返回规范的 JSON 错误响应。
    在 main.py 中通过 app.add_exception_handler 注册:

        app.add_exception_handler(Exception, api_exception_handler)

    响应格式:
        {"error": true, "message": "...", "code": 500, "detail": {...}}
    """
    # 已知业务异常
    if isinstance(exc, APIError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "code": exc.status_code,
                "detail": exc.detail,
            },
        )

    # 未知异常 — 记录完整堆栈但不泄露内部信息
    request_id = request.headers.get("X-Request-Id", "unknown")
    logger.exception(f"Unhandled exception [request={request_id}]: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误，请稍后重试",
            "code": 500,
            "detail": {"request_id": request_id},
        },
    )


# ============================================================
# L3: RunConfig 工厂
# ============================================================


def make_config(session_id: str, **extra) -> dict:
    """构建统一的 LangGraph RunnableConfig.

    消除各 endpoint 重复的 `{"configurable": {"thread_id": ...}}` 构造。

    Args:
        session_id: 会话/线程标识符
        **extra: 额外配置项合并到 configurable 中

    Returns:
        标准化的 LangGraph RunnableConfig 字典.

    示例:
        config = make_config("session_123", tags=["chat"])
        # → {"configurable": {"thread_id": "session_123", "tags": ["chat"]}}
    """
    base = {"thread_id": session_id}
    base.update(extra)
    return {"configurable": base}


# ============================================================
# 统一 Output Parser 链
# ============================================================

str_parser = StrOutputParser()
"""全局 StrOutputParser 实例."""

json_parser = JsonOutputParser()
"""全局 JsonOutputParser 实例."""


def safe_parse_json(raw: Any, fallback: dict | None = None) -> dict:
    """安全的 JSON 解析 — 兼容字符串 / dict / Pydantic model."""
    if isinstance(raw, dict):
        return raw
    if hasattr(raw, "model_dump"):
        return raw.model_dump()
    if hasattr(raw, "dict"):
        return raw.dict()
    if isinstance(raw, str) and raw.strip():
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    return fallback or {}


def format_agent_result(result: dict | None, **overrides) -> dict:
    """统一 Agent 返回结果格式化."""
    if not result:
        return {**overrides}
    base = result if isinstance(result, dict) else {"raw": str(result)}
    return {**base, **{k: v for k, v in overrides.items() if k not in base}}
