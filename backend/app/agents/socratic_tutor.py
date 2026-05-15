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

已接入 LLM Gateway，根据阶段和学生回复动态生成引导内容。
"""

import logging
from enum import Enum
from typing import AsyncIterator

from app.core.llm_gateway import llm_gateway
from app.rag.retriever import retriever

logger = logging.getLogger(__name__)

# 苏格拉底引导系统提示词
SOCRATIC_SYSTEM_PROMPT = """你是 TuringMate 的苏格拉底式引导私教，专门辅导408计算机考研学生。

你的核心原则：**永远不直接给出答案**，而是通过提问、提示和引导，让学生自己推导出结论。

当前引导阶段：{stage}
阶段说明：
- QUESTION: 提出引导性问题，让学生先思考核心知识点
- HINT: 学生卡住时给出方向性提示，但不暴露具体答案
- PROBE: 追问细节，检验学生是否真正理解而非死记硬背
- AFFIRM: 确认学生思路正确，给予正向反馈和鼓励
- EXTEND: 拓展到相关知识点，建立知识关联
- COMPLETE: 对话结束，总结关键要点和学习建议

题目上下文：
{question_context}

{rag_context}

回复要求：
1. 用中文回复，语气温暖专业像学长一样
2. 根据阶段调整引导策略
3. 适当使用 💡 🔍 ✨ 🎯 等图标增强可读性
4. 如果学生回答偏离主题，温和地引导回来
5. 控制回复长度在 200 字以内

{stage_instructions}"""

STAGE_INSTRUCTIONS = {
    "QUESTION": "先不评价学生回答对错，而是提出一个能让他们深入思考的问题。",
    "HINT": "给出方向性提示，可以是类比、反例或部分信息，但不给出完整答案。",
    "PROBE": "追问'为什么'和'什么情况下不成立'，检验理解的深度。",
    "AFFIRM": "肯定正确的思路，指出具体好在哪里，然后引导下一步。",
    "EXTEND": "把当前知识点联系到其他场景或科目，帮助建立知识网络。",
    "COMPLETE": "总结本次学习的3个关键要点，给出后续练习建议。",
}


class TutorStage(str, Enum):
    """引导阶段."""
    QUESTION = "QUESTION"
    HINT = "HINT"
    PROBE = "PROBE"
    AFFIRM = "AFFIRM"
    EXTEND = "EXTEND"
    COMPLETE = "COMPLETE"


# 阶段转换提示 - 用于 LLM 判断下一阶段
STAGE_TRANSITION_PROMPT = """根据学生的回复内容，判断应该进入哪个引导阶段。

当前阶段：{current_stage}
学生回复：{user_message}

判断规则：
- 学生回复方向正确 → 进入 AFFIRM
- 学生回复部分正确或模糊 → 进入 HINT 给更多提示
- 学生表示不理解 → 进入 HINT 给更具体的提示
- 学生正确解释了原理 → 进入 PROBE 追问细节
- 学生想继续深入学习 → 进入 EXTEND
- 学生表示已经掌握 → 进入 COMPLETE

只输出阶段名称（QUESTION/HINT/PROBE/AFFIRM/EXTEND/COMPLETE），不要输出其他内容。"""


class SocraticTutorAgent:
    """苏格拉底引导教学 Agent - 接入 LLM 动态生成引导内容."""

    def __init__(self):
        self._session_states: dict[str, TutorStage] = {}
        self._session_contexts: dict[str, dict] = {}
        self._session_histories: dict[str, list[dict]] = {}
        self.llm = llm_gateway

    def start_session(self, session_id: str, question_context: dict | None = None):
        """初始化会话状态."""
        self._session_states[session_id] = TutorStage.QUESTION
        self._session_contexts[session_id] = question_context or {}
        self._session_histories[session_id] = []

    def get_stage(self, session_id: str) -> TutorStage:
        """获取当前会话阶段."""
        return self._session_states.get(session_id, TutorStage.QUESTION)

    def set_stage(self, session_id: str, stage: TutorStage):
        """设置当前会话阶段."""
        self._session_states[session_id] = stage

    async def generate_first_message(
        self,
        session_id: str,
        question_context: dict | None = None,
    ) -> dict:
        """生成对话的第一条引导消息."""
        self.start_session(session_id, question_context)

        context_str = self._format_context(question_context)
        rag_context = await self._retrieve_rag_context(question_context)
        system_prompt = SOCRATIC_SYSTEM_PROMPT.format(
            stage="QUESTION",
            question_context=context_str,
            rag_context=rag_context,
            stage_instructions=STAGE_INSTRUCTIONS["QUESTION"],
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "我遇到了一道题，请帮我分析一下思路。"},
        ]

        try:
            response_text = await self.llm.chat(messages)
            self._session_histories[session_id].append({"role": "assistant", "content": response_text})
            return {
                "content": response_text,
                "stage": "HINT",
                "hint_available": True,
            }
        except Exception as e:
            logger.warning(f"SocraticTutor: LLM 调用失败 ({e})，使用 fallback")
            return {
                "content": "同学你好！看到这道题，你觉得它考查的核心知识点是什么呢？\n\n💡 可以从题目中的关键词入手想想~",
                "stage": "HINT",
                "hint_available": True,
            }

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
            question_context: 题目上下文

        Returns:
            AI 引导回复内容、当前阶段、是否有可用提示
        """
        current_stage = self.get_stage(session_id)

        # 如果会话不存在，初始化
        if session_id not in self._session_histories:
            self.start_session(session_id, question_context)

        # 记录用户消息
        self._session_histories[session_id].append({"role": "user", "content": user_message})

        context_str = self._format_context(
            question_context or self._session_contexts.get(session_id, {})
        )

        # 1. 用 LLM 判断下一阶段
        next_stage = await self._determine_next_stage(current_stage, user_message)

        # 2. 用 LLM 生成引导回复
        rag_context = await self._retrieve_rag_context(
            question_context or self._session_contexts.get(session_id, {})
        )
        system_prompt = SOCRATIC_SYSTEM_PROMPT.format(
            stage=next_stage.value,
            question_context=context_str,
            rag_context=rag_context,
            stage_instructions=STAGE_INSTRUCTIONS.get(next_stage.value, ""),
        )

        # 构建对话历史（最近 10 条）
        history = self._session_histories[session_id][-10:]
        messages = [{"role": "system", "content": system_prompt}] + history

        try:
            response_text = await self.llm.chat(messages)
            self._session_histories[session_id].append({"role": "assistant", "content": response_text})
            self.set_stage(session_id, next_stage)

            return {
                "content": response_text,
                "stage": next_stage.value,
                "hint_available": next_stage in (TutorStage.HINT, TutorStage.PROBE, TutorStage.QUESTION),
            }
        except Exception as e:
            logger.warning(f"SocraticTutor: LLM 调用失败 ({e})，使用 fallback")
            fallback = self._generate_fallback(current_stage, user_message)
            self.set_stage(session_id, TutorStage(fallback["stage"]))
            self._session_histories[session_id].append({"role": "assistant", "content": fallback["content"]})
            return fallback

    async def stream_response(
        self,
        session_id: str,
        user_message: str,
        question_context: dict | None = None,
    ) -> AsyncIterator[str]:
        """流式生成引导回复."""
        current_stage = self.get_stage(session_id)

        if session_id not in self._session_histories:
            self.start_session(session_id, question_context)

        self._session_histories[session_id].append({"role": "user", "content": user_message})

        context_str = self._format_context(
            question_context or self._session_contexts.get(session_id, {})
        )

        next_stage = await self._determine_next_stage(current_stage, user_message)

        rag_context = await self._retrieve_rag_context(
            question_context or self._session_contexts.get(session_id, {})
        )
        system_prompt = SOCRATIC_SYSTEM_PROMPT.format(
            stage=next_stage.value,
            question_context=context_str,
            rag_context=rag_context,
            stage_instructions=STAGE_INSTRUCTIONS.get(next_stage.value, ""),
        )

        history = self._session_histories[session_id][-10:]
        messages = [{"role": "system", "content": system_prompt}] + history

        collected = []
        try:
            async for chunk in self.llm.stream_chat(messages):
                collected.append(chunk)
                yield chunk

            full_response = "".join(collected)
            self._session_histories[session_id].append({"role": "assistant", "content": full_response})
            self.set_stage(session_id, next_stage)
        except Exception as e:
            logger.warning(f"SocraticTutor: 流式调用失败 ({e})，发送 fallback")
            fallback_text = "让我们一步步来分析这道题...\n\n你觉得这道题的关键点在哪里？"
            yield fallback_text

    async def _determine_next_stage(self, current_stage: TutorStage, user_message: str) -> TutorStage:
        """用 LLM 判断下一阶段."""
        prompt = STAGE_TRANSITION_PROMPT.format(
            current_stage=current_stage.value,
            user_message=user_message,
        )

        try:
            messages = [{"role": "user", "content": prompt}]
            result = await self.llm.chat(messages, max_tokens=20, temperature=0.1)
            stage_str = result.strip().upper()

            # 提取有效的阶段名
            for stage in TutorStage:
                if stage.value in stage_str:
                    return stage

            # 默认基于简单规则
            return self._simple_stage_transition(current_stage, user_message)
        except Exception:
            return self._simple_stage_transition(current_stage, user_message)

    def _simple_stage_transition(self, current_stage: TutorStage, user_message: str) -> TutorStage:
        """简单规则阶段转换（fallback）."""
        transitions = {
            TutorStage.QUESTION: TutorStage.HINT,
            TutorStage.HINT: TutorStage.PROBE,
            TutorStage.PROBE: TutorStage.AFFIRM,
            TutorStage.AFFIRM: TutorStage.EXTEND,
            TutorStage.EXTEND: TutorStage.COMPLETE,
            TutorStage.COMPLETE: TutorStage.COMPLETE,
        }
        return transitions.get(current_stage, TutorStage.HINT)

    def _format_context(self, context: dict) -> str:
        """格式化题目上下文."""
        if not context:
            return "（暂无具体题目信息，请根据学生描述灵活引导）"

        parts = []
        if context.get("subject"):
            parts.append(f"科目：{context['subject']}")
        if context.get("knowledge_tags"):
            parts.append(f"知识点：{', '.join(context['knowledge_tags'])}")
        if context.get("difficulty"):
            parts.append(f"难度：{context['difficulty']}/5")
        if context.get("content"):
            parts.append(f"题目：{context['content'][:300]}")

        return "\n".join(parts) if parts else "（暂无具体题目信息）"

    async def _retrieve_rag_context(self, context: dict) -> str:
        """通过 RAG 检索相关知识点作为引导辅助."""
        if not context:
            return ""

        # 构建检索查询
        query_parts = []
        if context.get("subject"):
            query_parts.append(context["subject"])
        if context.get("knowledge_tags"):
            query_parts.extend(context["knowledge_tags"])
        if context.get("content"):
            query_parts.append(context["content"][:100])

        if not query_parts:
            return ""

        query = " ".join(query_parts)

        try:
            results = await retriever.retrieve(query, top_k=3)
            if not results:
                return ""

            knowledge_items = []
            for r in results[:3]:
                content = r.get("content", "")
                if content:
                    knowledge_items.append(content)

            if knowledge_items:
                return f"相关知识点参考：\n{chr(10).join(knowledge_items)}\n\n请参考以上知识点辅助引导，但不要直接给出答案。"
        except Exception as e:
            logger.warning(f"SocraticTutor: RAG 检索失败 ({e})，跳过知识增强")

        return ""

    def _generate_fallback(self, stage: TutorStage, user_message: str) -> dict:
        """Fallback 响应 - LLM 不可用时使用."""
        fallbacks = {
            TutorStage.QUESTION: {
                "content": "同学你好！这道题涉及哪些核心概念呢？试着从题目关键词入手分析~",
                "stage": "HINT",
                "hint_available": True,
            },
            TutorStage.HINT: {
                "content": "不错的思考方向！再深入想想，这个操作的边界条件是什么？",
                "stage": "PROBE",
                "hint_available": True,
            },
            TutorStage.PROBE: {
                "content": "你能不能用自己的话说说为什么需要这样处理？",
                "stage": "AFFIRM",
                "hint_available": False,
            },
            TutorStage.AFFIRM: {
                "content": "很好！你的理解很到位。想不想看看这个知识点还能怎么拓展？",
                "stage": "EXTEND",
                "hint_available": False,
            },
            TutorStage.EXTEND: {
                "content": "今天的引导就到这里，总结一下我们学到的关键要点，继续保持！",
                "stage": "COMPLETE",
                "hint_available": False,
            },
            TutorStage.COMPLETE: {
                "content": "总结完成！继续加油，有问题随时找我~",
                "stage": "COMPLETE",
                "hint_available": False,
            },
        }
        return fallbacks.get(stage, fallbacks[TutorStage.QUESTION])


socratic_tutor = SocraticTutorAgent()
