"""Document Loader - 基于 LangChain Document Loaders.

使用 langchain_community 原生加载器：
  - PyMuPDFLoader: PDF 教材加载（直接返回 List[Document]）
  - JSONLoader: 真题/知识点 JSON 加载
  - DirectoryLoader: 目录批量加载

所有方法统一返回 List[Document]，消除全链路的 dict→Document 转换开销。
"""

import logging
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import (
    DirectoryLoader,
    JSONLoader,
    PyMuPDFLoader,
)
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)


class DocumentLoader:
    """LangChain 文档加载器封装."""

    def load_pdf(self, pdf_path: str) -> list[Document]:
        """加载 PDF 文档 (PyMuPDFLoader).

        Args:
            pdf_path: PDF 文件路径

        Returns:
            LangChain Document 列表
        """
        try:
            loader = PyMuPDFLoader(pdf_path)
            docs = loader.load()
            logger.info(f"DocumentLoader: 加载 PDF {pdf_path}, 共 {len(docs)} 页")
            return docs
        except Exception as e:
            logger.error(f"DocumentLoader: 加载 PDF 失败 - {e}")
            return []

    def load_exam(self, exam_path: str) -> list[Document]:
        """加载真题数据 (JSONLoader).

        Args:
            exam_path: 真题 JSON 文件路径

        Returns:
            LangChain Document 列表
        """
        try:
            loader = JSONLoader(
                file_path=exam_path,
                jq_schema=".[] | {content, subject, year, difficulty}",
                text_content=False,
            )
            docs = loader.load()

            # 补充 source metadata
            for doc in docs:
                doc.metadata["source"] = exam_path

            logger.info(f"DocumentLoader: 加载真题 {exam_path}, 共 {len(docs)} 条")
            return docs
        except Exception as e:
            logger.warning(f"DocumentLoader: JSONLoader 加载失败 ({e})，回退到手动解析")
            return self._load_json_fallback(exam_path)

    def load_knowledge(self, knowledge_dir: str) -> list[Document]:
        """加载知识节点目录 (DirectoryLoader + JSON).

        Args:
            knowledge_dir: 知识点 JSON 目录

        Returns:
            LangChain Document 列表
        """
        docs = []
        knowledge_path = Path(knowledge_dir)

        if not knowledge_path.exists():
            logger.warning(f"DocumentLoader: 知识目录不存在 - {knowledge_dir}")
            return docs

        for json_file in sorted(knowledge_path.glob("*.json")):
            try:
                loader = JSONLoader(
                    file_path=str(json_file),
                    jq_schema=".[] | {id, name, subject, prerequisites, related, description}",
                    text_content=False,
                )
                file_docs = loader.load()
                # 为每个 document 添加来源标记
                for doc in file_docs:
                    doc.metadata["_source_file"] = json_file.name
                docs.extend(file_docs)
            except Exception as e:
                logger.warning(f"DocumentLoader: 加载 {json_file} 失败 - {e}")

        logger.info(f"DocumentLoader: 从 {knowledge_dir} 加载 {len(docs)} 个知识点")
        return docs

    def load_directory(
        self,
        dir_path: str,
        extensions: Optional[list[str]] = None,
    ) -> list[Document]:
        """加载目录下所有文档 (DirectoryLoader).

        Args:
            dir_path: 目录路径
            extensions: 支持的文件扩展名

        Returns:
            所有 Document 列表
        """
        path = Path(dir_path)
        if not path.exists():
            logger.warning(f"DocumentLoader: 目录不存在 - {dir_path}")
            return []

        ext_set = set(extensions or [".pdf", ".json"])
        all_docs: list[Document] = []

        # 加载 PDF
        if ".pdf" in ext_set:
            try:
                pdf_loader = DirectoryLoader(
                    path, glob="**/*.pdf", loader_cls=PyMuPDFLoader
                )
                all_docs.extend(pdf_loader.load())
            except Exception as e:
                logger.debug(f"DirectoryLoader PDF 加载跳过: {e}")

        # 加载 JSON (知识点/真题)
        if ".json" in ext_set:
            json_files = list(path.rglob("*.json"))
            for jf in json_files:
                all_docs.extend(self._load_json_fallback(str(jf)))

        logger.info(f"DocumentLoader: 从目录 {dir_path} 加载 {len(all_docs)} 个文档")
        return all_docs

    @staticmethod
    def _load_json_fallback(json_path: str) -> list[Document]:
        """JSONLoader 不可用时的手动回退."""
        import json

        docs = []
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = data if isinstance(data, list) else [data]
            for i, item in enumerate(items):
                if isinstance(item, dict):
                    content_parts = []
                    for key in ("content", "description", "name"):
                        if item.get(key):
                            content_parts.append(f"{key}: {item[key]}")

                    if content_parts:
                        docs.append(Document(
                            page_content="\n".join(content_parts),
                            metadata={
                                "source": json_path,
                                "index": i,
                                **{k: v for k, v in item.items() if k not in ("content", "description", "name")},
                            },
                        ))
        except Exception as e:
            logger.debug(f"JSON fallback 失败 {json_path}: {e}")

        return docs


loader = DocumentLoader()
