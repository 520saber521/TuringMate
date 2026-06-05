"""Diagnosis Service - 薄弱点诊断业务逻辑层."""
from app.agents.diagnostician import diagnostician_agent
from app.crud.diagnosis import diagnosis_crud
from app.models.database import SessionLocal


class DiagnosisService:
    """诊断服务."""

    async def generate_report(self, user_id: str) -> dict:
        """生成诊断报告."""
        report = await diagnostician_agent.diagnose(user_id)
        return report

    async def get_practice(self, user_id: str) -> list[dict]:
        """获取推荐练习，基于最新诊断报告的弱项推荐相应题目."""
        db = SessionLocal()
        try:
            report = diagnosis_crud.get_latest_report(db, user_id)
            if not report or not report.weak_points:
                return []

            from app.crud.question import question_crud

            practices = []
            for wp in report.weak_points[:3]:
                if isinstance(wp, dict) and wp.get("knowledge_tag"):
                    questions = question_crud.list_by_subject(
                        db, subject=wp.get("subject", "ds"), limit=3
                    )
                    for q in questions:
                        practices.append({
                            "id": q.id,
                            "subject": q.subject,
                            "content": q.content[:100],
                            "difficulty": q.difficulty,
                            "knowledge_tags": q.knowledge_tags,
                            "reason": f"薄弱知识点: {wp.get('knowledge_tag', '')}",
                        })
            return practices
        finally:
            db.close()


diagnosis_service = DiagnosisService()
