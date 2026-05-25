"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


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
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Database (MySQL)
    DATABASE_URL: str = "mysql+pymysql://turingmate:turingmate@localhost:3306/turingmate"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Configuration - Model Gateway
    DEFAULT_LLM_MODEL: str = "deepseek"  # deepseek, gpt-4o, qwen
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"

    # RAG Configuration
    EMBEDDING_MODEL: str = "text2vec-base-chinese"  # 开发阶段用本地模型
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RERANK_WEIGHT_VECTOR: float = 0.7
    RERANK_WEIGHT_BM25: float = 0.3

    # LangGraph Checkpointer 后端 (M6: memory / postgres / redis)
    CHECKPOINT_BACKEND: str = "memory"

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
