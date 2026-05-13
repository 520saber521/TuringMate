"""Document Loader - 文档加载.

支持 408 教材 PDF (PyMuPDF)、历年真题解析、结构化知识点数据。
MVP 阶段先实现 PDF 加载框架。
"""


class DocumentLoader:
    """文档加载器."""

    def load_pdf(self, pdf_path: str) -> list[dict]:
        """加载 PDF 文档.

        Args:
            pdf_path: PDF 文件路径

        Returns:
            文档页面列表 [{"page": int, "content": str, "metadata": dict}]
        """
        # TODO: 使用 PyMuPDF 解析 PDF
        # import fitz
        # doc = fitz.open(pdf_path)
        # pages = []
        # for i, page in enumerate(doc):
        #     pages.append({"page": i+1, "content": page.get_text(), "metadata": {}})
        # return pages
        return []

    def load_exam(self, exam_path: str) -> list[dict]:
        """加载真题数据."""
        # TODO: 实现真题解析器
        return []

    def load_knowledge(self, knowledge_dir: str) -> list[dict]:
        """加载结构化知识节点."""
        # TODO: 加载 JSON 知识图谱数据
        return []


loader = DocumentLoader()
