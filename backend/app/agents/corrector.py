"""Corrector Agent - 手写批改 Agent.

使用 LangChain + with_structured_output() 结构化输出,
分析学生草稿纸/手写答案，给出逐步骤的评分和反馈。
"""

import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


# ── Pydantic 输出模型 ────────────────────────────────────────────


class CorrectionStep(BaseModel):
    """批改步骤."""
    step_no: int = Field(description="步骤编号")
    description: str = Field(description="步骤描述")
    is_correct: bool = Field(description="是否正确")
    score: int = Field(description="该步骤得分")
    feedback: str = Field(description="点评")


class WeakPoint(BaseModel):
    """薄弱点."""
    topic: str = Field(description="知识点")
    score: int = Field(description="掌握程度分 (0-100)")


class CorrectionResult(BaseModel):
    """结构化批改结果."""
    total_score: int = Field(description="总分")
    max_score: int = Field(default=100, description="满分")
    steps: list[CorrectionStep] = Field(default_factory=list, description="各步骤评分")
    summary: str = Field(default="", description="总体评价")
    suggestions: list[str] = Field(default_factory=list, description="改进建议")
    weak_points: list[WeakPoint] = Field(default_factory=list, description="薄弱环节")


CORRECTION_SYSTEM_PROMPT = """你是计算机考研408的专业批改老师。

请仔细分析学生手写的解题过程，输出结构化的批改结果。

## 批改要求：
1. **逐步骤评分**：每个关键步骤给分（满分根据步骤数分配）
2. **标注错误**：明确指出哪一步错了、错在哪、正确做法是什么
3. **总体评价**：总结主要问题点和优点
4. **改进建议**：针对薄弱点给出具体学习方向"""


class CorrectorAgent:
    """基于 LangChain + Structured Output 的批改 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        # 结构化 LLM — 自动解析 JSON 输出为 CorrectionResult
        self._structured_llm = self._llm.with_structured_output(CorrectionResult)
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
            批改结果字典
        """
        try:
            messages = [SystemMessage(content=CORRECTION_SYSTEM_PROMPT)]

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

            # 用 structured LLM 解析多模态返回文本
            parsed: CorrectionResult = await self._structured_llm.ainvoke(result)
            return parsed.model_dump()

        except Exception as e:
            logger.error(f"Corrector 批改失败: {e}")
            return self._fallback_result(str(e))

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
