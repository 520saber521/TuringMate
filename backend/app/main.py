"""TuringMate Backend - FastAPI Application Entry Point.

包含全局异常处理器注册、CORS 配置、中间件注册.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.utils import api_exception_handler, APIError
from app.api.middleware import setup_middlewares


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="TuringMate API",
        description="408计算机考研 AI 1对1私教 - 后端服务",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── 注册自定义中间件 ──
    # 请求追踪、日志记录、性能监控
    setup_middlewares(app)

    # ── CORS 配置 ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── L2: 全局异常处理器 ──
    # 统一捕获所有未处理异常，返回规范 JSON 错误响应
    # 业务异常抛出 APIError / AgentError / RAGError 自动映射到对应 HTTP 状态码
    app.add_exception_handler(APIError, api_exception_handler)
    app.add_exception_handler(Exception, api_exception_handler)

    # ── 注册路由 ──
    from app.api.v1 import router as v1_router
    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "turingmate-backend"}

    return app


app = create_app()
