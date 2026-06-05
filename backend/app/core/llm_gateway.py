"""LLM Gateway - 基于 LangChain 的多模型统一网关.

使用 langchain-openai 的 ChatOpenAI 统一接口，支持：
- deepseek:  DeepSeek API (deepseek-chat / deepseek-reasoner)
- openai:    OpenAI GPT-4o
- qwen:      通义千问 (DashScope OpenAI 兼容)

所有模型共享统一的 LangChain 接口:
  - .invoke()       → 同步调用
  - .ainvoke()      → 异步调用
  - .stream()       → 同步流式
  - .astream()      → 异步流式（用于 SSE）
  - .bind_tools()   → 工具绑定（Agent 用途）
"""

import base64
import logging
from typing import AsyncIterator

from langchain_openai import ChatOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================
# 模型注册表 — 预定义的模型配置
# ============================================================

MODEL_REGISTRY: dict[str, dict] = {
    "deepseek": {
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url_env": "DEEPSEEK_BASE_URL",
        "default_base_url": "https://api.deepseek.com/v1",
    },
    "openai": {
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "default_base_url": "https://api.openai.com/v1",
    },
    "qwen": {
        "model": "qwen-plus",
        "api_key_env": "QWEN_API_KEY",
        "base_url_env": "QWEN_BASE_URL",
        "default_base_url": "https://dashscope.aliyuncs.com/api/v1",
    },
    "doubao": {
        "model": "doubao-seed-2.0-lite",
        "api_key_env": "DOUBAO_API_KEY",
        "base_url_env": "DOUBAO_BASE_URL",
        "default_base_url": "https://ark.cn-beijing.volces.com/api/v3",
    },
}


class LLMGateway:
    """LangChain LLM 网关.

    基于 ChatOpenAI 实现多模型管理、路由和统一调用。
    所有模型实例延迟创建，首次使用时初始化。
    """

    def __init__(self):
        self._models: dict[str, ChatOpenAI] = {}
        self.default_model_name: str = settings.DEFAULT_LLM_MODEL or "deepseek"

    # ── 核心方法：获取 LangChain ChatOpenAI 实例 ──

    def get_chat_model(self, model_name: str | None = None) -> ChatOpenAI:
        """获取指定模型的 LangChain ChatOpenAI 实例.

        Args:
            model_name: 模型名称 ("deepseek" | "openai" | "qwen")，
                       默认使用配置中的默认模型

        Returns:
            LangChain ChatOpenAI 实例
        """
        name = model_name or self.default_model_name

        if name not in MODEL_REGISTRY:
            raise ValueError(
                f"不支持的模型: {name}. 可选: {list(MODEL_REGISTRY.keys())}"
            )

        # 延迟创建：已缓存则直接返回
        if name in self._models:
            return self._models[name]

        # 创建新的 ChatOpenAI 实例
        config = MODEL_REGISTRY[name]
        api_key = getattr(settings, config["api_key_env"], "")
        base_url = getattr(settings, config["base_url_env"], "") or config["default_base_url"]

        if not api_key:
            logger.warning(
                f"LLMGateway: {name} API Key 未配置 ({config['api_key_env']}), "
                f"将尝试调用但可能失败"
            )

        chat_model = ChatOpenAI(
            model=config["model"],
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=2048,
            streaming=True,  # 默认启用流式支持
        )
        self._models[name] = chat_model
        logger.info(f"LLMGateway: 初始化模型 {name} ({config['model']}) @ {base_url}")
        return chat_model

    # ── 便捷调用方法 ──

    async def chat(self, messages: list[dict], model: str | None = None, **kwargs) -> str:
        """同步对话.

        Args:
            messages: OpenAI 格式的消息列表 [{"role": ..., "content": ...}]
            model: 可选覆盖默认模型
            **kwargs: 覆盖 temperature, max_tokens 等

        Returns:
            模型回复文本
        """
        llm = self.get_chat_model(model)

        from langchain_core.messages import (
            SystemMessage, HumanMessage, AIMessage,
        )
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif role == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        # 构建带 kwargs 的 LLM
        invoke_kwargs = {}
        if "temperature" in kwargs:
            invoke_kwargs["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            invoke_kwargs["max_tokens"] = kwargs["max_tokens"]

        response = await llm.ainvoke(lc_messages, config={"configurable": invoke_kwargs})
        return response.content

    async def chat_with_image(
        self,
        messages: list[dict],
        image_url: str,
        model: str | None = None,
        **kwargs,
    ) -> str:
        """多模态对话 (图片 + 文本).

        Args:
            messages: 对话历史消息
            image_url: 图片 URL 或本地文件路径
            model: 模型名称
        """
        llm = self.get_chat_model(model)

        from langchain_core.messages import (
            SystemMessage, HumanMessage, AIMessage,
        )
        from langchain_core.messages.human import HumanMessage as HM

        # 构建多模态 content
        content_parts: list[dict | str] = []

        # 最后一条 user 消息携带图片
        for msg in messages[:-1]:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                content_parts.append(SystemMessage(content=content))
            elif role == "user":
                content_parts.append(HumanMessage(content=content))
            elif role == "assistant":
                content_parts.append(AIMessage(content=content))

        # 处理图片
        last_msg_content: list = []
        if messages and messages[-1].get("content"):
            last_msg_content.append({"type": "text", "text": messages[-1]["content"]})

        if image_url.startswith(("http://", "https://")):
            last_msg_content.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })
        else:
            with open(image_url, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            last_msg_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        content_parts.append(HM(content=last_msg_content))

        response = await llm.ainvoke(content_parts)
        return response.content

    async def stream_chat(
        self,
        messages: list[dict],
        model: str | None = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """流式对话 — 用于 SSE 推送.

        Yields:
            文本 token 片段
        """
        llm = self.get_chat_model(model)

        from langchain_core.messages import (
            SystemMessage, HumanMessage, AIMessage,
        )
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif role == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        async for chunk in llm.astream(lc_messages):
            if chunk.content:
                yield chunk.content

    # ── Agent 相关 ──

    def get_bindable_llm(self, model: str | None = None) -> ChatOpenAI:
        """获取可用于 .bind_tools() 的 LLM 实例.

        LangGraph Agent 需要 bind_tools 来绑定工具定义.
        """
        return self.get_chat_model(model)


# 全局单例
llm_gateway = LLMGateway()


# ── 向后兼容：保留旧的直接访问方式 ──

def get_llm(model: str | None = None) -> ChatOpenAI:
    """获取 LangChain ChatOpenAI 实例（便捷函数）."""
    return llm_gateway.get_chat_model(model)
