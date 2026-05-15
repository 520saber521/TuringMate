"""Embeddings - 基于 LangChain 的 Embedding 模型.

使用 langchain 统一接口，支持多种后端：
  1. OpenAIEmbeddings (DeepSeek API 兼容) — 高质量 1536 维
  2. HuggingFaceEmbeddings (sentence-transformers) — 本地免费
  3. FakeEmbeddings (开发测试) — 随机向量

通过 create_embeddings() 自动选择最佳可用模型。
"""

import logging

from app.config import settings

logger = logging.getLogger(__name__)


def create_embeddings():
    """创建 LangChain Embeddings 实例（自动选择最佳后端）.

    选择优先级:
      1. DeepSeek OpenAI Embedding API (需 API Key)
      2. HuggingFace sentence-transformers 本地模型
      3. FakeEmbeddings 兜底（仅限测试）

    Returns:
        LangChain Embeddings 实例，兼容所有 LangChain 向量存储/检索组件
    """
    # ── 策略 1: DeepSeek / OpenAI Embedding API ──
    if settings.DEEPSEEK_API_KEY:
        try:
            from langchain_openai import OpenAIEmbeddings
            emb = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
            logger.info("Embeddings: 使用 DeepSeek/OpenAI Embedding API (1536维)")
            return emb
        except Exception as e:
            logger.warning(f"Embeddings: OpenAI Embedding 初始化失败 ({e})")

    # ── 策略 2: HuggingFace 本地模型 ──
    local_model = settings.EMBEDDING_MODEL or "shibing624/text2vec-base-chinese"
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        emb = HuggingFaceEmbeddings(
            model_name=local_model,
            encode_kwargs={"normalize_embeddings": True},
        )
        dim = getattr(emb.client, "get_sentence_embedding_dimension", lambda: "?")()
        logger.info(f"Embeddings: 使用 HuggingFace {local_model} ({dim}维)")
        return emb
    except ImportError:
        logger.warning("Embeddings: langchain_huggingface 未安装")
    except Exception as e:
        logger.warning(f"Embeddings: HuggingFace 模型加载失败 ({e})")

    # ── 策略 3: FakeEmbeddings 兜底 ──
    try:
        from langchain_core.embeddings import FakeEmbeddings
        import numpy as np
        logger.warning("Embeddings: 使用 FakeEmbeddings（仅限开发测试！）")
        return FakeEmbeddings(size=384)
    except Exception:
        # 最终兜底
        class _MinimalFakeEmbeddings:
            def embed_query(self, text):
                return [0.0] * 384
            def embed_documents(self, texts):
                return [[0.0] * 384 for _ in texts]
        logger.error("Embeddings: 所有方案均失败，使用极简 mock!")
        return _MinimalFakeEmbeddings()


# 全局单例（懒初始化）
_embeddings_instance = None


def get_embeddings():
    """获取全局 Embeddings 单例."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = create_embeddings()
    return _embeddings_instance


# 向后兼容
embeddings = get_embeddings()
