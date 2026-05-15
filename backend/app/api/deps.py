"""API dependencies - 依赖注入."""

from app.config import get_settings


def get_app_settings():
    """获取应用配置."""
    return get_settings()
