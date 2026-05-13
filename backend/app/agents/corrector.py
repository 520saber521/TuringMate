"""Corrector Agent - 手写批改 Agent.

识别手写草稿中的每一步计算/推导过程，
定位具体哪一步出错并标注错误类型。
MVP 阶段返回 Mock 数据。
"""


class CorrectorAgent:
    """批改 Agent - 分析手写步骤错误."""

    async def analyze(self, image_url: str, question_id: str | None = None) -> dict:
        """分析草稿纸图片.

        Args:
            image_url: 草稿图片 URL
            question_id: 关联题目 ID（可选）

        Returns:
            每步判断结果 + 总体反馈
        """
        # TODO: 调用多模态 LLM 识别手写内容 + 逻辑判断
        return {
            "correction_id": "corr_mock_001",
            "steps": [
                {"step_no": 1, "content": "...", "is_correct": True},
                {"step_no": 2, "content": "...", "is_correct": False, "error_type": "逻辑错误"},
            ],
            "overall_feedback": "整体思路不错，第2步需要再检查一下~",
        }


corrector = CorrectorAgent()
