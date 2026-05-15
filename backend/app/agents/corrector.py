"""Corrector Agent - 手写批改 Agent.

识别手写草稿中的每一步计算/推导过程，
定位具体哪一步出错并标注错误类型。
已接入 LLM Gateway 多模态能力。
"""

import logging
import json
import re

from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)

CORRECTOR_SYSTEM_PROMPT = """你是 TuringMate 的手写批改专家，专门分析计算机考研408学生的草稿纸。

请仔细观察图片中的手写解题步骤，对每一步进行判断：

1. 识别出所有可辨识的解题步骤
2. 判断每一步的计算/推导是否正确
3. 对错误步骤标注错误类型和修正提示

输出 JSON 格式（不要输出其他文字）：
{
  "steps": [
    {
      "step_no": 步骤序号,
      "content": "该步骤的文字描述",
      "is_correct": true/false,
      "error_type": "错误类型（如逻辑错误/计算错误/概念错误），正确则为null",
      "hint": "修正提示，正确则为null"
    }
  ],
  "overall_feedback": "总体反馈和改进建议"
}

错误类型说明：
- 逻辑错误：推理过程有误
- 计算错误：数值计算出错
- 概念错误：对基本概念理解有误
- 遗漏步骤：缺少关键中间步骤
"""


class CorrectorAgent:
    """批改 Agent - 分析手写步骤错误."""

    def __init__(self):
        self.llm = llm_gateway

    async def analyze(self, image_url: str, question_id: str | None = None) -> dict:
        """分析草稿纸图片.

        Args:
            image_url: 草稿图片 URL 或本地路径
            question_id: 关联题目 ID（可选）

        Returns:
            每步判断结果 + 总体反馈
        """
        messages = [
            {"role": "system", "content": CORRECTOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "请分析这张草稿纸图片中的解题步骤，标注每一步是否正确。",
            },
        ]

        try:
            logger.info(f"Corrector: 开始分析图片 - {image_url}")
            raw_response = await self.llm.chat_with_image(messages, image_url)
            logger.info(f"Corrector: LLM 响应长度: {len(raw_response)}")

            parsed = self._extract_json(raw_response)
            steps = parsed.get("steps", [])

            # 校验步骤数据
            for i, step in enumerate(steps):
                step.setdefault("step_no", i + 1)
                step.setdefault("is_correct", True)
                step.setdefault("error_type", None)
                step.setdefault("hint", None)

            if not steps:
                steps = [
                    {"step_no": 1, "content": "未能识别出清晰步骤", "is_correct": True, "error_type": None, "hint": None}
                ]

            return {
                "correction_id": f"corr_{hash(image_url) % 100000:05d}",
                "question_id": question_id or "q_unknown",
                "steps": steps,
                "overall_feedback": parsed.get(
                    "overall_feedback",
                    "已分析解题过程，请查看各步骤标注。",
                ),
            }

        except Exception as e:
            logger.warning(f"Corrector: 分析失败 ({e})，返回 fallback")
            return {
                "correction_id": "corr_fallback_001",
                "question_id": question_id or "q_unknown",
                "steps": [
                    {
                        "step_no": 1,
                        "content": "图片识别暂不可用",
                        "is_correct": True,
                        "error_type": None,
                        "hint": None,
                    }
                ],
                "overall_feedback": f"批改分析暂时不可用，请稍后重试。({str(e)[:50]})",
            }

    def _extract_json(self, text: str) -> dict:
        """从 LLM 响应中提取 JSON."""
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        logger.warning(f"Corrector: 无法解析JSON，原文前200字: {text[:200]}")
        return {"steps": [], "overall_feedback": text.strip()}


corrector = CorrectorAgent()
