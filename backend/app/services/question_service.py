"""Question Service - 题目业务逻辑层."""


class QuestionService:
    """题目服务."""

    async def get_question(self, question_id: str) -> dict | None:
        """获取题目详情."""
        # TODO: 从数据库查询
        return None

    async def search_similar(self, query: str, limit: int = 10) -> list[dict]:
        """搜索相似题目."""
        # TODO: 调用 RAG 检索或数据库查询
        return []


question_service = QuestionService()
