"""TuringMate Backend - FastAPI Application Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="TuringMate API",
        description="408计算机考研 AI 1对1私教 - 后端服务",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.api.v1 import router as v1_router
    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "turingmate-backend"}

    return app


app = create_app()
