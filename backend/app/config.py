"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "TuringMate"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ]

    # Database (MySQL)
    DATABASE_URL: str = "mysql+pymysql://turingmate:turingmate@localhost:3306/turingmate"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Configuration - Model Gateway
    DEFAULT_LLM_MODEL: str = "deepseek"  # deepseek, gpt-4o, qwen, doubao
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    DOUBAO_API_KEY: str = ""
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"

    # 文档处理服务 (MinerU + Gotenberg)
    MINERU_BASE_URL: str = "http://localhost:8001"
    MINERU_API_TOKEN: Optional[str] = None
    MINERU_TIMEOUT: float = 300.0
    GOTENBERG_BASE_URL: str = "http://localhost:3000"
    GOTENBERG_TIMEOUT: float = 120.0

    # RAG Configuration
    EMBEDDING_MODEL: str = "text2vec-base-chinese"  # 开发阶段用本地模型
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RERANK_WEIGHT_VECTOR: float = 0.7
    RERANK_WEIGHT_BM25: float = 0.3

    # LangGraph Checkpointer 后端 (M6: memory / postgres / redis)
    CHECKPOINT_BACKEND: str = "memory"

    # Auth / JWT
    SECRET_KEY: str = "change-me-in-production-use-a-strong-random-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # COS (Tencent Cloud Object Storage)
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_BUCKET: str = ""
    COS_REGION: str = "ap-shanghai"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
