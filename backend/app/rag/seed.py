"""Seed RAG Knowledge Base - 初始化知识库数据.

加载408四科知识点 JSON 数据到向量存储，供 RAG 检索使用。
运行方式：python -m app.rag.seed
"""

import asyncio
import logging
import sys
from pathlib import Path

from app.rag.loader import loader
from app.rag.retriever import retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"


async def seed_knowledge_base():
    """初始化知识库."""
    logger.info("=" * 50)
    logger.info("开始初始化 RAG 知识库...")
    logger.info(f"知识目录: {KNOWLEDGE_DIR}")

    if not KNOWLEDGE_DIR.exists():
        logger.error(f"知识目录不存在: {KNOWLEDGE_DIR}")
        return

    # 1. 加载知识点文档
    documents = loader.load_knowledge(str(KNOWLEDGE_DIR))
    logger.info(f"加载了 {len(documents)} 个知识节点文档")

    if not documents:
        logger.warning("没有加载到任何文档，退出")
        return

    # 2. 索引到向量库
    await retriever.index_documents(documents)
    logger.info(f"成功索引 {len(documents)} 个文档到向量库")

    # 3. 测试检索
    test_query = "链表删除操作"
    results = await retriever.retrieve(test_query, top_k=3)
    logger.info(f"\n测试检索 '{test_query}':")
    for r in results:
        logger.info(f"  - [{r.get('score', 0):.3f}] {r.get('content', '')[:80]}...")

    # 4. 测试跨科检索
    cross_query = "内存管理虚拟内存"
    results2 = await retriever.retrieve(cross_query, top_k=3)
    logger.info(f"\n测试检索 '{cross_query}':")
    for r in results2:
        logger.info(f"  - [{r.get('score', 0):.3f}] {r.get('content', '')[:80]}...")

    logger.info("=" * 50)
    logger.info("知识库初始化完成！")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())
