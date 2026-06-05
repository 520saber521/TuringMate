"""Correction Service - 手写批改业务逻辑层."""
from app.agents.corrector import corrector_agent


class CorrectionService:
    """批改服务."""

    async def analyze(self, image_url: str, question_id: str | None = None) -> dict:
        """分析手写草稿."""
        result = await corrector_agent.correct(
            image_url=image_url,
            question_info={"id": question_id} if question_id else None,
        )
        return result


correction_service = CorrectionService()
