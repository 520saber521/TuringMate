"""Vector Store - 基于 LangChain ChromaDB 向量存储 (L5 简化版).

- 使用 langchain_chroma.Chroma 原生持久化
- 自动创建目录 / collection (Chroma 内置处理)
- 延迟初始化单例模式
- 移除冗余 VectorStoreWrapper 兼容层
"""

import logging
from typing import Optional

from langchain_chroma import Chroma

from app.config import settings
from .embeddings import get_embeddings

logger = logging.getLogger(__name__)

# 全局单例（延迟初始化）
_store: Optional[Chroma] = None


def get_vectorstore() -> Chroma:
    """获取 LangChain Chroma 向量存储实例 (延迟初始化).

    Chroma 原生自动处理:
      - persist_directory 不存在时自动创建
      - collection 不存在时自动创建
      - embedding_function 绑定

    Returns:
        langchain_chroma.Chroma 实例.
    """
    global _store
    if _store is None:
        embeddings = get_embeddings()
        _store = Chroma(
            embedding_function=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_name="turingmate_knowledge",
        )
        logger.info(
            f"VectorStore: Chroma 初始化完成 "
            f"(dir={settings.CHROMA_PERSIST_DIR}, collection=turingmate_knowledge)"
        )
    return _store


def reset_vectorstore():
    """重置向量存储单例（用于测试或重建场景）."""
    global _store
    _store = None


# 懒加载 — 避免模块导入时触发 embeddings 初始化（langchain_openai 导入需 ~22s）
_vectorstore_compat = None


def __getattr__(name):
    global _vectorstore_compat
    if name == "vectorstore":
        if _vectorstore_compat is None:
            _vectorstore_compat = get_vectorstore()
        return _vectorstore_compat
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
