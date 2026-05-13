"""Diagnosis Service - 薄弱点诊断业务逻辑层."""
from app.agents.diagnostician import diagnostician


class DiagnosisService:
    """诊断服务."""

    async def generate_report(self, user_id: str) -> dict:
        """生成诊断报告."""
        report = await diagnostician.generate_report(user_id)
        return report

    async def get_practice(self, user_id: str) -> list[dict]:
        """获取练习推荐."""
        # TODO: 基于诊断报告推荐
        return []


diagnosis_service = DiagnosisService()
