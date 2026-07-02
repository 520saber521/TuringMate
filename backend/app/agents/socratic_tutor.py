"""SocraticTutor Agent - 基于 LangGraph create_react_agent 的苏格拉底教学 Agent.

使用 LangGraph 预构建的 ReAct Agent 模式:
  - create_react_agent(llm, tools) 自动处理工具调用循环
  - 内置 thought → action → observation 循环
  - 支持 RAG 检索增强 + 状态机阶段控制
  - 可配置的 Checkpointer 后端 (MemorySaver / PostgresSaver)

状态流转 (TutorStage):
  QUESTION ──→ THINKING ──→ GUIDANCE ──→ PRACTICE
     ↑                                              │
     └──────────────── 反馈循环 ←──────────────────┘
"""

import logging
import operator
from enum import Enum
from typing import AsyncIterator, TypedDict, Annotated

from langchain_core.documents import Document
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage,
    BaseMessage, RemoveMessage,
)
from langgraph.graph.message import add_messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.core.llm_gateway import llm_gateway
from app.core.tools import question_search, knowledge_graph
from app.core.prompts import get_prompt, STAGE_INSTRUCTIONS
from app.rag.retriever import retriever
from app.config import settings

# F2: 情绪感知集成
from app.agents.emotion_detector import emotion_detector

logger = logging.getLogger(__name__)


# ============================================================
# 类型定义
# ============================================================

class TutorStage(str, Enum):
    """教学阶段."""
    QUESTION = "question"
    THINKING = "thinking"
    GUIDANCE = "guidance"
    PRACTICE = "practice"
    REVIEW = "review"


class TutorState(TypedDict):
    """LangGraph 状态定义（含 F2 扩展字段）."""
    messages: Annotated[list[BaseMessage], add_messages]
    remaining_steps: Annotated[int, operator.add]
    stage: str
    session_id: str
    question_context: dict
    rag_context: str
    is_complete: bool
    # F2: 情绪感知模式覆盖（注入到 system prompt）
    emotion_override: str


# ============================================================
# RAG Context 格式化器 (L4: 用 LangChain 方式替代手动拼接)
# ============================================================

RAG_CONTEXT_TEMPLATE = PromptTemplate.from_template(
    "相关知识点参考：\n{context}\n\n请参考以上知识点辅助引导，但不要直接给出答案。"
)


def _format_retrieved_documents(docs: list[dict]) -> str:
    """用 LangChain PromptTemplate 格式化检索结果.

    替代之前的手动:
        items = [r.get("content", "") for r in results[:3]]
        rag_text = "相关知识点参考：\n" + "\n".join(items) + "\n\n..."

    Args:
        docs: retriever 返回的 [{"content", "metadata"}, ...]

    Returns:
        格式化的上下文字符串.
    """
    if not docs:
        return ""
    texts = [d.get("content", "") for d in docs[:3] if d.get("content")]
    if not texts:
        return ""
    return RAG_CONTEXT_TEMPLATE.format(context="\n".join(texts))


# ============================================================
# Graph Nodes — 使用 create_react_agent 工厂模式
# ============================================================

# SocraticTutor 可用工具集（通过 @tool 定义，直接传给 create_react_agent）
TUTOR_TOOLS = [question_search, knowledge_graph]


async def retrieve_knowledge(state: TutorState) -> dict:
    """节点: RAG 检索相关知识点 (使用 _format_retrieved_documents)."""
    context = state.get("question_context", {})

    if not context:
        return {"rag_context": ""}

    query_parts = []
    if context.get("subject"):
        query_parts.append(context["subject"])
    if context.get("knowledge_tags"):
        query_parts.extend(context["knowledge_tags"])
    if context.get("content"):
        query_parts.append(context["content"][:100])

    if not query_parts:
        return {"rag_context": ""}

    try:
        results = await retriever.retrieve(" ".join(query_parts), top_k=3)
        return {"rag_context": _format_retrieved_documents(results)}
    except Exception as e:
        logger.debug(f"SocraticTutor RAG 失败: {e}")
        return {"rag_context": ""}


def _build_system_content(stage: str, context: dict, rag_ctx: str, emotion_override: str = "") -> str:
    """从集中式 Prompt 构建系统消息内容（含 F3 情绪模式覆盖）."""
    base = f"""你是 TuringMate 的 AI 苏格拉底私教老师，专攻计算机考研408。

## 当前阶段：{stage}

## 题目上下文：
{_format_context(context)}

## 参考知识（来自知识库）：
{rag_ctx or '(暂无)'}

## 阶段指令：
{STAGE_INSTRUCTIONS.get(stage, '')}

## 核心原则：
1. **永远不直接给出答案**，而是通过提问引导学生自己思考
2. **每次只问一个问题**，等学生回答后再继续
3. **根据学生回答质量调整引导方向**
4. **适时鼓励**学生，保持学习动力

请用简洁、友好的中文回复。"""

    # F3: 追加情绪感知模式覆盖指令
    if emotion_override:
        base += f"\n\n{emotion_override}"

    return base


async def generate_response(state: TutorState) -> dict:
    """节点: LLM 生成回复（使用 bind_tools 的 ReAct Agent + F3 情绪覆盖）."""
    llm = llm_gateway.get_chat_model()

    # 使用 LangChain 原生 bind_tools 绑定工具
    bound_llm = llm.bind_tools(TUTOR_TOOLS)

    # F3: 获取情绪模式覆盖
    emotion_override = state.get("emotion_override", "")

    system_content = _build_system_content(
        stage=state.get("stage", "question"),
        context=state.get("question_context", {}),
        rag_ctx=state.get("rag_context", ""),
        emotion_override=emotion_override,
    )

    messages_with_system = [
        SystemMessage(content=system_content),
        *state.get("messages", []),
    ]

    response = await bound_llm.ainvoke(messages_with_system)

    # 如果 LLM 决定调用工具，执行工具并返回结果
    if response.tool_calls and hasattr(response, 'tool_calls'):
        from langchain_core.messages import ToolMessage
        tool_messages = []
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_result = await _execute_tool(tool_name, tool_args)
            tool_messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tc["id"])
            )
        followup_response = await bound_llm.ainvoke(
            messages_with_system + [response] + tool_messages
        )
        response = followup_response

    next_stage = _determine_next_stage(
        state.get("stage", "question"),
        state.get("messages", []),
    )

    return {
        "messages": [response],
        "stage": next_stage.value if isinstance(next_stage, TutorStage) else next_stage,
    }


async def _execute_tool(tool_name: str, args: dict) -> any:
    """执行工具调用."""
    tool_map = {t.name: t for t in TUTOR_TOOLS}
    tool = tool_map.get(tool_name)
    if tool:
        return await tool.ainvoke(args)
    return f"Unknown tool: {tool_name}"


def route_by_stage(state: TutorState) -> str:
    """条件边: 根据阶段决定是否结束."""
    stage = state.get("stage", "")
    messages = state.get("messages", [])

    if len(messages) >= 15:
        return "end"

    last_human = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_human = msg.content.strip()
            break
    if last_human and any(kw in last_human for kw in ["懂了", "明白了", "好了", "结束", "next"]):
        return "end"

    return "continue"


# ============================================================
# Checkpoint 工厂 (M6: 可配置持久化后端)
# ============================================================

def create_checkpointer(backend: str = "memory"):
    """创建可配置的 LangGraph Checkpointer.

    支持后端:
      - memory:   MemorySaver (默认，开发环境)
      - postgres: PostgresSaver (生产环境，需要 DATABASE_URL)
      - redis:    RedisSaver (实验性，高并发场景)

    Args:
        backend: 持久化后端名称 ("memory" | "postgres" | "redis")

    Returns:
        LangGraph BaseCheckpointSaver 实例.
    """
    if backend == "memory":
        return MemorySaver()

    elif backend == "postgres":
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            import os

            db_url = getattr(settings, 'DATABASE_URL', None) or os.environ.get(
                "DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5432/langgraph"
            )
            # 注意：AsyncPostgresSaver 需要在应用启动时 setup()，
            # 这里只创建实例引用，实际初始化在 lifespan 中完成
            logger.info(f"Checkpointer: 使用 PostgreSQL 后端 - {db_url.split('@')[-1]}")
            return AsyncPostgresSaver.from_conn_string(db_url)
        except ImportError:
            logger.warning("PostgresSaver 需要 asyncpg 包，回退到 MemorySaver")
            return MemorySaver()

    elif backend == "redis":
        try:
            from langgraph_checkpoint_redis import RedisSaver
            redis_url = getattr(settings, 'REDIS_URL', None) or os.environ.get(
                "REDIS_URL", "redis://localhost:6379"
            )
            logger.info(f"Checkpointer: 使用 Redis 后端 - {redis_url}")
            return RedisSaver.from_conn_string(redis_url)
        except ImportError:
            logger.warning("RedisSaver 需要 langgraph-checkpoint-redis 包，回退到 MemorySaver")
            return MemorySaver()

    else:
        logger.warning(f"未知 checkpointer 后端 '{backend}'，使用 MemorySaver")
        return MemorySaver()


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
    """基于 LangGraph StateGraph + bind_tools 的苏格拉底教学 Agent.

    编排流程:
      START → retrieve_knowledge → generate_response (bind_tools) → (route) → continue/end

    特性:
      - create_react_agent() 自动工具调用循环
      - 可配置 Checkpointer 后端 (M6)
      - LangChain PromptTemplate 格式化 RAG 上下文 (L4)
    """

    def __init__(self, checkpointer_backend: str = "memory"):
        self._checkpointer_backend = checkpointer_backend
        self._graph = self._build_graph()
        self._react_agent = create_react_agent(
            model=llm_gateway.get_chat_model(),
            tools=TUTOR_TOOLS,
            prompt=get_prompt("socratic_tutor"),
            state_schema=TutorState,
        )
        # F2: 会话级思维追踪器 {session_id: ThinkingTracer}
        self._tracers: dict[str, object] = {}
        # F3: 情绪感知已通过 emotion_detector 全局单例管理

    def _build_graph(self):
        """构建带阶段控制的 StateGraph."""
        graph = StateGraph(TutorState)

        graph.add_node("retrieve", retrieve_knowledge)
        graph.add_node("generate", generate_response)

        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "generate")

        graph.add_conditional_edges(
            "generate",
            route_by_stage,
            {"continue": "retrieve", "end": END},
        )

        # M6: 使用可配置的 Checkpointer
        checkpointer = create_checkpointer(self._checkpointer_backend)
        return graph.compile(checkpointer=checkpointer, interrupt_before=[])

    async def generate_first_message(self, session_id: str, question_context: dict = None) -> dict:
        """生成对话的第一条引导消息（含 F2 初始化追踪器）."""
        # F2: 初始化思维追踪器
        question_id = question_context.get("question_id", "") if question_context else ""
        user_id = question_context.get("user_id", "") if question_context else ""
        self._tracers[session_id] = create_tracer(session_id, question_id, user_id)

        initial_state: TutorState = {
            "messages": [HumanMessage(content="请开始引导学生理解这道题目。")],
            "stage": TutorStage.QUESTION.value,
            "session_id": session_id,
            "question_context": question_context or {},
            "rag_context": "",
            "is_complete": False,
            "emotion_override": "",  # F3
        }

        config = {"configurable": {"thread_id": session_id}}
        result = await self._graph.ainvoke(initial_state, config=config)

        ai_message = result["messages"][-1]

        # F2: 记录 AI 引导作为 INSIGHT 类型
        tracer = self._tracers.get(session_id)
        if tracer:
            tracer.record_step(
                content=ai_message.content if hasattr(ai_message, 'content') else str(ai_message),
                role="assistant",
                step_type=StepType.QUESTION,
                related_topic=question_context.get("knowledge_tags", [""])[0] if question_context and question_context.get("knowledge_tags") else "",
            )

        return {
            "session_id": session_id,
            "stage": result["stage"],
            "message": ai_message.content if hasattr(ai_message, 'content') else str(ai_message),
            "is_first": True,
        }

    async def generate_response(self, session_id: str, user_message: str, question_context: dict = None) -> dict:
        """基于用户消息生成引导回复（含 F2 思维追踪 + F3 情绪感知）."""
        # F2: 记录学生思考步骤
        tracer = self._tracers.get(session_id)
        if tracer:
            step_type = StepType.ANSWER
            # 检测是否为变式练习回答
            if any(kw in user_message for kw in ["答案是", "结果是", "我认为", "应该是"]):
                step_type = StepType.PRACTICE
            elif any(kw in user_message for kw in ["为什么", "怎么", "如何", "不懂", "不明白"]):
                step_type = StepType.QUESTION

            topic = ""
            if question_context and question_context.get("knowledge_tags"):
                topic = question_context["knowledge_tags"][0] if isinstance(question_context["knowledge_tags"], list) else ""

            tracer.record_step(
                content=user_message,
                role="user",
                step_type=step_type,
                related_topic=topic,
            )

        # F3: 情绪检测 + 教学模式切换
        emotion_override = ""
        emotion_result = None
        try:
            emotion_result = emotion_detector.detect(user_message, session_id)
            emotion_override = emotion_detector.get_mode_prompt_override(session_id)
            if emotion_result and emotion_result.emotion.value != "neutral":
                logger.info(
                    f"SocraticTutor[ {session_id}] 情绪检测: "
                    f"{emotion_result.emotion.value} (置信度:{emotion_result.confidence:.2f}) → "
                    f"模式: {emotion_result.suggested_mode.value}"
                )
        except Exception as e:
            logger.debug(f"情绪检测跳过: {e}")

        config = {"configurable": {"thread_id": session_id}}

        # F3: 将情绪覆盖传入图状态
        update_state: TutorState = {
            "messages": [HumanMessage(content=user_message)],
            "emotion_override": emotion_override or "",
        }

        result = await self._graph.ainvoke(update_state, config=config)

        ai_message = result["messages"][-1]

        # F2: 记录 AI 回复
        if tracer:
            ai_content = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)
            # 如果情绪是纠正/鼓励类型，标记为 CORRECTION
            ai_step_type = StepType.HINT
            if emotion_result and emotion_result.suggested_mode.value in ("confidence", "relaxed"):
                ai_step_type = StepType.CORRECTION

            tracer.record_step(
                content=ai_content,
                role="assistant",
                step_type=ai_step_type,
            )

        return {
            "session_id": session_id,
            "stage": result["stage"],
            "message": ai_message.content if hasattr(ai_message, 'content') else str(ai_message),
            "is_first": False,
            # F3: 返回情绪状态（供前端展示）
            "emotion_state": emotion_result.model_dump() if emotion_result else None,
        }

    async def stream_response(self, session_id: str, user_message: str, question_context: dict = None) -> AsyncIterator[str]:
        """流式输出回复 (SSE, 含 F2/F3 集成)."""
        # F2: 记录学生思考步骤
        tracer = self._tracers.get(session_id)
        if tracer:
            step_type = StepType.ANSWER
            if any(kw in user_message for kw in ["答案是", "结果是", "我认为", "应该是"]):
                step_type = StepType.PRACTICE
            elif any(kw in user_message for kw in ["为什么", "怎么", "如何", "不懂", "不明白"]):
                step_type = StepType.QUESTION

            topic = ""
            if question_context and question_context.get("knowledge_tags"):
                topic = question_context["knowledge_tags"][0] if isinstance(question_context["knowledge_tags"], list) else ""

            tracer.record_step(
                content=user_message,
                role="user",
                step_type=step_type,
                related_topic=topic,
            )

        # F3: 情绪检测
        emotion_override = ""
        try:
            emotion_result = emotion_detector.detect(user_message, session_id)
            emotion_override = emotion_detector.get_mode_prompt_override(session_id)
        except Exception:
            pass

        config = {"configurable": {"thread_id": session_id}}

        update_state: TutorState = {
            "messages": [HumanMessage(content=user_message)],
            "emotion_override": emotion_override or "",
        }

        ai_content_buffer = ""
        async for chunk in self._graph.astream(update_state, config=config, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                if node_name == "generate":
                    new_messages = node_output.get("messages", [])
                    for msg in new_messages:
                        if hasattr(msg, 'content') and msg.content:
                            ai_content_buffer += msg.content
                            yield msg.content

        # F2: 流式结束后记录 AI 回复
        if tracer and ai_content_buffer:
            ai_step_type = StepType.HINT
            try:
                if emotion_result and emotion_result.suggested_mode.value in ("confidence", "relaxed"):
                    ai_step_type = StepType.CORRECTION
            except Exception:
                pass
            tracer.record_step(
                content=ai_content_buffer,
                role="assistant",
                step_type=ai_step_type,
            )

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

    @property
    def checkpointer_backend(self) -> str:
        """当前使用的 Checkpointer 后端类型."""
        return self._checkpointer_backend

    # ── F2: 思维追踪公共 API ──────────────────────────────

    def get_thinking_path(self, session_id: str) -> dict | None:
        """获取会话的完整思考路径图.

        Args:
            session_id: 会话 ID

        Returns:
            ThinkingPath 字典，如果不存在则返回 None
        """
        tracer = self._tracers.get(session_id)
        if not tracer:
            return None
        return tracer.build_path()

    def get_thinking_report(self, session_id: str) -> dict | None:
        """获取思维成长报告（周/月维度）.

        Args:
            session_id: 会话 ID
        """
        tracer = self._tracers.get(session_id)
        if not tracer:
            return None
        # 收集同用户其他会话的历史路径
        user_id = tracer.user_id
        historical = []
        for sid, t in self._tracers.items():
            if sid != session_id and t.user_id == user_id:
                try:
                    historical.append(t.build_path())
                except Exception:
                    pass
        return tracer.generate_weekly_report(historical)

    def close_session(self, session_id: str) -> dict | None:
        """关闭会话，返回最终思维路径并清理资源."""
        tracer = self._tracers.pop(session_id, None)
        if not tracer:
            return None
        path = tracer.build_path()
        emotion_detector.reset_session(session_id)
        return path

    # ── F3: 情绪感知公共 API ──────────────────────────────

    def get_emotion_state(self, session_id: str) -> dict:
        """获取当前会话的情绪状态快照.

        Args:
            session_id: 会话 ID
        """
        return emotion_detector.get_current_state(session_id)

    def get_emotion_events(self, session_id: str) -> list[dict]:
        """获取情绪事件日志."""
        return emotion_detector.get_session_events(session_id)


# 全局单例 — 从 settings 读取后端配置
_backend = getattr(settings, 'CHECKPOINT_BACKEND', 'memory')
socratic_tutor_agent = SocraticTutorAgent(checkpointer_backend=_backend)
logger.info(f"SocraticTutorAgent 初始化完成 (Checkpointer: {_backend})")
