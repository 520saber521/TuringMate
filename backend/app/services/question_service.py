"""Question Service - 题目业务逻辑层."""
from app.crud.question import question_crud
from app.rag.retriever import retriever
from app.models.database import SessionLocal


class QuestionService:
    """题目服务."""

    async def get_question(self, question_id: str) -> dict | None:
        """从数据库获取题目详情."""
        db = SessionLocal()
        try:
            q = question_crud.get_by_id(db, question_id)
            if not q:
                return None
            return {
                "id": q.id,
                "subject": q.subject,
                "content": q.content,
                "knowledge_tags": q.knowledge_tags,
                "difficulty": q.difficulty,
                "image_url": q.image_url,
                "solution_steps": q.solution_steps,
                "variant_of": q.variant_of,
            }
        finally:
            db.close()

    async def search_similar(self, query: str, subject: str = None, limit: int = 10) -> list[dict]:
        """通过 RAG 混合检索搜索相似题目."""
        results = await retriever.retrieve(query, top_k=limit, subject=subject)
        return results


question_service = QuestionService()
