"""文档处理模块的自定义异常.

统一错误类型，便于上层捕获和处理。
"""

from __future__ import annotations


class DocumentError(Exception):
    """文档处理基础异常."""

    pass


# ────────────────────────────────────────
# MinerU 相关
# ────────────────────────────────────────


class MinerUError(DocumentError):
    """MinerU 通用错误."""

    pass


class MinerUAuthError(MinerUError):
    """MinerU 认证错误（401/403）."""

    pass


class MinerURequestError(MinerUError):
    """MinerU 请求错误（4xx/5xx）."""

    pass


class MinerUTimeoutError(MinerUError):
    """MinerU 超时."""

    pass


# ────────────────────────────────────────
# Gotenberg 相关
# ────────────────────────────────────────


class GotenbergError(DocumentError):
    """Gotenberg 通用错误."""

    pass


class GotenbergRequestError(GotenbergError):
    """Gotenberg 请求错误."""

    pass


class GotenbergTimeoutError(GotenbergError):
    """Gotenberg 超时."""

    pass


# ────────────────────────────────────────
# Pipeline 相关
# ────────────────────────────────────────


class PipelineError(DocumentError):
    """Pipeline 执行错误."""

    pass


class UnsupportedFormatError(PipelineError):
    """不支持的文档格式."""

    pass


class ConfigurationError(PipelineError):
    """配置错误."""

    pass
