"""Text Splitter - 文本分块.

使用 RecursiveCharacterTextSplitter 策略，
chunk_size=500, overlap=50，适配中文技术文档。
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """获取文本分块器实例."""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )


def split_documents(documents: list[dict]) -> list[dict]:
    """分块文档列表.

    Args:
        documents: 文档页面列表

    Returns:
        分块后的文本列表 [{"content": str, "metadata": dict}]
    """
    splitter = get_text_splitter()
    chunks = []
    for doc in documents:
        texts = splitter.split_text(doc["content"])
        for i, text in enumerate(texts):
            chunks.append({
                "content": text,
                "metadata": {**doc.get("metadata", {}), "chunk_index": i},
            })
    return chunks
