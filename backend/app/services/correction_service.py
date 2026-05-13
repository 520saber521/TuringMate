"""Correction Service - 手写批改业务逻辑层."""
from app.agents.corrector import corrector


class CorrectionService:
    """批改服务."""

    async def analyze(self, image_url: str, question_id: str | None = None) -> dict:
        """分析手写草稿."""
        result = await corrector.analyze(image_url, question_id)
        return result


correction_service = CorrectionService()
