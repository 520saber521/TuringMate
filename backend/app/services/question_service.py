"""Question Service - 题目业务逻辑层."""
from sqlalchemy.orm import Session

from app.services.base import BaseService
from app.crud.question import question_crud
from app.rag.retriever import retriever


class QuestionService(BaseService):
    """题目服务."""

    service_name = "question"

    async def get_question(self, db: Session, question_id: str) -> dict | None:
        """从数据库获取题目详情."""
        self.log_info(f"获取题目: question_id={question_id}")

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

    @BaseService.handle_errors("question", "题目检索失败")
    async def search_similar(self, query: str, subject: str = None, limit: int = 10) -> list[dict]:
        """通过 RAG 混合检索搜索相似题目."""
        self.log_info(f"搜索相似题目: query={query[:50]}..., subject={subject}")

        results = await retriever.retrieve(query, top_k=limit, subject=subject)
        return results

    async def list_questions(
        self,
        db: Session,
        subject: str = None,
        difficulty: int = None,
        limit: int = 20,
    ) -> list[dict]:
        """获取题目列表."""
        self.log_info(f"获取题目列表: subject={subject}, difficulty={difficulty}")

        questions = question_crud.list_by_subject(
            db, subject=subject, difficulty=difficulty, limit=limit
        )
        return [
            {
                "id": q.id,
                "subject": q.subject,
                "content": q.content[:200],
                "difficulty": q.difficulty,
                "knowledge_tags": q.knowledge_tags,
            }
            for q in questions
        ]


question_service = QuestionService()