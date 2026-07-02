"""Question CRUD operations."""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_
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
               difficulty: int = 3, solution_steps: list = None, variant_of: str = None,
               year: int = None, exam_paper: str = "", chapter_order: int = None,
               source_type: str = "manual") -> Question:
        question = Question(
            id=str(uuid.uuid4())[:32],
            subject=subject,
            content=content,
            knowledge_tags=knowledge_tags or [],
            difficulty=difficulty,
            solution_steps=solution_steps or [],
            variant_of=variant_of,
            year=year,
            exam_paper=exam_paper,
            chapter_order=chapter_order,
            source_type=source_type,
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    def list_paginated(self, db: Session, subject: str = None, tag: str = None,
                       difficulty: int = None, year: int = None,
                       keyword: str = None, page: int = 1, page_size: int = 20):
        q = db.query(Question)

        if subject:
            q = q.filter(Question.subject == subject)
        if difficulty:
            q = q.filter(Question.difficulty == difficulty)
        if year:
            q = q.filter(Question.year == year)
        if keyword:
            q = q.filter(or_(
                Question.content.contains(keyword),
                Question.exam_paper.contains(keyword),
            ))
        if tag:
            # JSON array contains
            q = q.filter(Question.knowledge_tags.contains(tag))

        total = q.count()
        items = (
            q.order_by(Question.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def search_by_keywords(self, db: Session, q: str, subject: str = None, limit: int = 20):
        query = db.query(Question).filter(
            or_(
                Question.content.contains(q),
                Question.exam_paper.contains(q),
            )
        )
        if subject:
            query = query.filter(Question.subject == subject)
        return query.order_by(Question.created_at.desc()).limit(limit).all()

    def get_by_year(self, db: Session, year: int, subject: str = None,
                    page: int = 1, page_size: int = 20):
        q = db.query(Question).filter(Question.year == year)
        if subject:
            q = q.filter(Question.subject == subject)
        total = q.count()
        items = q.order_by(Question.chapter_order, Question.id).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_distinct_years(self, db: Session) -> list[int]:
        rows = db.query(Question.year).filter(Question.year.isnot(None)).distinct().order_by(Question.year).all()
        return [r[0] for r in rows if r[0]]

    def get_distinct_tags(self, db: Session, subject: str = None) -> list[str]:
        q = db.query(Question.knowledge_tags).filter(Question.knowledge_tags.isnot(None))
        if subject:
            q = q.filter(Question.subject == subject)
        tags_set = set()
        for row in q.all():
            tags = row[0]
            if isinstance(tags, list):
                tags_set.update(tags)
        return sorted(tags_set)

    def bulk_create(self, db: Session, questions_data: list[dict]) -> list[Question]:
        created = []
        for data in questions_data:
            q = Question(
                id=data.get("id", str(uuid.uuid4())[:32]),
                subject=data["subject"],
                content=data["content"],
                knowledge_tags=data.get("knowledge_tags", []),
                difficulty=data.get("difficulty", 3),
                solution_steps=data.get("solution_steps", []),
                year=data.get("year"),
                exam_paper=data.get("exam_paper", ""),
                chapter_order=data.get("chapter_order"),
                source_type=data.get("source_type", "manual"),
            )
            db.add(q)
            created.append(q)
        db.commit()
        return created


question_crud = QuestionCRUD()
