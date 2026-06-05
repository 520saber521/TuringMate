"""Diagnosis CRUD operations."""
import uuid
from sqlalchemy.orm import Session
from app.models.diagnosis import Mistake, DiagnosisReport


class DiagnosisCRUD:
    def create_report(self, db: Session, user_id: str, scores: dict,
                      weak_points: list = None, recommendations: list = None) -> DiagnosisReport:
        report = DiagnosisReport(
            id=str(uuid.uuid4())[:32],
            user_id=user_id,
            scores=scores,
            weak_points=weak_points or [],
            recommendations=recommendations or [],
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def get_latest_report(self, db: Session, user_id: str) -> DiagnosisReport | None:
        return (
            db.query(DiagnosisReport)
            .filter(DiagnosisReport.user_id == user_id)
            .order_by(DiagnosisReport.generated_at.desc())
            .first()
        )

    def list_by_user(self, db: Session, user_id: str, limit: int = 10) -> list[DiagnosisReport]:
        return (
            db.query(DiagnosisReport)
            .filter(DiagnosisReport.user_id == user_id)
            .order_by(DiagnosisReport.generated_at.desc())
            .limit(limit)
            .all()
        )

    def create_mistake(self, db: Session, user_id: str, question_id: str = None,
                       user_answer: str = None, error_step: int = None,
                       error_type: str = "", knowledge_tags: list = None) -> Mistake:
        mistake = Mistake(
            id=str(uuid.uuid4())[:32],
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer,
            error_step=error_step,
            error_type=error_type,
            knowledge_tags=knowledge_tags or [],
        )
        db.add(mistake)
        db.commit()
        db.refresh(mistake)
        return mistake

    def list_mistakes_by_user(self, db: Session, user_id: str, limit: int = 50) -> list[Mistake]:
        return (
            db.query(Mistake)
            .filter(Mistake.user_id == user_id)
            .order_by(Mistake.created_at.desc())
            .limit(limit)
            .all()
        )


diagnosis_crud = DiagnosisCRUD()
