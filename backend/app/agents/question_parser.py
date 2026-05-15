"""QuestionParser Agent - 题目识别与解析.

使用 LangChain ChatModel + 多模态能力，将图片/文本解析为结构化题目数据。
"""

import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


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
分析输入的内容（图片描述或文字），提取并输出结构化的 JSON 题目信息。

要求：
1. 准确识别科目和数据结构/算法相关的知识点
2. 根据题目的综合复杂度判断难度(1-5)
3. 保留完整的题面原文
4. 如果无法确定某字段，用 null 或空列表"""


class QuestionParserAgent:
    """基于 LangChain 的题目解析 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
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

            # 尝试从回复中提取 JSON
            return self._extract_structured(result)
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
            chain = self._prompt | self._llm
            response = await chain.ainvoke({"input": text})
            result = response.content if hasattr(response, 'content') else str(response)
            return self._extract_structured(result)
        except Exception as e:
            logger.error(f"QuestionParser 文本解析失败: {e}")
            return {"error": f"文本解析失败: {str(e)}"}

    def _extract_structured(self, raw_response: str) -> dict:
        """从 LLM 回复中提取结构化 JSON."""
        import json
        import re

        # 尝试直接解析
        try:
            data = json.loads(raw_response.strip())
            if "subject" in data or "content" in data:
                return data
        except json.JSONDecodeError:
            pass

        # 尝试提取 markdown 代码块中的 JSON
        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_response)
        if match:
            try:
                data = json.loads(match.group(1).strip())
                return data
            except json.JSONDecodeError:
                pass

        # 尝试找到最外层 {...}
        brace_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_response)
        if brace_match:
            try:
                data = json.loads(brace_match.group(0))
                return data
            except json.JSONDecodeError:
                pass

        # 最终兜底：返回原始文本
        return {
            "subject": "未识别",
            "question_type": "未知",
            "knowledge_tags": [],
            "difficulty": 3,
            "content": raw_response[:1000],
        }


# 全局单例
question_parser_agent = QuestionParserAgent()
