"""Corrector Agent - 手写批改 Agent.

使用 LangChain 多模态能力分析学生草稿纸/手写答案，
给出逐步骤的评分和反馈。
"""

import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_gateway import llm_gateway
from app.core.tools import image_ocr

logger = logging.getLogger(__name__)


CORRECTION_SYSTEM_PROMPT = """你是计算机考研408的专业批改老师。

请仔细分析学生手写的解题过程，按以下格式输出批改结果：

## 批改要求：
1. **逐步骤评分**：每个关键步骤给分（满分根据步骤数分配）
2. **标注错误**：明确指出哪一步错了、错在哪、正确做法是什么
3. **总体评价**：总结主要问题点和优点
4. **改进建议**：针对薄弱点给出具体学习方向

## 输出 JSON 格式：
{
  "total_score": 85,
  "max_score": 100,
  "steps": [
    {
      "step_no": 1,
      "description": "步骤描述",
      "is_correct": true/false,
      "score": 10,
      "feedback": "点评"
    }
  ],
  "summary": "总体评价",
  "suggestions": ["建议1", "建议2"],
  "weak_points": [{"topic": "知识点", "score": 70}]
}"""


class CorrectorAgent:
    """基于 LangChain 的批改 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", CORRECTION_SYSTEM_PROMPT),
            ("human", [
                {"type": "text", "text": "题目信息：{question_info}\n\n请批改下面学生的手写答案。"},
                {"type": "image_url", "image_url": {"url": "{image_url}"}}
            ]),
        ])

    async def correct(
        self,
        image_url: str,
        question_info: Optional[dict] = None,
    ) -> dict:
        """执行手写答案批改.

        Args:
            image_url: 学生手写答案图片路径或 URL
            question_info: 题目信息 {"content", "subject", "answer"}

        Returns:
            批改结果 {"total_score", "steps", "summary", ...}
        """
        try:
            # 使用多模态 LLM 分析图片
            messages = [
                SystemMessage(content=CORRECTION_SYSTEM_PROMPT),
            ]

            q_text = ""
            if question_info:
                parts = []
                if question_info.get("subject"):
                    parts.append(f"科目：{question_info['subject']}")
                if question_info.get("content"):
                    parts.append(f"题目：{question_info['content']}")
                if question_info.get("answer"):
                    parts.append(f"参考答案：{question_info['answer']}")
                q_text = "\n".join(parts)

            messages.append(HumanMessage(content=f"{q_text}\n\n请批改下面学生的手写答案（图片）。"))

            result = await llm_gateway.chat_with_image(messages, image_url)
            return self._extract_correction(result)

        except Exception as e:
            logger.error(f"Corrector 批改失败: {e}")
            return self._fallback_result(str(e))

    def _extract_correction(self, raw_response: str) -> dict:
        """从 LLM 回复中提取结构化批改结果."""
        import json, re

        try:
            data = json.loads(raw_response.strip())
            if "total_score" in data or "steps" in data:
                return data
        except json.JSONDecodeError:
            pass

        # 提取 markdown JSON
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_response)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        return self._fallback_result(raw_response[:500])

    @staticmethod
    def _fallback_result(error_msg: str = "") -> dict:
        """兜底返回."""
        return {
            "total_score": 0,
            "max_score": 100,
            "steps": [],
            "summary": f"批改服务暂时不可用: {error_msg}" if error_msg else "无法完成批改",
            "suggestions": ["请稍后重试"],
            "weak_points": [],
        }


# 全局单例
corrector_agent = CorrectorAgent()
