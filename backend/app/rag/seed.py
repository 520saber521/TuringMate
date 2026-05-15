"""Seed RAG Knowledge Base - 初始化知识库数据.

加载408四科知识点、PDF教材、历年真题到向量存储。

运行方式:
    # 默认（自动选择切分策略）
    python -m app.rag.seed

    # 指定语义切分
    python -m app.rag.seed --strategy semantic

    # 仅加载知识节点（跳过 PDF/真题）
    python -m app.rag.seed --knowledge-only

    # 重新构建（清空已有索引）
    python -m app.rag.seed --rebuild
"""

import asyncio
import argparse
import logging
import sys
import time
from pathlib import Path

from app.config import settings
from app.rag.loader import loader
from app.rag.splitter import split_documents, SmartSplitter
from app.rag.retriever import retriever

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 数据目录
BASE_DATA_DIR = Path(__file__).parent.parent.parent / "data"
KNOWLEDGE_DIR = BASE_DATA_DIR / "knowledge"
PDFS_DIR = BASE_DATA_DIR / "pdfs"
EXAMS_DIR = BASE_DATA_DIR / "exams"


def parse_args():
    parser = argparse.ArgumentParser(description="初始化 RAG 知识库")
    parser.add_argument(
        "--strategy", "-s",
        choices=["rule", "semantic", "auto"],
        default="auto",
        help="切分策略 (默认: auto)",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.45,
        help="语义切分相似度阈值 0~1 (默认: 0.45)",
    )
    parser.add_argument(
        "--knowledge-only",
        action="store_true",
        help="仅加载知识节点 JSON（跳过 PDF 和真题）",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="重建索引（清空已有向量库）",
    )
    return parser.parse_args()


async def seed_knowledge_base(
    strategy: str = "auto",
    threshold: float = 0.45,
    knowledge_only: bool = False,
    rebuild: bool = False,
):
    """初始化完整知识库."""
    total_start = time.time()

    logger.info("=" * 60)
    logger.info("TuringMate RAG Knowledge Base Seeder")
    logger.info(f"切分策略: {strategy}")
    if strategy == "semantic":
        logger.info(f"相似度阈值: {threshold}")

    all_documents = []
    stats = {"knowledge": 0, "pdf": 0, "exam": 0}

    # ── 1. 加载知识节点 ──────────────────────────────
    if KNOWLEDGE_DIR.exists():
        logger.info(f"\n[1/4] 加载知识节点: {KNOWLEDGE_DIR}")
        docs = loader.load_knowledge(str(KNOWLEDGE_DIR))
        all_documents.extend(docs)
        stats["knowledge"] = len(docs)
        logger.info(f"  ✓ 加载 {len(docs)} 个知识节点")
    else:
        logger.warning(f"  ✗ 知识目录不存在: {KNOWLEDGE_DIR}")

    # ── 2. 加载 PDF 教材 ────────────────────────────
    if not knowledge_only and PDFS_DIR.exists():
        logger.info(f"\n[2/4] 加载 PDF 教材: {PDFS_DIR}")
        for pdf_file in sorted(PDFS_DIR.glob("*.pdf")):
            pages = loader.load_pdf(str(pdf_file))
            for page in pages:
                page["metadata"]["source"] = pdf_file.name
            all_documents.extend(pages)
            stats["pdf"] += len(pages)
            logger.info(f"  ✓ {pdf_file.name}: {len(pages)} 页")

    elif not knowledge_only:
        logger.info(f"\n[2/4] PDF 目录不存在（跳过）: {PDFS_DIR}")
        # 尝试查找 data 目录下的散落 PDF
        scattered_pdfs = list(BASE_DATA_DIR.glob("*.pdf"))
        if scattered_pdfs:
            logger.info(f"  发现 {len(scattered_pdfs)} 个散落 PDF:")
            for pdf in scattered_pdfs:
                pages = loader.load_pdf(str(pdf))
                for page in pages:
                    page["metadata"]["source"] = pdf.name
                all_documents.extend(pages)
                stats["pdf"] += len(pages)
                logger.info(f"  ✓ {pdf.name}: {len(pages)} 页")

    # ── 3. 加载历年真题 ────────────────────────────
    if not knowledge_only and EXAMS_DIR.exists():
        logger.info(f"\n[3/4] 加载真题: {EXAMS_DIR}")
        for exam_file in sorted(EXAMS_DIR.glob("*exam*.*")):
            exams = loader.load_exam(str(exam_file))
            all_documents.extend(exams)
            stats["exam"] += len(exams)
            logger.info(f"  ✓ {exam_file.name}: {len(exams)} 道题")

    # ── 统计 ───────────────────────────────────────
    total_docs = len(all_documents)
    logger.info(f"\n{'=' * 60}")
    logger.info("文档加载汇总:")
    logger.info(f"  知识节点: {stats['knowledge']} 条")
    logger.info(f"  PDF 页面: {stats['pdf']} 页")
    logger.info(f"  真题:     {stats['exam']} 道")
    logger.info(f"  总计:     {total_docs} 条文档")

    if total_docs == 0:
        logger.error("没有可用的原始资料！请检查 data/ 目录。")
        return

    # ── 4. 文本切分 ────────────────────────────────
    logger.info(f"\n[4/{'3' if knowledge_only else '4'}] 文本切分 (策略={strategy})...")
    t_split = time.time()

    splitter = SmartSplitter(
        strategy=strategy,
        similarity_threshold=threshold,
    )
    chunks = splitter.split_documents(all_documents)

    split_time = time.time() - t_split
    rule_count = sum(1 for c in chunks if c.get("metadata", {}).get("splitter") == "rule")
    sem_count = sum(1 for c in chunks if c.get("metadata", {}).get("splitter") == "semantic")

    logger.info(f"  ✓ 切分完成 ({split_time:.2f}s)")
    logger.info(f"    规则切分: {rule_count} 块 | 语义切分: {sem_count} 块")
    logger.info(f"    总 chunk 数: {len(chunks)}")

    # ── 5. 向量化 & 存入向量库 ─────────────────────
    logger.info(f"\n向量化并建立索引...")
    t_index = time.time()

    await retriever.index_documents(chunks, rebuild=rebuild)

    index_time = time.time() - t_index
    logger.info(f"  ✓ 索引完成 ({index_time:.2f}s)")

    # ── 6. 检索测试 ────────────────────────────────
    logger.info("\n" + "-" * 60)
    logger.info("检索测试:")

    test_queries = [
        ("链表操作", "数据结构"),
        ("虚拟内存管理", "操作系统"),
        ("指令流水线", "计组"),
        ("TCP三次握手", "网络"),
        ("时间复杂度分析", "跨科"),
    ]

    for query, category in test_queries:
        try:
            results = await retriever.retrieve(query, top_k=2)
            top_score = results[0].get("score", 0) if results else 0
            content_preview = results[0].get("content", "")[:60] if results else "(无结果)"
            logger.info(f'  [{category}] "{query}" → [{top_score:.3f}] {content_preview}...')
        except Exception as e:
            logger.warning(f'  [{category}] "{query}" → 检索失败: {e}')

    # ── 完成 ───────────────────────────────────────
    total_time = time.time() - total_start
    logger.info("\n" + "=" * 60)
    logger.info(f"✓ 知识库初始化完成！总耗时 {total_time:.2f}s")
    logger.info(f"  文档: {total_docs} → Chunks: {len(chunks)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(seed_knowledge_base(
            strategy=args.strategy,
            threshold=args.threshold,
            knowledge_only=args.knowledge_only,
            rebuild=args.rebuild,
        ))
    except KeyboardInterrupt:
        logger.info("\n用户中断")
        sys.exit(1)
