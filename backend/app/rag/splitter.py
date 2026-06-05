"""Text Splitter - 基于 LangChain 的文本切分.

使用 LangChain 原生 TextSplitter:
  - RecursiveCharacterTextSplitter: 规则切分（默认）
  - SemanticChunker (实验性): 语义切分

支持策略:
  - "rule":     RecursiveCharacterTextSplitter
  - "semantic": 基于 Embedding 的语义切分
  - "auto":     自动选择
"""

import logging
from typing import Literal, Optional
from enum import Enum

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import Language

from app.config import settings

logger = logging.getLogger(__name__)


class SplitStrategy(str, Enum):
    """切分策略."""
    RULE = "rule"
    SEMANTIC = "semantic"
    AUTO = "auto"


def get_rule_splitter() -> RecursiveCharacterTextSplitter:
    """获取规则切分器 (LangChain RecursiveCharacterTextSplitter).

    使用中文友好的分隔符: 段落 → 句子 → 短语 → 字符
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE or 500,
        chunk_overlap=settings.CHUNK_OVERLAP or 50,
        separators=[
            "\n\n",      # 段落分隔
            "\n",        # 行分隔
            "。",        # 中文句号
            "！",        # 中文感叹号
            "？",        # 中文问号
            "；",        # 中文分号
            ".",         # 英文句号
            " ",         # 空格
            "",          # 字符级兜底
        ],
    )


def get_semantic_splitter():
    """获取语义切分器.

    基于句子间 embedding 相似度检测语义边界。
    需要 langchain_experimental 的 SemanticChunker.
    """
    from .embeddings import get_embeddings

    try:
        from langchain_experimental.text_splitter import SemanticChunker
        embeddings = get_embeddings()
        return SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=45,  # 百分位阈值
        )
    except ImportError:
        logger.warning("SemanticChunker 需要安装 langchain_experimental，回退到规则切分")
        return get_rule_splitter()


class SmartSplitter:
    """智能切分器 — 自动选择最佳策略.

    Args:
        strategy: 切分策略 ("rule" | "semantic" | "auto")
    """

    def __init__(self, strategy: str = "auto"):
        self.strategy = strategy
        self._rule_splitter = get_rule_splitter()
        self._semantic_splitter = None

    def _get_semantic(self):
        if self._semantic_splitter is None:
            self._semantic_splitter = get_semantic_splitter()
        return self._semantic_splitter

    def split_text(self, text: str) -> list[str]:
        """切分单段文本."""
        if not text.strip():
            return []

        if self.strategy == "auto":
            # 短文本直接返回
            if len(text) < settings.CHUNK_SIZE * 0.8:
                return [text]
            # 长文本尝试语义切分
            splitter = self._get_semantic()
        elif self.strategy == "semantic":
            splitter = self._get_semantic()
        else:
            splitter = self._rule_splitter

        return splitter.split_text(text)

    def split_documents(self, documents: list[dict]) -> list[dict]:
        """批量切分文档列表.

        Args:
            documents: [{"content": str, "metadata": dict}]

        Returns:
            切分后的块列表 [{"content", "metadata"}, ...]
        """
        from langchain_core.documents import Document

        results = []
        for doc in documents:
            chunks = self.split_text(doc.get("content", ""))
            metadata = doc.get("metadata", {})
            for i, chunk in enumerate(chunks):
                results.append({
                    "content": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "splitter": self.strategy,
                    },
                })
        return results


# ── 全局默认实例 & 便捷函数 ──

_default_splitter: Optional[SmartSplitter] = None


def get_default_splitter() -> SmartSplitter:
    """获取全局默认切分器."""
    global _default_splitter
    if _default_splitter is None:
        _default_splitter = SmartSplitter(strategy="auto")
    return _default_splitter


def split_documents(
    documents: list[dict],
    strategy: Optional[str] = None,
) -> list[dict]:
    """便捷函数：切分文档列表."""
    if strategy is not None:
        splitter = SmartSplitter(strategy=strategy)
    else:
        splitter = get_default_splitter()
    return splitter.split_documents(documents)


def split_text(text: str, strategy: str = "auto") -> list[str]:
    """便捷函数：切分单段文本."""
    if strategy == "auto" and len(text) < (settings.CHUNK_SIZE or 500):
        return [text]
    return SmartSplitter(strategy=strategy).split_text(text)
