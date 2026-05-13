"""Retriever - 混合检索 + 重排序.

检索策略：混合检索 = 向量相似度(0.7) + BM25关键词(0.3) → 可选重排序
MVP 阶段先实现向量检索，BM25 和 Reranker 后续接入。
"""

from app.rag.vectorstore import vectorstore
from app.rag.embeddings import embeddings
from app.config import settings


class Retriever:
    """混合检索器."""

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        **kwargs,
    ) -> list[dict]:
        """执行混合检索.

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表，按相关性排序
        """
        # 1. 向量相似度搜索
        query_embedding = embeddings.embed_query(query)
        vector_results = await vectorstore.similarity_search(
            query_vector=query_embedding,
            top_k=top_k,
            score_threshold=0.5,  # MVP 降低阈值保证有结果
        )

        # TODO: 2. BM25 关键词搜索（后续接入）
        # bm25_results = self._bm25_search(query, top_k=top_k)

        # TODO: 3. 混合加权 (0.7 * vector + 0.3 * bm25)

        # TODO: 4. Reranker 重排序（后续接入）

        return vector_results

    async def index_documents(self, documents: list[dict]):
        """索引文档到向量库.

        Args:
            documents: 分块后的文档列表
        """
        from app.rag.splitter import split_documents

        chunks = split_documents(documents)
        texts = [c["content"] for c in chunks]
        emb_list = embeddings.embed_documents(texts)
        await vectorstore.add_documents(chunks, emb_list)


# 全局单例
retriever = Retriever()
