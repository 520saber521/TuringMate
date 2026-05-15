"""Document Loader - 文档加载.

支持 408 教材 PDF (PyMuPDF)、历年真题解析、结构化知识点数据。
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentLoader:
    """文档加载器 - 支持 PDF 和 JSON 知识点加载."""

    def load_pdf(self, pdf_path: str) -> list[dict]:
        """加载 PDF 文档.

        Args:
            pdf_path: PDF 文件路径

        Returns:
            文档页面列表 [{"page": int, "content": str, "metadata": dict}]
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            pages = []
            for i, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    pages.append({
                        "page": i + 1,
                        "content": text.strip(),
                        "metadata": {"source": pdf_path, "page": i + 1},
                    })
            logger.info(f"DocumentLoader: 加载 PDF {pdf_path}, 共 {len(pages)} 页")
            return pages
        except ImportError:
            logger.warning("DocumentLoader: PyMuPDF 未安装，无法解析 PDF")
            return []
        except Exception as e:
            logger.error(f"DocumentLoader: 加载 PDF 失败 - {e}")
            return []

    def load_exam(self, exam_path: str) -> list[dict]:
        """加载真题数据 (JSON 格式).

        Args:
            exam_path: 真题 JSON 文件路径

        Returns:
            题目文档列表
        """
        import json

        try:
            path = Path(exam_path)
            if not path.exists():
                logger.warning(f"DocumentLoader: 真题文件不存在 - {exam_path}")
                return []

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return [
                    {
                        "page": i + 1,
                        "content": item.get("content", ""),
                        "metadata": {
                            "source": exam_path,
                            "subject": item.get("subject", ""),
                            "year": item.get("year", ""),
                            "difficulty": item.get("difficulty", 3),
                        },
                    }
                    for i, item in enumerate(data)
                    if item.get("content")
                ]
            return []
        except Exception as e:
            logger.error(f"DocumentLoader: 加载真题失败 - {e}")
            return []

    def load_knowledge(self, knowledge_dir: str) -> list[dict]:
        """加载结构化知识节点.

        Args:
            knowledge_dir: 知识点 JSON 目录

        Returns:
            知识点文档列表
        """
        import json

        docs = []
        knowledge_path = Path(knowledge_dir)

        if not knowledge_path.exists():
            logger.warning(f"DocumentLoader: 知识目录不存在 - {knowledge_dir}")
            return docs

        for json_file in knowledge_path.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    nodes = json.load(f)

                if isinstance(nodes, list):
                    for node in nodes:
                        # 将知识节点转为文档
                        content_parts = [f"知识点：{node.get('name', '')}"]

                        if node.get("prerequisites"):
                            prereq_names = node.get("prerequisites", [])
                            content_parts.append(f"前置知识：{', '.join(prereq_names)}")

                        if node.get("related"):
                            related_names = node.get("related", [])
                            content_parts.append(f"关联知识：{', '.join(related_names)}")

                        docs.append({
                            "page": 0,
                            "content": "\n".join(content_parts),
                            "metadata": {
                                "source": json_file.name,
                                "subject": node.get("subject", ""),
                                "node_id": node.get("id", ""),
                            },
                        })
            except Exception as e:
                logger.error(f"DocumentLoader: 加载知识点文件失败 - {json_file}: {e}")

        logger.info(f"DocumentLoader: 从 {knowledge_dir} 加载 {len(docs)} 个知识点")
        return docs

    def load_directory(self, dir_path: str, extensions: list[str] | None = None) -> list[dict]:
        """加载目录下所有文档.

        Args:
            dir_path: 目录路径
            extensions: 支持的文件扩展名

        Returns:
            所有文档列表
        """
        path = Path(dir_path)
        if not path.exists():
            logger.warning(f"DocumentLoader: 目录不存在 - {dir_path}")
            return []

        ext_set = set(extensions or [".pdf", ".json"])
        all_docs = []

        for file_path in path.rglob("*"):
            if file_path.suffix.lower() in ext_set:
                if file_path.suffix == ".pdf":
                    all_docs.extend(self.load_pdf(str(file_path)))
                elif file_path.suffix == ".json":
                    # JSON 文件可能是知识点或真题
                    all_docs.extend(self.load_knowledge(str(file_path.parent)))
                    break  # 避免重复加载

        return all_docs


loader = DocumentLoader()
