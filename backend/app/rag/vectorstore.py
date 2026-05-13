"""Vector Store - 向量存储抽象.

统一接口，支持切换：
- 开发阶段：Chroma（本地文件存储）
- 生产阶段：腾讯云 VectorDB

MVP 阶段使用内存存储模拟。
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class BaseVectorStore(ABC):
    """向量存储基类."""

    @abstractmethod
    async def add_documents(self, documents: list[dict], embeddings: list[list[float]]):
        """添加文档向量."""
        ...

    @abstractmethod
    async def similarity_search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> list[dict]:
        """相似度搜索."""
        ...

    @abstractmethod
    async def count(self) -> int:
        """返回文档数量."""
        ...


class InMemoryVectorStore(BaseVectorStore):
    """内存向量存储 - MVP 阶段使用."""

    def __init__(self):
        self._vectors: list[np.ndarray] = []
        self._documents: list[dict] = []

    async def add_documents(self, documents: list[dict], embeddings: list[list[float]]):
        for doc, emb in zip(documents, embeddings):
            self._documents.append(doc)
            self._vectors.append(np.array(emb))

    async def similarity_search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> list[dict]:
        if not self._vectors:
            return []

        query = np.array(query_vector)
        # 余弦相似度
        norms = np.linalg.norm(self._vectors, axis=1)
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return []

        similarities = np.dot(self._vectors, query) / (norms * query_norm)

        # 按相似度排序，返回 top_k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= score_threshold:
                results.append({
                    **self._documents[idx],
                    "score": score,
                })
        return results

    async def count(self) -> int:
        return len(self._documents)


# 全局单例
vectorstore = InMemoryVectorStore()
