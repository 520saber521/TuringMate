"""Vector Store - 基于 LangChain + ChromaDB 的向量存储.

使用 langchain_chroma 的 Chroma 向量数据库：
- 持久化到本地磁盘 (data/chroma_db)
- 支持相似度搜索、元数据过滤
- 自动与 LangChain Embeddings + Retriever 集成
"""

import logging
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

# 全局 Chroma 实例（延迟初始化）
_chroma_collection = None


def get_vectorstore():
    """获取 LangChain Chroma 向量存储实例.

    Returns:
        langchain_chroma.Chroma 实例
    """
    global _chroma_collection
    if _chroma_collection is None:
        from langchain_chroma import Chroma
        from .embeddings import get_embeddings

        persist_dir = settings.CHROMA_PERSIST_DIR
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        embeddings = get_embeddings()
        _chroma_collection = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_dir,
            collection_name="turingmate_knowledge",
        )
        logger.info(f"VectorStore: Chroma 初始化完成, 持久目录={persist_dir}")
    return _chroma_collection


async def add_documents(documents: list[dict]):
    """添加文档到向量库.

    Args:
        documents: 文档列表，每项包含 "content" 和 "metadata"
    """
    from langchain_core.documents import Document

    store = get_vectorstore()

    docs = []
    for doc in documents:
        docs.append(Document(
            page_content=doc.get("content", ""),
            metadata=doc.get("metadata", {}),
        ))

    if docs:
        # 使用 Chroma 的 add_documents
        store.add_documents(docs)
        # 持久化
        try:
            store.persist()
        except Exception:
            pass  # 新版 chromadb 可能自动持久化
        logger.info(f"VectorStore: 已添加 {len(docs)} 个文档")


async def similarity_search(
    query: str,
    top_k: int = 5,
    score_threshold: float = 0.5,
    **filter_kwargs,
) -> list[dict]:
    """相似度搜索.

    Args:
        query: 查询文本
        top_k: 返回结果数量
        score_threshold: 最低相似度阈值
        **filter_kwargs: 元数据过滤条件，如 subject="数据结构"

    Returns:
        检索结果列表 [{"content", "metadata", "score"}, ...]
    """
    store = get_vectorstore()

    # 构建过滤条件
    where_filter = None
    if filter_kwargs:
        where_filter = filter_kwargs

    # 执行搜索
    results = store.similarity_search_with_score(
        query=query,
        k=top_k,
        filter=where_filter,
    )

    formatted = []
    for doc, score in results:
        # Chroma 返回的是距离（越小越近），转为相似度
        similarity = 1.0 - min(score, 1.0)  # 简单转换
        if similarity >= score_threshold:
            formatted.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": round(similarity, 4),
            })

    return formatted


async def count() -> int:
    """返回向量库中的文档总数."""
    store = get_vectorstore()
    return store.count()


async def delete_by_metadata(filter_dict: dict):
    """按元数据删除文档."""
    store = get_vectorstore()
    store.delete(where=filter_dict)
    try:
        store.persist()
    except Exception:
        pass
    logger.info(f"VectorStore: 已删除匹配 {filter_dict} 的文档")


# ── 向后兼容：保留旧的 vectorstore 变量名 ──
# 但现在返回一个兼容接口对象

class VectorStoreWrapper:
    """向后兼容的 VectorStore 包装器."""

    async def add_documents(self, documents, embeddings=None):
        await add_documents(documents)

    async def similarity_search(self, query_vector=None, query_text=None, **kwargs):
        return await similarity_search(
            query=query_text or "",
            top_k=kwargs.get("top_k", 5),
            score_threshold=kwargs.get("score_threshold", 0.7),
        )

    async def count(self):
        return await count()


vectorstore = VectorStoreWrapper()
