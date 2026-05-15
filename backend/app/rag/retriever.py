"""Retriever - 基于 LangChain 的混合检索器.

完整 RAG 管线:
  1. ChromaDB 向量相似度搜索 (langchain_chroma)
  2. BM25 关键词搜索 (可选)
  3. 混合加权 + 重排序
  4. 输出格式化检索结果

与 LangChain Chain 集成：
  - 可作为 RetrieverTool 被 Agent 调用
  - 可用于 create_retrieval_chain 构建 QA Chain
"""

import logging
from typing import Optional

from app.config import settings
from .vectorstore import get_vectorstore
from .splitter import split_documents

logger = logging.getLogger(__name__)


class HybridRetriever:
    """LangChain 混合检索器.

    整合向量搜索 + BM25（可选）+ 重排序，
    提供统一的检索接口供 Agent 和 API 使用。
    """

    def __init__(self):
        self._vectorstore = None
        self._bm25_corpus: list[str] = []  # BM25 语料库

    def _get_vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = get_vectorstore()
        return self._vectorstore

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

        # ── 1. 向量相似度搜索 ──
        results_with_scores = store.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=where_filter,
        )

        vector_results = []
        for doc, raw_score in results_with_scores:
            # Chroma 返回距离 → 转为相似度 (0~1)
            similarity = max(0.0, 1.0 - min(raw_score, 1.0))
            vector_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": round(similarity, 4),
                "_source": "vector",
            })

        # ── 2. BM25 关键词搜索（如果可用）──
        bm25_weight = getattr(settings, "RERANK_WEIGHT_BM25", 0.3)
        if bm25_weight > 0 and self._bm25_corpus:
            try:
                bm25_results = await self._bm25_search(query, top_k=top_k)
                # 合并去重 + 加权融合
                vector_results = self._merge_and_rerank(
                    vector_results, bm25_results,
                    vec_weight=(1.0 - bm25_weight),
                    bm25_weight=bm25_weight,
                )
            except Exception as e:
                logger.debug(f"BM25 搜索跳过: {e}")

        # ── 3. 按最终得分排序，返回 top_k ──
        vector_results.sort(key=lambda x: x["score"], reverse=True)
        return vector_results[:top_k]

    async def index_documents(self, documents: list[dict], rebuild=False):
        """索引文档到向量库.

        Args:
            documents: 文档列表 [{"content": str, "metadata": dict}]
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

        # 使用 LangChain splitter 切分
        chunks = split_documents(documents)

        langchain_docs = []
        for chunk in chunks:
            langchain_docs.append(Document(
                page_content=chunk.get("content", ""),
                metadata=chunk.get("metadata", {}),
            ))

        if langchain_docs:
            # 直接使用 Chroma add_documents
            store.add_documents(langchain_docs)
            try:
                store.persist()
            except Exception:
                pass

            # 更新 BM25 语料库
            self._bm25_corpus = [doc.page_content for doc in langchain_docs]

            logger.info(f"Retriever: 已索引 {len(langchain_docs)} 个文档块")

    async def _bm25_search(self, query: str, top_k: int = 5) -> list[dict]:
        """BM25 关键词搜索."""
        import math
        from collections import Counter

        if not self._bm25_corpus:
            return []

        # 简易 BM25 实现
        query_terms = query.lower().split()
        k1 = 1.5
        b = 0.75
        avg_dl = sum(len(d.split()) for d in self._bm25_corpus) / len(self._bm25_corpus)

        scores = []
        for idx, doc in enumerate(self._bm25_corpus):
            doc_terms = doc.lower().split()
            dl = len(doc_terms)
            term_freqs = Counter(doc_terms)
            score = 0.0
            for q_term in query_terms:
                tf = term_freqs.get(q_term, 0)
                df = sum(1 for d in self._bm25_corpus if q_term in d.lower().split())
                idf = math.log((len(self._bm25_corpus) - df + 0.5) / (df + 0.5) + 1.0)
                score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
            if score > 0:
                scores.append({"index": idx, "score": score})

        scores.sort(key=lambda x: x["score"], reverse=True)
        results = []
        for item in scores[:top_k]:
            idx = item["index"]
            results.append({
                "content": self._bm25_corpus[idx],
                "metadata": {},
                "score": min(item["score"] / 10.0, 1.0),  # 归一化
                "_source": "bm25",
            })
        return results

    @staticmethod
    def _merge_and_rerank(
        vector_results: list[dict],
        bm25_results: list[dict],
        vec_weight: float = 0.7,
        bm25_weight: float = 0.3,
    ) -> list[dict]:
        """合并并重新排序两个来源的结果.

        按 content 匹配合并分数.
        """
        merged = {}
        for r in vector_results:
            key = r["content"][:100]  # 用前 100 字符作为键
            merged[key] = {**r, "final_score": r["score"] * vec_weight}

        for r in bm25_results:
            key = r["content"][:100]
            if key in merged:
                merged[key]["final_score"] += r["score"] * bm25_weight
            else:
                merged[key] = {
                    **r,
                    "final_score": r["score"] * bm25_weight,
                }

        result_list = list(merged.values())
        for r in result_list:
            r["score"] = round(r.pop("final_score", r.get("score", 0)), 4)

        return result_list

    @property
    def as_langchain_retriever(self):
        """返回 LangChain 兼容的 Retriever 对象.

        可直接传入 create_retrieval_chain() 或 LLM.bind_tools().
        """
        store = self._get_vectorstore()
        return store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )


# 全局单例
retriever = HybridRetriever()
