"""Semantic Splitter - 基于 Embedding 的语义切分器.

核心原理:
  1. 文本 → 句子级切分
  2. 每句 → Embedding 向量
  3. 计算相邻句子的余弦相似度
  4. 相似度低于阈值 → 检测到语义边界 → 在此切分
  5. 边界内句子合并为 chunk

对比规则切分的优势:
  - 规则: 按"。" 或固定字数断开，可能从知识点中间切断
  - 语义: 按"话题转换点"断开，每个 chunk 是完整知识单元
"""

from __future__ import annotations

import re
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class SemanticSplitter:
    """基于 Embedding 相似度的语义文本切分器.

    Args:
        embeddings: Embedding 模型实例（需实现 embed_documents）
        similarity_threshold: 相似度低于此值则判定为边界 (0~1)
            越高越激进地切分（chunk 更小更精准），越低 chunk 越大
        max_chunk_size: 单个 chunk 最大字符数（安全兜底）
        min_chunk_size: 单个 chunk 最小字符数（过小的合并到前一个）
        sentence_delimiters: 中文句子分割正则
    """

    def __init__(
        self,
        embeddings,  # BaseEmbeddings 实例
        similarity_threshold: float = 0.45,
        max_chunk_size: int = 800,
        min_chunk_size: int = 50,
        sentence_delimiters: str | None = None,
    ):
        self._embeddings = embeddings
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        # 默认中文句子分隔符
        self._delimiter_pattern = (
            sentence_delimiters
            or r'(?<=[。！？\n])\s*'
        )

    def split_text(self, text: str) -> list[str]:
        """将单段文本按语义边界切分为多个 chunk.

        Args:
            text: 原始文档文本

        Returns:
            切分后的文本块列表，每块是一个完整的语义单元
        """
        if not text or len(text.strip()) < self.min_chunk_size:
            return [text] if text.strip() else []

        # Step 1: 句子级预切分
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return [text]

        logger.debug(f"SemanticSplitter: 预切分为 {len(sentences)} 个句子")

        # Step 2: Embedding 向量化
        try:
            embeddings_matrix = self._embeddings.embed_documents(sentents)
            vectors = np.array(embeddings_matrix, dtype=np.float32)
        except Exception as e:
            logger.warning(f"SemanticSplitter: Embedding 失败 ({e})，回退到规则切分")
            return self._fallback_split(text)

        # Step 3: 计算相邻句子相似度
        similarities = self._compute_similarities(vectors)
        logger.debug(
            f"SemanticSplitter: 相似度范围 [{min(similarities):.3f}, {max(similarities):.3f}], "
            f"阈值={self.similarity_threshold}"
        )

        # Step 4: 检测语义边界
        break_points = self._detect_boundaries(similarities, sentences)

        # Step 5: 合并为 chunks
        chunks = self._merge_chunks(sentences, break_points)

        # Step 6: 后处理 — 过小/过大的 chunk
        chunks = self._postprocess(chunks, text)

        logger.debug(f"SemanticSplitter: 最终生成 {len(chunks)} 个 chunks")
        return chunks

    def split_documents(self, documents: list[dict]) -> list[dict]:
        """批量切分文档列表.

        Args:
            documents: [{"content": str, "metadata": dict}]

        Returns:
            切分后的文档块列表
        """
        results = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            chunks = self.split_text(content)
            for i, chunk in enumerate(chunks):
                results.append({
                    "content": chunk,
                    "metadata": {**metadata, "chunk_index": i, "splitter": "semantic"},
                })
        return results

    # ================================================================
    # 内部方法
    # ================================================================

    def _split_sentences(self, text: str) -> list[str]:
        """将文本按中文句子分隔符切分."""
        raw_parts = re.split(self._delimiter_pattern, text)
        sentences = []
        for part in raw_parts:
            part = part.strip()
            if part:
                sentences.append(part)
        return sentences

    @staticmethod
    def _compute_similarities(vectors: np.ndarray) -> list[float]:
        """计算相邻向量对的余弦相似度."""
        similarities = []
        for i in range(len(vectors) - 1):
            v1, v2 = vectors[i], vectors[i + 1]
            cos_sim = np.dot(v1, v) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            similarities.append(float(cos_sim))
        return similarities

    def _detect_boundaries(
        self,
        similarities: list[float],
        sentences: list[str],
    ) -> list[int]:
        """检测语义边界位置.

        返回需要在此处断开的句子索引列表.
        """
        boundaries = []

        for i, sim in enumerate(similarities):
            # 策略 1: 相似度低于阈值 → 语义断裂
            is_boundary = sim < self.similarity_threshold

            # 策略 2: 累积长度超限强制断开（安全兜底）
            current_start = boundaries[-1] if boundaries else 0
            accumulated_len = sum(len(s) for s in sentences[current_start : i + 1])
            force_break = accumulated_len >= self.max_chunk_size

            if is_boundary or force_break:
                boundaries.append(i + 1)  # 在 i+1 之前断开

        return boundaries

    def _merge_chunks(
        self,
        sentences: list[str],
        break_points: list[int],
    ) -> list[str]:
        """根据断点合并句子为 chunk."""
        chunks = []
        start = 0
        for bp in break_points:
            chunk_text = "".join(sentences[start:bp]).strip()
            if chunk_text:
                chunks.append(chunk_text)
            start = bp
        # 最后一个 chunk
        if start < len(sentences):
            chunk_text = "".join(sentences[start:]).strip()
            if chunk_text:
                chunks.append(chunk_text)
        return chunks

    def _postprocess(self, chunks: list[str], original_text: str) -> list[str]:
        """后处理：合并过小 chunk、拆分过大 chunk."""
        processed = []
        i = 0
        while i < len(chunks):
            chunk = chunks[i]

            # 过小 chunk 合并到前一个
            if len(chunk) < self.min_chunk_size and processed:
                processed[-1] += "\n" + chunk
                i += 1
                continue

            # 过大 chunk 递归再切
            if len(chunk) > self.max_chunk_size * 1.5:
                sub_chunks = self.split_text(chunk[: self.max_chunk_size])
                processed.extend(sub_chunks)
                remainder = chunk[self.max_chunk_size :]
                if remainder.strip():
                    # 把剩余部分插回待处理
                    chunks.insert(i + 1, remainder)
                i += 1
                continue

            processed.append(chunk)
            i += 1

        # 如果后处理全吃掉了，返回原文
        if not processed:
            return [original_text]
        return processed

    def _fallback_split(self, text: str) -> list[str]:
        """Embedding 失败时回退到规则切分."""
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.max_chunk_size,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
        )
        return splitter.split_text(text)


# ============================================================
# 便捷函数
# ============================================================


def create_semantic_splitter(
    threshold: float = 0.45,
    max_chunk_size: int = 800,
) -> SemanticSplitter:
    """创建语义切分器的工厂函数（自动使用全局 Embedding）."""
    from .embeddings import get_embeddings

    return SemanticSplitter(
        embeddings=get_embeddings(),
        similarity_threshold=threshold,
        max_chunk_size=max_chunk_size,
    )
