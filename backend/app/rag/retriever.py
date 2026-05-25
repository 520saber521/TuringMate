"""Retriever - 基于 LangChain EnsembleRetriever 的混合检索器.

完整 RAG 管线:
  1. ChromaDB 向量相似度搜索 (langchain_chroma)
  2. BM25 关键词搜索 (langchain_community.BM25Retriever)
  3. EnsembleRetriever 原生混合融合
  4. 格式化检索结果输出

替代之前的手动 BM25 实现 (_bm25_search ~40行) 和手动合并逻辑.
"""

import logging
from typing import Optional

from app.config import settings
from .vectorstore import get_vectorstore
from .splitter import split_documents

logger = logging.getLogger(__name__)


class HybridRetriever:
    """LangChain EnsembleRetriever 混合检索器.

    使用原生 BM25Retriever + Chroma Retriever + EnsembleRetriever，
    替代手动实现的 BM25 算法和合并排序逻辑。
    """

    def __init__(self):
        self._vectorstore = None
        self._bm25_retriever = None  # langchain_community.retrievers.BM25Retriever
        self._ensemble_retriever = None  # langchain.retrievers.EnsembleRetriever
        self._bm25_corpus: list[str] = []  # 用于重建 BM25Retriever

    def _get_vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = get_vectorstore()
        return self._vectorstore

    def _get_ensemble(self, query: str = "", top_k: int = 5):
        """获取或创建 EnsembleRetriever."""
        store = self._get_vectorstore()

        # 向量检索器
        vec_retriever = store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )

        bm25_weight = getattr(settings, "RERANK_WEIGHT_BM25", 0.3)

        # 如果不需要 BM25 或没有语料，直接返回向量检索器
        if bm25_weight <= 0 or not self._bm25_corpus or not self._bm25_retriever:
            return vec_retriever

        # 使用 LangChain 原生 EnsembleRetriever
        if self._ensemble_retriever is None:
            from langchain.retrievers import EnsembleRetriever

            self._ensemble_retriever = EnsembleRetriever(
                retrievers=[vec_retriever, self._bm25_retriever],
                weights=[1.0 - bm25_weight, bm25_weight],
            )
        return self._ensemble_retriever

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
            **kwargs: subject 过滤等

        Returns:
            检索结果列表 [{"content", "metadata", "score"}, ...]
        """
        store = self._get_vectorstore()

        # 构建过滤条件
        where_filter = None
        if kwargs.get("subject"):
            where_filter = {"subject": kwargs["subject"]}

        # ── 有过滤条件时用向量库原生搜索（EnsembleRetriever 不支持 where filter）──
        if where_filter:
            results_with_scores = store.similarity_search_with_score(
                query=query,
                k=top_k,
                filter=where_filter,
            )
            return self._format_results(results_with_scores, source="vector")

        # ── 无过滤条件时用 EnsembleRetriever 混合检索 ──
        ensemble = self._get_ensemble(query, top_k)

        try:
            docs = ensemble.invoke(query)
            # EnsembleRetriever 不返回分数，统一给默认高分
            return [{
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": 0.85,  # Ensemble 结果均为高相关
                "_source": "ensemble",
            } for doc in docs[:top_k]]
        except Exception as e:
            logger.debug(f"EnsembleRetriever 搜索失败 ({e})，回退到纯向量搜索")
            results_with_scores = store.similarity_search_with_score(
                query=query, k=top_k,
            )
            return self._format_results(results_with_scores, source="vector_fallback")

    async def index_documents(self, documents: list[dict], rebuild=False):
        """索引文档到向量库.

        Args:
            documents: 文档列表 (支持 dict 或 LangChain Document)
            rebuild: 是否清空重建
        """
        from langchain_core.documents import Document

        store = self._get_vectorstore()

        if rebuild:
            try:
                store.delete_collection()
                logger.info("Retriever: 已清空向量库")
            except Exception as e:
                logger.warning(f"Retriever: 清空失败 ({e})")

        # 统一转换为 Document 对象
        langchain_docs = []
        for doc in documents:
            if isinstance(doc, Document):
                langchain_docs.append(doc)
            elif isinstance(doc, dict):
                langchain_docs.append(Document(
                    page_content=doc.get("content", ""),
                    metadata=doc.get("metadata", {}),
                ))

        # 如果还没切分，先做切分
        if not langchain_docs or any(
            len(d.page_content) > (settings.CHUNK_SIZE or 500) * 1.5
            for d in langchain_docs
        ):
            chunks = split_documents([
                d.dict() if hasattr(d, "dict") else {"content": d.page_content, "metadata": d.metadata}
                if isinstance(d, Document) else d
                for d in langchain_docs
            ])
            langchain_docs = [
                Document(page_content=c["content"], metadata=c["metadata"])
                for c in chunks
            ]

        if langchain_docs:
            store.add_documents(langchain_docs)
            try:
                store.persist()
            except Exception:
                pass

            # 重建 BM25Retriever 语料库
            self._bm25_corpus = [doc.page_content for doc in langchain_docs]
            self._rebuild_bm25_retriever()

            logger.info(f"Retriever: 已索引 {len(langchain_docs)} 个文档块")

    def _rebuild_bm25_retriever(self):
        """从语料库重建 BM25Retriever."""
        if not self._bm25_corpus:
            self._bm25_retriever = None
            self._ensemble_retriever = None
            return

        try:
            from langchain_community.retrievers import BM25Retriever

            self._bm25_retriever = BM25Retriever.from_texts(
                self._bm25_corpus, k=5
            )
            # 重置 ensemble 缓存，下次 retrieve 时自动重建
            self._ensemble_retriever = None
            logger.info(f"Retriever: BM25Retriever 已重建，语料 {len(self._bm25_corpus)} 条")
        except ImportError:
            logger.warning("BM25Retriever 需要 rank_bm25 包，BM25 功能禁用")
            self._bm25_retriever = None

    @staticmethod
    def _format_results(results_with_scores, source: str = "vector") -> list[dict]:
        """将 Chroma similarity_search_with_score 结果格式化."""
        formatted = []
        for doc, raw_score in results_with_scores:
            similarity = max(0.0, 1.0 - min(raw_score, 1.0))
            formatted.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": round(similarity, 4),
                "_source": source,
            })
        return formatted

    @property
    def as_langchain_retriever(self):
        """返回 LangChain 兼容的 Retriever 对象."""
        store = self._get_vectorstore()
        return store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )


# 全局单例
retriever = HybridRetriever()
