"""LLM Gateway - 多模型统一网关.

支持多模型可插拔切换：
- deepseek: DeepSeek API (文本推理主力)
- gpt-4o: OpenAI GPT-4o (视觉理解 + 文本)
- qwen: 通义千问 (备选)

通过配置文件指定默认模型，运行时按场景路由：
- 图片理解 → 多模态模型 (gpt-4o / deepseek-vl)
- 引导推理 → 文本大模型 (deepseek / gpt-4o)
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator
from app.config import settings


class BaseLLM(ABC):
    """LLM 基类."""

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """同步对话."""
        ...

    @abstractmethod
    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        """多模态对话（图片+文本）."""
        ...

    @abstractmethod
    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """流式对话."""
        ...


class DeepSeekLLM(BaseLLM):
    """DeepSeek 模型实现."""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL

    async def chat(self, messages: list[dict], **kwargs) -> str:
        # TODO: 实现 DeepSeek API 调用
        return "[Mock] DeepSeek response"

    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        # TODO: DeepSeek-VL 调用
        return "[Mock] DeepSeek VL response"

    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        # TODO: DeepSeek SSE 流式调用
        yield "[Mock] DeepSeek stream chunk"


class OpenAILLM(BaseLLM):
    """OpenAI GPT-4o 模型实现."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL

    async def chat(self, messages: list[dict], **kwargs) -> str:
        # TODO: 实现 OpenAI API 调用
        return "[Mock] GPT-4o response"

    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        # TODO: GPT-4o Vision 调用
        return "[Mock] GPT-4o Vision response"

    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        # TODO: OpenAI SSE 流式调用
        yield "[Mock] GPT-4o stream chunk"


class QwenLLM(BaseLLM):
    """通义千问模型实现."""

    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = settings.QWEN_BASE_URL

    async def chat(self, messages: list[dict], **kwargs) -> str:
        # TODO: 实现通义千问 API 调用
        return "[Mock] Qwen response"

    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        # TODO: 通义千问 VL 调用
        return "[Mock] Qwen VL response"

    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        # TODO: 通义千问 SSE 流式调用
        yield "[Mock] Qwen stream chunk"


class LLMGateway:
    """LLM 统一网关 - 管理多模型实例和路由."""

    def __init__(self):
        self._models: dict[str, BaseLLM] = {
            "deepseek": DeepSeekLLM(),
            "gpt-4o": OpenAILLM(),
            "qwen": QwenLLM(),
        }
        self.default_model = settings.DEFAULT_LLM_MODEL

    def get_model(self, model: str | None = None) -> BaseLLM:
        """获取指定模型实例."""
        name = model or self.default_model
        if name not in self._models:
            raise ValueError(f"Unsupported model: {name}. Available: {list(self._models.keys())}")
        return self._models[name]

    async def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        """对话（使用指定模型或默认模型）."""
        llm = self.get_model(model)
        return await llm.chat(messages, **kwargs)

    async def chat_with_image(
        self,
        messages: list[dict],
        image_url: str,
        model: str | None = None,
        **kwargs,
    ) -> str:
        """多模态对话."""
        llm = self.get_model(model)
        return await llm.chat_with_image(messages, image_url, **kwargs)

    async def stream_chat(
        self,
        messages: list[dict],
        model: str | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """流式对话."""
        llm = self.get_model(model)
        async for chunk in llm.stream_chat(messages, **kwargs):
            yield chunk


# 全局单例
llm_gateway = LLMGateway()
