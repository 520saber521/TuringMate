"""Correction Service - 手写批改业务逻辑层."""
from app.services.base import BaseService
from app.agents.corrector import corrector_agent


class CorrectionService(BaseService):
    """批改服务."""

    service_name = "correction"

    @BaseService.handle_errors("correction", "批改分析失败")
    async def analyze(self, image_url: str, question_id: str | None = None) -> dict:
        """分析手写草稿."""
        self.log_info(f"批改分析: image_url={image_url}, question_id={question_id}")

        result = await corrector_agent.correct(
            image_url=image_url,
            question_info={"id": question_id} if question_id else None,
        )
        return result


correction_service = CorrectionService()