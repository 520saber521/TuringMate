"""Embeddings - Embedding 模型抽象.

可插拔接口：
- 开发阶段：text2vec-base-chinese (本地模型)
- 生产阶段：可切换为云端模型（Cohere/OpenAI Embeddings）
"""

from abc import ABC, abstractmethod
import numpy as np


class BaseEmbeddings(ABC):
    """Embedding 模型基类."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """嵌入查询文本."""
        ...

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """嵌入文档列表."""
        ...


class MockEmbeddings(BaseEmbeddings):
    """Mock Embedding - MVP 阶段使用随机向量."""

    dimension = 384

    def embed_query(self, text: str) -> list[float]:
        # 生成基于文本哈希的伪随机向量（保证相同文本向量一致）
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.dimension).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]


# 全局单例，后续替换为真实模型
embeddings = MockEmbeddings()
