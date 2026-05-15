"""QuestionParser Agent - 题目识别 Agent.

调用多模态 LLM (DeepSeek / GPT-4o / 通义VL) 解析图片中的题目，
输出结构化的题目信息：科目、知识点、难度、题面内容。
"""

import logging
import json
import re

from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)

# 系统提示词 - 引导多模态 LLM 输出结构化 JSON
QUESTION_PARSE_SYSTEM_PROMPT = """你是 TuringMate 的题目识别专家，专门解析计算机考研408科目的题目图片。

请仔细观察图片中的题目内容，输出以下 JSON 格式（不要输出其他任何文字）：
{
  "subject": "科目（必须是：数据结构、计组、操作系统、网络 之一）",
  "knowledge_tags": ["知识点1", "知识点2"],
  "difficulty": 难度等级（1-5的整数，1最简单5最难）,
  "content": "完整的题目文字描述，包含所有条件和问题"
}

判断规则：
- subject: 根据题目涉及的核心概念判断
- knowledge_tags: 提取2-4个关键知识点
- difficulty: 基础概念填空=1-2, 综合应用=3, 算法设计/综合分析=4-5
- content: 必须完整准确，不要省略条件或问题描述
"""


class QuestionParserAgent:
    """题目识别 Agent - 解析图片中的考题."""

    def __init__(self):
        self.llm = llm_gateway

    async def parse_image(self, image_path: str | None = None, image_url: str | None = None) -> dict:
        """解析图片中的题目.

        Args:
            image_path: 本地图片文件路径
            image_url: 图片 URL

        Returns:
            结构化题目信息 dict
        """
        messages = [
            {"role": "system", "content": QUESTION_PARSE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "请识别这张图片中的计算机考研408题目，输出结构化JSON。",
            },
        ]

        try:
            src = image_path or image_url
            if not src:
                raise ValueError("必须提供 image_path 或 image_url")

            logger.info(f"QuestionParser: 开始识别图片 - {src}")

            # 尝试多模态调用
            raw_response = await self.llm.chat_with_image(messages, src)
            logger.info(f"QuestionParser: LLM 多模态响应长度: {len(raw_response)}")

            # 解析 JSON
            parsed = self._extract_json(raw_response)

            # 补充 question_id 和校验
            parsed["question_id"] = f"q_{hash(parsed.get('content', '')) % 100000:05d}"

            # 校验必要字段
            if not parsed.get("content"):
                parsed["content"] = raw_response

            valid_subjects = ["数据结构", "计组", "操作系统", "网络"]
            if parsed.get("subject") not in valid_subjects:
                parsed["subject"] = "数据结构"  # 默认值

            if not isinstance(parsed.get("difficulty"), int) or not (1 <= parsed["difficulty"] <= 5):
                parsed["difficulty"] = 3

            logger.info(f"QuestionParser: 识别成功 - {parsed['subject']}, 难度{parsed['difficulty']}")
            return parsed

        except Exception as e:
            logger.warning(f"QuestionParser: 多模态识别失败 ({e})，尝试纯文本 fallback...")
            try:
                fallback_messages = [
                    {"role": "system", "content": QUESTION_PARSE_SYSTEM_PROMPT},
                    {"role": "user", "content": "请生成一道计算机考研408数据结构科目的中等难度题目（链表相关），输出JSON格式。"},
                ]
                raw_response = await self.llm.chat(fallback_messages)
                logger.info(f"QuestionParser: Fallback 成功, 响应长度: {len(raw_response)}")

                # Fallback 成功，继续走 JSON 解析流程
                parsed = self._extract_json(raw_response)
                parsed["question_id"] = f"q_fallback_{hash(raw_response) % 100000:05d}"
                if not parsed.get("subject"):
                    parsed["subject"] = "数据结构"
                if not isinstance(parsed.get("difficulty"), int) or not (1 <= parsed.get("difficulty") <= 5):
                    parsed["difficulty"] = 3
                logger.info(f"QuestionParser: Fallback 解析成功 - {parsed['subject']}")
                return parsed

            except Exception as e2:
                logger.error(f"QuestionParser: Fallback 也失败 - {e2}", exc_info=True)
                return {
                    "question_id": "q_error_001",
                    "subject": "数据结构",
                    "knowledge_tags": [],
                    "difficulty": 0,
                    "content": f"[识别失败] {str(e)}",
                    "error": str(e),
                }

    def _extract_json(self, text: str) -> dict:
        """从 LLM 响应中提取 JSON."""
        # 尝试直接解析
        text = text.strip()

        # 移除可能的 markdown 代码块标记
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        # 尝试找到 JSON 对象
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 如果无法解析为 JSON，包装为 content
        logger.warning(f"QuestionParser: 无法解析JSON，原始文本前200字: {text[:200]}")
        return {
            "subject": "数据结构",
            "knowledge_tags": [],
            "difficulty": 3,
            "content": text.strip(),
        }
