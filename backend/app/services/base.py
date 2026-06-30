"""服务层基类.

提供统一的服务层基础设施:
1. 日志记录
2. 错误处理
3. 重试机制
4. 上下文管理
"""

import logging
import functools
from typing import Any, TypeVar, Callable
from abc import ABC

from app.api.utils import retry_async, APIError

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class BaseService(ABC):
    """服务层基类.

    所有业务服务应继承此类，获得:
    - 统一的日志记录器
    - 错误处理装饰器
    - 重试机制

    示例:
        class ChatService(BaseService):
            @BaseService.handle_errors("对话服务")
            async def send_message(self, session_id: str, message: str) -> dict:
                ...
    """

    # 子类应覆盖此属性
    service_name: str = "base"

    def __init__(self):
        self._logger = logging.getLogger(f"app.services.{self.service_name}")

    @property
    def logger(self) -> logging.Logger:
        """获取当前服务的日志记录器."""
        return self._logger

    @staticmethod
    def handle_errors(
        service_name: str,
        default_message: str = "服务处理失败",
    ) -> Callable[[F], F]:
        """错误处理装饰器.

        捕获服务层异常，转换为统一的APIError。
        自动记录错误日志。

        Args:
            service_name: 服务名称，用于日志标识
            default_message: 默认错误消息

        Returns:
            装饰后的函数
        """

        def decorator(func: F) -> F:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except APIError:
                    raise
                except Exception as e:
                    logger = logging.getLogger(f"app.services.{service_name}")
                    logger.exception(f"[{service_name}] {func.__name__} failed: {e}")
                    raise APIError(
                        message=f"{default_message}: {str(e)}",
                        status_code=500,
                        detail={"service": service_name, "function": func.__name__},
                    )

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except APIError:
                    raise
                except Exception as e:
                    logger = logging.getLogger(f"app.services.{service_name}")
                    logger.exception(f"[{service_name}] {func.__name__} failed: {e}")
                    raise APIError(
                        message=f"{default_message}: {str(e)}",
                        status_code=500,
                        detail={"service": service_name, "function": func.__name__},
                    )

            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper  # type: ignore
            return sync_wrapper  # type: ignore

        return decorator

    @staticmethod
    def with_retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
    ) -> Callable[[F], F]:
        """重试装饰器.

        为异步方法添加自动重试能力。

        Args:
            max_attempts: 最大重试次数
            delay: 首次重试等待秒数
            backoff: 延迟倍增因子

        Returns:
            装饰后的函数
        """
        return retry_async(max_attempts, delay, backoff)

    def log_info(self, message: str, **kwargs):
        """记录信息日志."""
        self._logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """记录警告日志."""
        self._logger.warning(message, **kwargs)

    def log_error(self, message: str, **kwargs):
        """记录错误日志."""
        self._logger.error(message, **kwargs)