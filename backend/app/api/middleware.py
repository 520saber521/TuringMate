"""API中间件模块.

提供:
1. 请求追踪 (X-Request-Id)
2. 请求日志记录
3. 性能监控
4. 错误处理增强
"""

import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.api.response import error, ResponseMeta

logger = logging.getLogger("app.api.middleware")


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件.

    为每个请求生成或传递 X-Request-Id，
    并在响应头中返回。
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取或生成请求ID
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

        # 存储请求ID以便后续访问
        request.state.request_id = request_id

        # 执行请求
        response = await call_next(request)

        # 在响应头中设置请求ID
        response.headers["X-Request-Id"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件.

    记录请求方法和路径，响应状态码和耗时。
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始
        start_time = time.time()
        method = request.method
        path = request.url.path
        request_id = getattr(request.state, "request_id", "unknown")

        logger.info(f"[{request_id}] Request: {method} {path}")

        try:
            response = await call_next(request)

            # 记录请求完成
            duration = time.time() - start_time
            status = response.status_code

            log_level = logging.INFO if status < 400 else logging.WARNING
            logger.log(
                log_level,
                f"[{request_id}] Response: {status} ({duration:.3f}s)",
            )

            # 添加耗时头
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] Error: {e} ({duration:.3f}s)",
                exc_info=True,
            )

            # 返回统一错误响应
            return JSONResponse(
                status_code=500,
                content=error(
                    code="INTERNAL_ERROR",
                    message="服务器内部错误",
                    details={"error": str(e)},
                    meta=ResponseMeta(request_id=request_id),
                ),
            )


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件.

    监控慢请求并记录警告。
    """

    # 慢请求阈值 (秒)
    SLOW_REQUEST_THRESHOLD = 2.0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        response = await call_next(request)

        duration = time.time() - start_time

        # 检查慢请求
        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"[{request_id}] Slow request: {request.method} {request.url.path} "
                f"({duration:.3f}s > {self.SLOW_REQUEST_THRESHOLD}s)",
            )

        return response


def setup_middlewares(app):
    """注册所有中间件.

    Args:
        app: FastAPI 应用实例
    """
    # 注意: 中间件注册顺序为: 请求进入从外到内，响应返回从内到外
    # 所以最先注册的是最外层

    # 性能监控 (最外层)
    app.add_middleware(PerformanceMiddleware)

    # 请求日志
    app.add_middleware(RequestLoggingMiddleware)

    # 请求追踪 (最内层，最先处理请求ID)
    app.add_middleware(RequestTrackingMiddleware)