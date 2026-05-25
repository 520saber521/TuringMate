"""TuringMate RAG Pipeline.

模块:
  - loader:          文档加载 (PyMuPDFLoader / JSONLoader / DirectoryLoader)
  - splitter:        文本切分 (RecursiveCharacterTextSplitter / SemanticChunker)
  - embeddings:      向量化模型 (OpenAI / HuggingFace / Fake)
  - vectorstore:     ChromaDB 持久化向量存储
  - retriever:       混合检索器 (EnsembleRetriever: Vector + BM25)
  - seed:            知识库初始化脚本
"""

from app.rag.loader import loader
from app.rag.splitter import (
    SmartSplitter,
    get_default_splitter,
    split_documents,
    split_text,
)
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
    "split_documents",
    "split_text",
    "get_default_splitter",
]
