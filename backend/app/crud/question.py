"""Question CRUD operations."""
import uuid
from sqlalchemy.orm import Session
from app.models.question import Question


class QuestionCRUD:
    def get_by_id(self, db: Session, question_id: str) -> Question | None:
        return db.query(Question).filter(Question.id == question_id).first()

    def list_by_subject(self, db: Session, subject: str, limit: int = 20) -> list[Question]:
        return (
            db.query(Question)
            .filter(Question.subject == subject)
            .order_by(Question.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, db: Session, subject: str, content: str, knowledge_tags: list = None,
               difficulty: int = 3, solution_steps: list = None, variant_of: str = None) -> Question:
        question = Question(
            id=str(uuid.uuid4())[:32],
            subject=subject,
            content=content,
            knowledge_tags=knowledge_tags or [],
            difficulty=difficulty,
            solution_steps=solution_steps or [],
            variant_of=variant_of,
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question


question_crud = QuestionCRUD()
