"""SocraticTutor Agent - 基于 LangGraph 的苏格拉底教学 Agent.

状态图:
  START → [分析意图] → [RAG检索] → [LLM生成] → END

  状态流转 (TutorStage):
    QUESTION  ──→ THINKING  ──→ GUIDANCE  ──→ PRACTICE
       ↑                                              │
       └──────────────── 反馈循环 ←──────────────────┘

使用 LangChain 组件:
  - ChatOpenAI (via LLM Gateway) 对话模型
  - @tool 装饰器的工具集
  - ChromaDB Retriever 检索增强
"""

import logging
from enum import Enum
from typing import AsyncIterator, TypedDict, Annotated
import operator

from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage,
    BaseMessage, remove_message, add_messages
)
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.llm_gateway import llm_gateway
from app.core.tools import question_search, knowledge_graph
from app.rag.retriever import retriever

logger = logging.getLogger(__name__)


# ============================================================
# 类型定义
# ============================================================

class TutorStage(str, Enum):
    """教学阶段."""
    QUESTION = "question"         # 题目理解阶段
    THINKING = "thinking"         # 思考引导阶段
    GUIDANCE = "guidance"         # 引导解答阶段
    PRACTICE = "practice"         # 练习巩固阶段
    REVIEW = "review"             # 复习回顾阶段


class TutorState(TypedDict):
    """LangGraph 状态定义."""
    messages: Annotated[list[BaseMessage], add_messages]  # 消息历史（自动追加）
    stage: str                                            # 当前教学阶段
    session_id: str                                       # 会话 ID
    question_context: dict                                # 题目上下文
    rag_context: str                                      # RAG 检索上下文
    is_complete: bool                                     # 是否完成


# ============================================================
# Prompt 模板
# ============================================================

SYSTEM_PROMPT_TEMPLATE = """你是 TuringMate 的 AI 苏格拉底私教老师，专攻计算机考研408。

## 当前阶段：{stage}

## 题目上下文：
{question_context}

## 参考知识（来自知识库）：
{rag_context}

## 阶段指令：
{stage_instructions}

## 核心原则：
1. **永远不直接给出答案**，而是通过提问引导学生自己思考
2. **每次只问一个问题**，等学生回答后再继续
3. **根据学生回答质量调整引导方向**：
   - 回答正确 → 提出更深层的问题
   - 回答部分正确 → 指出错误部分并追问原因
   - 回答错误 → 给提示但不直接纠正
4. **适时鼓励**学生，保持学习动力

请用简洁、友好的中文回复。"""

STAGE_INSTRUCTIONS: dict[str, str] = {
    "QUESTION": """帮助学生理解题目要求。
- 先问学生：这道题让你求什么？已知条件有哪些？
- 如果学生描述不清，帮他拆解题目要素
- 不要急着给思路，先确保他读懂了题""",
    "THINKING": """引导学生独立思考解题思路。
- 问：你觉得可以用什么方法/数据结构来解决？为什么？
- 如果学生卡住了，给一个方向性提示而非具体方法
- 鼓励学生说出他的想法，即使不完全对""",
    "GUIDANCE": """在学生有了初步思路后，引导他细化方案。
- 让他说出具体的算法步骤
- 追问边界条件、时间复杂度
- 用反例测试他的方案是否完善""",
    "PRACTICE": """给学生一道类似的变式题练习。
- 题目难度应略低于原题
- 观察学生是否能独立解决
- 做完后一起回顾关键步骤""",
    "REVIEW": """回顾本次对话的核心知识点。
- 总结学到了什么
- 点出易错点
- 鼓励继续练习""",
}


# ============================================================
# Graph Nodes (LangGraph 节点函数)
# ============================================================

async def retrieve_knowledge(state: TutorState) -> dict:
    """节点: RAG 检索相关知识点."""
    context = state.get("question_context", {})
    rag_text = ""

    if context:
        query_parts = []
        if context.get("subject"):
            query_parts.append(context["subject"])
        if context.get("knowledge_tags"):
            query_parts.extend(context["knowledge_tags"])
        if context.get("content"):
            query_parts.append(context["content"][:100])

        if query_parts:
            try:
                results = await retriever.retrieve(
                    " ".join(query_parts), top_k=3
                )
                if results:
                    items = [r.get("content", "") for r in results[:3]]
                    rag_text = f"相关知识点参考：\n" + "\n".join(items) + \
                              "\n\n请参考以上知识点辅助引导，但不要直接给出答案。"
            except Exception as e:
                logger.debug(f"SocraticTutor RAG 失败: {e}")

    return {"rag_context": rag_text}


async def generate_response(state: TutorState) -> dict:
    """节点: LLM 生成回复."""
    llm = llm_gateway.get_chat_model()

    # 构建系统 prompt
    system_content = SYSTEM_PROMPT_TEMPLATE.format(
        stage=state.get("stage", "question"),
        question_context=_format_context(state.get("question_context")),
        rag_context=state.get("rag_context", "(暂无)"),
        stage_instructions=STAGE_INSTRUCTIONS.get(state.get("stage", ""), ""),
    )

    messages_with_system = [
        SystemMessage(content=system_content),
        *state.get("messages", []),
    ]

    response = await llm.ainvoke(messages_with_system)

    # 确定下一阶段
    next_stage = _determine_next_stage(
        state.get("stage", "question"),
        state.get("messages", []),
    )

    return {
        "messages": [response],
        "stage": next_stage.value if isinstance(next_stage, TutorStage) else next_stage,
    }


def route_by_stage(state: TutorState) -> str:
    """条件边: 根据阶段决定是否结束."""
    stage = state.get("stage", "")
    messages = state.get("messages", [])

    # 如果已经完成足够轮次的对话
    if len(messages) >= 15:
        return "end"

    # 如果最后一条消息是学生说"懂了"/"好了"等结束语
    last_human = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human = msg.content.strip()
            break
    if last_human and any(kw in last_human for kw in ["懂了", "明白了", "好了", "结束", "next"]):
        return "end"

    return "continue"


# ============================================================
# 辅助函数
# ============================================================

def _format_context(context: dict | None) -> str:
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


def _determine_next_stage(current_stage: str, messages: list) -> TutorStage:
    """根据当前状态和对话内容确定下一阶段."""
    stage_map = {
        "question": TutorStage.THINKING,
        "thinking": TutorStage.GUIDANCE,
        "guidance": TutorStage.PRACTICE,
        "practice": TutorStage.REVIEW,
        "review": TutorStage.REVIEW,
    }
    return stage_map.get(current_stage, TutorStage.THINKING)


# ============================================================
# SocraticTutor Agent 类
# ============================================================

class SocraticTutorAgent:
    """基于 LangGraph 的苏格拉底教学 Agent.

    使用 StateGraph 编排教学流程:
      START → retrieve_knowledge → generate_response → (route) → continue/end
    """

    def __init__(self):
        self._graph = self._build_graph()

    def _build_graph(self):
        """构建 LangGraph 状态图."""
        graph = StateGraph(TutorState)

        # 添加节点
        graph.add_node("retrieve", retrieve_knowledge)
        graph.add_node("generate", generate_response)

        # 添加边
        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "generate")

        # 条件边: generate 之后根据阶段决定是否继续或结束
        graph.add_conditional_edges(
            "generate",
            route_by_stage,
            {
                "continue": "retrieve",   # 继续下一轮
                "end": END,              # 结束对话
            },
        )

        # 配置检查点（支持会话记忆）
        memory = MemorySaver()
        return graph.compile(checkpointer=memory, interrupt_before=[])

    async def generate_first_message(self, session_id: str, question_context: dict = None) -> dict:
        """生成对话的第一条引导消息.

        Args:
            session_id: 会话唯一标识
            question_context: 题目上下文 {"subject", "knowledge_tags", "difficulty", "content"}
        """
        initial_state: TutorState = {
            "messages": [
                HumanMessage(content="请开始引导学生理解这道题目。")
            ],
            "stage": TutorStage.QUESTION.value,
            "session_id": session_id,
            "question_context": question_context or {},
            "rag_context": "",
            "is_complete": False,
        }

        config = {"configurable": {"thread_id": session_id}}
        result = await self._graph.ainvoke(initial_state, config=config)

        ai_message = result["messages"][-1]
        return {
            "session_id": session_id,
            "stage": result["stage"],
            "message": ai_message.content if hasattr(ai_message, 'content') else str(ai_message),
            "is_first": True,
        }

    async def generate_response(self, session_id: str, user_message: str, question_context: dict = None) -> dict:
        """基于用户消息生成引导回复.

        Args:
            session_id: 会话标识
            user_message: 用户输入
            question_context: 题目上下文
        """
        config = {"configurable": {"thread_id": session_id}}

        update_state: TutorState = {
            "messages": [HumanMessage(content=user_message)],
        }

        result = await self._graph.ainvoke(update_state, config=config)

        ai_message = result["messages"][-1]
        return {
            "session_id": session_id,
            "stage": result["stage"],
            "message": ai_message.content if hasattr(ai_message, 'content') else str(ai_message),
            "is_first": False,
        }

    async def stream_response(self, session_id: str, user_message: str, question_context: dict = None) -> AsyncIterator[str]:
        """流式输出回复 (用于 SSE).

        Yields:
            文本 token 片段
        """
        config = {"configurable": {"thread_id": session_id}}

        update_state: TutorState = {
            "messages": [HumanMessage(content=user_message)],
        }

        async for chunk in self._graph.astream(update_state, config=config, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                if node_name == "generate":
                    new_messages = node_output.get("messages", [])
                    for msg in new_messages:
                        if hasattr(msg, 'content') and msg.content:
                            yield msg.content

    def get_session_history(self, session_id: str) -> list[dict]:
        """获取会话历史记录."""
        config = {"configurable": {"thread_id": session_id}}
        try:
            state_snapshot = self._graph.get_state(config)
            messages = state_snapshot.values.get("messages", [])
            return [
                {
                    "role": "user" if isinstance(m, HumanMessage) else "assistant",
                    "content": m.content if hasattr(m, 'content') else str(m),
                    "timestamp": "",
                }
                for m in messages
            ]
        except Exception:
            return []


# 全局单例
socratic_tutor_agent = SocraticTutorAgent()
