"""QuestionParser Agent - 题目识别 Agent.

调用多模态 LLM (GPT-4o / 通义VL / DeepSeek VL) 解析图片中的题目，
输出结构化的题目信息：科目、知识点、难度、题面内容。
MVP 阶段返回 Mock 数据。
"""

from app.core.llm_gateway import LLMGateway


class QuestionParserAgent:
    """题目识别 Agent - 解析图片中的考题."""

    def __init__(self, llm_gateway: LLMGateway):
        self.llm = llm_gateway

    async def parse_image(self, image_url: str) -> dict:
        """解析图片中的题目.

        Args:
            image_url: 图片 URL（COS 路径）

        Returns:
            结构化题目信息
        """
        # TODO: 构造 Prompt，调用多模态 LLM
        # prompt = "请识别这张图片中的计算机考研408题目，输出：科目、知识点、难度(1-5)、完整题面"
        # result = await self.llm.chat_with_image(prompt, image_url)

        return {
            "question_id": "q_mock_001",
            "subject": "数据结构",
            "knowledge_tags": ["线性表", "链表"],
            "difficulty": 3,
            "content": "设单链表的表头指针为 L，设计算法删除链表中所有值等于 x 的结点。",
        }
