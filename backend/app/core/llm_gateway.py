"""LLM Gateway - 多模型统一网关.

支持多模型可插拔切换（基于 OpenAI SDK，统一接口）:
- deepseek: DeepSeek API (文本推理主力, 兼容 OpenAI 格式)
- gpt-4o: OpenAI GPT-4o (视觉理解 + 文本)
- qwen: 通义千问 VL (备选, DashScope OpenAI兼容)

通过配置文件指定默认模型，运行时按场景路由：
- 图片理解 → 多模态模型 (gpt-4o / deepseek / qwen-vl)
- 引导推理 → 文本大模型 (deepseek-chat / gpt-4o)
"""

import logging
import base64
from abc import ABC, abstractmethod
from typing import AsyncIterator

from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """LLM 基类."""

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    f"{self.__class__.__name__}: API_KEY 未配置，请检查 .env 文件"
                )
            self._client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

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
    """DeepSeek 模型实现 - 使用 deepseek-chat / deepseek-reasoner."""

    def __init__(self):
        super().__init__(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            model_name="deepseek-chat",
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        model = kwargs.get("model", "deepseek-chat")
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        """DeepSeek 多模态对话."""
        content_with_image = []
        for msg in messages[-1:]:
            content_with_image.append({"type": "text", "text": msg["content"]})

        if image_url.startswith(("http://", "https://")):
            content_with_image.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
        else:
            with open(image_url, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            content_with_image.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        new_messages = [
            *messages[:-1],
            {"role": "user", "content": content_with_image},
        ]
        return await self.chat(new_messages, **kwargs)

    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        model = kwargs.get("model", "deepseek-chat")
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


class OpenAILLM(BaseLLM):
    """OpenAI GPT-4o 模型实现."""

    def __init__(self):
        super().__init__(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            model_name="gpt-4o",
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        model = kwargs.get("model", "gpt-4o")
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        """GPT-4o Vision 原生多模态."""
        content_with_image = []
        for msg in messages[-1:]:
            content_with_image.append({"type": "text", "text": msg["content"]})

        if image_url.startswith(("http://", "https://")):
            content_with_image.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
        else:
            with open(image_url, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            content_with_image.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        new_messages = [
            *messages[:-1],
            {"role": "user", "content": content_with_image},
        ]
        return await self.chat(new_messages, **kwargs)

    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        model = kwargs.get("model", "gpt-4o")
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


class QwenLLM(BaseLLM):
    """通义千问模型实现 - DashScope OpenAI 兼容格式."""

    def __init__(self):
        super().__init__(
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_BASE_URL,
            model_name="qwen-plus",
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        model = kwargs.get("model", "qwen-plus")
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )
        return response.choices[0].message.content or ""

    async def chat_with_image(self, messages: list[dict], image_url: str, **kwargs) -> str:
        """通义千问 VL 多模态."""
        content_with_image = []
        for msg in messages[-1:]:
            content_with_image.append({"type": "text", "text": msg["content"]})

        if image_url.startswith(("http://", "https://")):
            content_with_image.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
        else:
            with open(image_url, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            content_with_image.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        new_messages = [
            *messages[:-1],
            {"role": "user", "content": content_with_image},
        ]
        return await self.chat(new_messages, model="qwen-vl-max", **kwargs)

    async def stream_chat(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        model = kwargs.get("model", "qwen-plus")
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


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
