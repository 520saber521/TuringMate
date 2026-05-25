"""QuestionParser Agent - 题目识别与解析.

使用 LangChain ChatModel + with_structured_output(),
将图片/文本解析为结构化题目数据 (ParsedQuestion).
"""

import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


# ── Pydantic 输出模型 (用于 with_structured_output) ──────────────


class ParsedQuestion(BaseModel):
    """解析后的题目结构."""
    subject: str = Field(description="科目: 数据结构/计组/操作系统/网络")
    question_type: str = Field(description="题型: 选择/填空/解答/算法设计")
    knowledge_tags: list[str] = Field(description="知识点标签")
    difficulty: int = Field(description="难度等级 1-5", ge=1, le=5)
    content: str = Field(description="题面内容（纯文本）")
    options: Optional[list[str]] = Field(default=None, description="选择题选项")
    answer: Optional[str] = Field(default=None, description="参考答案")


PARSER_SYSTEM_PROMPT = """你是计算机考研408题目解析专家。
分析输入的内容（图片描述或文字），提取并输出结构化的题目信息。

要求：
1. 准确识别科目和数据结构/算法相关的知识点
2. 根据题目的综合复杂度判断难度(1-5)
3. 保留完整的题面原文
4. 如果无法确定某字段，用 null 或空列表"""


class QuestionParserAgent:
    """基于 LangChain + Structured Output 的题目解析 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        # 使用 with_structured_output 绑定 Pydantic 模型，LLM 自动输出结构化 JSON
        self._structured_llm = self._llm.with_structured_output(ParsedQuestion)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", PARSER_SYSTEM_PROMPT),
            ("human", "{input}"),
        ])

    async def parse_image(self, image_url: str) -> dict:
        """从图片中解析题目（多模态）.

        Args:
            image_url: 图片 URL 或本地路径

        Returns:
            ParsedQuestion 字典
        """
        try:
            messages = [
                SystemMessage(content=PARSER_SYSTEM_PROMPT),
                HumanMessage(content="请解析这张图片中的408考研题目。"),
            ]
            result = await llm_gateway.chat_with_image(messages, image_url)

            # 多模态调用返回原始文本，用 structured_llm 解析
            parsed: ParsedQuestion = await self._structured_llm.ainvoke(result)
            return parsed.model_dump()
        except Exception as e:
            logger.error(f"QuestionParser 图片解析失败: {e}")
            return {"error": f"图片解析失败: {str(e)}"}

    async def parse_text(self, text: str) -> dict:
        """从文本中解析题目.

        Args:
            text: 题目文本

        Returns:
            ParsedQuestion 字典
        """
        try:
            chain = self._prompt | self._structured_llm
            parsed: ParsedQuestion = await chain.ainvoke({"input": text})
            return parsed.model_dump()
        except Exception as e:
            logger.error(f"QuestionParser 文本解析失败: {e}")
            return {"error": f"文本解析失败: {str(e)}"}


# 全局单例
question_parser_agent = QuestionParserAgent()
