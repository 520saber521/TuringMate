"""SocraticTutor Agent - 苏格拉底式引导教学 Agent.

核心教学 Agent，通过状态机驱动引导流程：
QUESTION → HINT → PROBE → AFFIRM → EXTEND → COMPLETE

每个阶段：
1. QUESTION: 提出引导性问题，让学生先思考
2. HINT: 学生卡住时给出提示，但不直接给答案
3. PROBE: 追问，检验学生是否真正理解
4. AFFIRM: 确认学生思路正确，给予正向反馈
5. EXTEND: 拓展到相关知识点
6. COMPLETE: 对话结束，总结关键点

MVP 阶段使用预设对话模板 + 简单规则引擎模拟。
"""

from enum import Enum
from typing import Literal


class TutorStage(str, Enum):
    """引导阶段."""
    QUESTION = "QUESTION"
    HINT = "HINT"
    PROBE = "PROBE"
    AFFIRM = "AFFIRM"
    EXTEND = "EXTEND"
    COMPLETE = "COMPLETE"


class SocraticTutorAgent:
    """苏格拉底引导教学 Agent."""

    # 阶段转换规则：当前阶段 + 学生回复类型 → 下一阶段
    STAGE_TRANSITIONS: dict[TutorStage, dict[str, TutorStage]] = {
        TutorStage.QUESTION: {
            "correct_direction": TutorStage.AFFIRM,
            "partially_correct": TutorStage.HINT,
            "wrong": TutorStage.HINT,
            "dont_know": TutorStage.HINT,
        },
        TutorStage.HINT: {
            "understood": TutorStage.PROBE,
            "still_confused": TutorStage.HINT,
            "gave_up": TutorStage.AFFIRM,
        },
        TutorStage.PROBE: {
            "correct": TutorStage.AFFIRM,
            "partial": TutorStage.HINT,
            "wrong": TutorStage.HINT,
        },
        TutorStage.AFFIRM: {
            "ready_to_extend": TutorStage.EXTEND,
            "want_more_practice": TutorStage.QUESTION,
            "done": TutorStage.COMPLETE,
        },
        TutorStage.EXTEND: {
            "understood": TutorStage.COMPLETE,
            "confused": TutorStage.HINT,
        },
    }

    def __init__(self):
        self._session_states: dict[str, TutorStage] = {}

    def get_stage(self, session_id: str) -> TutorStage:
        """获取当前会话阶段."""
        return self._session_states.get(session_id, TutorStage.QUESTION)

    def set_stage(self, session_id: str, stage: TutorStage):
        """设置当前会话阶段."""
        self._session_states[session_id] = stage

    async def generate_response(
        self,
        session_id: str,
        user_message: str,
        question_context: dict | None = None,
    ) -> dict:
        """生成引导回复.

        Args:
            session_id: 会话 ID
            user_message: 学生回复
            question_context: 题目上下文（知识点、难度等）

        Returns:
            AI 引导回复内容、当前阶段、是否有可用提示
        """
        current_stage = self.get_stage(session_id)

        # TODO: MVP 阶段使用 LLM 生成回复
        # 后续接入 RAG 检索相关知识点辅助生成
        response = await self._generate_mock_response(current_stage, user_message)

        self.set_stage(session_id, response["stage"])
        return response

    async def _generate_mock_response(
        self,
        stage: TutorStage,
        user_message: str,
    ) -> dict:
        """Mock 响应生成 - TODO: 替换为 LLM 调用."""
        mock_responses = {
            TutorStage.QUESTION: {
                "content": f"同学你好！看到这道题，你觉得它考查的核心知识点是什么呢？\n\n💡 可以从题目中的关键词入手想想~",
                "stage": "HINT",
                "hint_available": True,
            },
            TutorStage.HINT: {
                "content": "很好的思考方向！那我们进一步想一下...\n\n🔍 提示：注意这道题中**删除操作**的特殊性——我们需要处理哪些边界情况？",
                "stage": "PROBE",
                "hint_available": True,
            },
            TutorStage.PROBE: {
                "content": "对！那你能不能用自己的话说说，为什么需要这样处理？\n\n✨ 这能帮我确认你是否真正理解了原理~",
                "stage": "AFFIRM",
                "hint_available": False,
            },
            TutorStage.AFFIRM: {
                "content": "非常棒！你的理解完全正确！🎉\n\n现在我们已经掌握了核心思路，想不想看看这个知识点还能怎么拓展应用？",
                "stage": "EXTEND",
                "hint_available": False,
            },
            TutorStage.EXTEND: {
                "content": "拓展思考：如果把「单链表」换成「双向链表」，解题思路会有什么变化？\n\n这种对比学习能帮你建立更完整的知识体系哦~",
                "stage": "COMPLETE",
                "hint_available": False,
            },
            TutorStage.COMPLETE: {
                "content": "今天的引导讲解就到这里！总结一下我们学到的要点：\n\n1️⃣ 链表遍历时维护前驱指针\n2️⃣ 注意头结点和空链表的边界情况\n3️⃣ 删除操作要释放被删结点的空间\n\n继续保持这样的思考方式，你一定可以的！💪",
                "stage": "COMPLETE",
                "hint_available": False,
            },
        }
        return mock_responses.get(stage, mock_responses[TutorStage.QUESTION])


socratic_tutor = SocraticTutorAgent()
