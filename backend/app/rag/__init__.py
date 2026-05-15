"""TuringMate RAG Pipeline.

模块:
  - loader:          文档加载（PDF / JSON 知识点 / 真题）
  - splitter:        文本切分（规则 / 语义混合策略）
  - semantic_splitter: Embedding 语义切分器
  - embeddings:      向量化模型（DeepSeek API / sentence-transformers / Mock）
  - vectorstore:     向量存储
  - retriever:       检索器
  - seed:            知识库初始化脚本
"""

from app.rag.loader import loader
from app.rag.splitter import (
    SmartSplitter,
    get_default_splitter,
    split_documents,
    split_text,
)
from app.rag.semantic_splitter import SemanticSplitter, create_semantic_splitter
from app.rag.embeddings import create_embeddings, get_embeddings, embeddings
from app.rag.vectorstore import vectorstore
from app.rag.retriever import retriever

__all__ = [
    # Core
    "loader",
    "retriever",
    "vectorstore",
    "embeddings",
    "get_embeddings",
    "create_embeddings",
    # Splitting
    "SmartSplitter",
    "SemanticSplitter",
    "create_semantic_splitter",
    "split_documents",
    "split_text",
    "get_default_splitter",
]
