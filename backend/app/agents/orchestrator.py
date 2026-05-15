"""Orchestrator Agent - 基于 LangGraph 的主调度器.

使用 LangGraph StateGraph 编排多 Agent 协作:
  - 接收用户请求 → 意图识别 → 路由到对应 Agent
  - 支持 Agent 间协作（如：搜题 → 引导对话）
  - 工具调用集成（RAG检索 / 知识图谱 / OCR）

状态图:
  START → [intent_classify] → [route_to_agent] → [agent_execute] → END
"""

import logging
from enum import Enum
from typing import TypedDict, Annotated, AsyncIterator
import operator

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.llm_gateway import llm_gateway
from app.core.tools import ALL_TOOLS, get_tool_descriptions
from .socratic_tutor import socratic_tutor_agent as tutor
from .question_parser import question_parser_agent as parser
from .corrector import corrector_agent as corrector
from .diagnostician import diagnostician_agent as diagnostician

logger = logging.getLogger(__name__)


# ============================================================
# 类型定义
# ============================================================

class AgentType(str, Enum):
    """Agent 类型."""
    QUESTION_PARSER = "question_parser"
    SOCRATIC_TUTOR = "socratic_tutor"
    CORRECTOR = "corrector"
    DIAGNOSTICIAN = "diagnostician"
    UNKNOWN = "unknown"


class UserIntent(str, Enum):
    """用户意图."""
    SEARCH_QUESTION = "search_question"       # 拍照搜题/题目解析
    START_CHAT = "start_chat"                # 开始引导对话
    CONTINUE_CHAT = "continue_chat"          # 继续对话
    CORRECT_HOMEWORK = "correct_homework"     # 手写批改
    GET_DIAGNOSIS = "get_diagnosis"          # 薄弱点诊断
    CODE_VISUALIZE = "code_visualize"        # 代码可视化
    GENERAL_QA = "general_qa"                # 通用问答


class OrchestratorState(TypedDict):
    """调度器状态."""
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str                              # 识别的意图
    target_agent: str                        # 目标 Agent 名称
    raw_input: dict                          # 原始输入数据
    result: dict                             # Agent 执行结果
    session_id: str                          # 会话 ID


# ============================================================
# Prompt
# ============================================================

INTENT_CLASSIFY_PROMPT = """你是 TuringMate 的意图路由器。
分析用户的请求，判断应该路由到哪个处理模块。

## 可用 Agent：
{agent_list}

## 工具能力：
{tool_list}

## 用户输入：{user_input}

## 输出 JSON：
{
  "intent": "意图类型",
  "target_agent": "目标agent",
  "confidence": 0.95,
  "extracted_params": {{}}
}"""


# ============================================================
# Graph Nodes
# ============================================================

async def intent_classifier(state: OrchestratorState) -> dict:
    """节点: 意图分类."""
    llm = llm_gateway.get_chat_model()

    user_text = ""
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, 'content'):
            user_text = last_msg.content[:500]

    # 构建可用信息
    tool_descs = get_tool_descriptions()
    prompt = INTENT_CLASSIFY_PROMPT.format(
        agent_list="question_parser(搜题) | socratic_tutor(引导对话) | corrector(批改) | diagnostician(诊断)",
        tool_list="\n".join(f"- {t['name']}: {t['description']}" for t in tool_descs),
        user_input=user_text or "(无文字输入，可能是图片)",
    )

    response_msg = await llm.ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content="分析以上请求。"),
    ])

    raw_content = response_msg.content if hasattr(response_msg, 'content') else str(response_msg)
    intent_data = _parse_intent_json(raw_content)

    return {
        "intent": intent_data.get("intent", "general_qa"),
        "target_agent": intent_data.get("target_agent", "unknown"),
        "raw_input": intent_data.get("extracted_params", {}),
    }


async def route_and_execute(state: OrchestratorState) -> dict:
    """节点: 路由并执行对应 Agent."""
    target = state.get("target_agent", "unknown")
    intent = state.get("intent", "")
    session_id = state.get("session_id", "default")
    messages = state.get("messages", [])
    raw_input = state.get("raw_input", {})

    logger.info(f"Orchestrator: 路由到 {target}, intent={intent}")

    try:
        match target:
            case AgentType.QUESTION_PARSER.value | "question_parser":
                result = await parser.parse_image(
                    image_url=raw_input.get("image_url", ""),
                ) if raw_input.get("image_url") else \
                       await parser.parse_text(raw_input.get("text", ""))

            case AgentType.SOCRATIC_TUTOR.value | "socratic_tutor":
                user_msg = ""
                for m in reversed(messages):
                    if isinstance(m, HumanMessage):
                        user_msg = m.content
                        break

                if intent == UserIntent.START_CHAT.value:
                    result = await tutor.generate_first_message(
                        session_id=session_id,
                        question_context=raw_input.get("question_context"),
                    )
                else:
                    result = await tutor.generate_response(
                        session_id=session_id,
                        user_message=user_msg,
                        question_context=raw_input.get("question_context"),
                    )

            case AgentType.CORRECTOR.value | "corrector":
                result = await corrector.correct(
                    image_url=raw_input.get("image_url", ""),
                    question_info=raw_input.get("question_info"),
                )

            case AgentType.DIAGNOSTICIAN.value | "diagnostician":
                result = await diagnostician.diagnose(
                    user_id=raw_input.get("user_id", "default"),
                    time_range=raw_input.get("time_range", "recent_30d"),
                )

            case _:
                # 兜底：通用 QA（直接用 LLM）
                llm = llm_gateway.get_chat_model()
                response = await llm.ainvoke(list(messages))
                result = {"message": response.content}

        return {"result": result}

    except Exception as e:
        logger.error(f"Orchestrator: Agent 执行失败 ({target}): {e}")
        return {"result": {"error": f"处理失败: {str(e)[:200]}", "success": False}}


def route_after_execution(state: OrchestratorState) -> str:
    """条件边: 执行后决定是否结束."""
    return END


# ============================================================
# 辅助函数
# ============================================================

def _parse_intent_json(raw: str) -> dict:
    """解析意图分类结果."""
    import json, re
    try:
        data = json.loads(raw.strip())
        if "intent" in data:
            return data
    except (json.JSONDecodeError, TypeError):
        pass

    # 简单关键词匹配兜底
    lower = raw.lower()
    if any(kw in lower for kw in ["搜题", "拍照", "识别题目", "parse"]):
        return {"intent": "search_question", "target_agent": "question_parser"}
    if any(kw in lower for kw in ["引导", "对话", "聊天", "chat"]):
        return {"intent": "start_chat", "target_agent": "socratic_tutor"}
    if any(kw in lower for kw in ["批改", "纠正", "correct"]):
        return {"intent": "correct_homework", "target_agent": "corrector"}
    if any(kw in lower for kw in ["诊断", "薄弱", "diagnosis"]):
        return {"intent": "get_diagnosis", "target_agent": "diagnostician"}

    return {"intent": "general_qa", "target_agent": "socratic_tutor"}


# ============================================================
# Orchestrator 主类
# ============================================================

class TuringMateOrchestrator:
    """基于 LangGraph 的 TuringMate 主调度器.

    编排所有子 Agent 的协作流程.
    """

    def __init__(self):
        self._graph = self._build_graph()
        self._agents = {
            AgentType.QUESTION_PARSER: parser,
            AgentType.SOCRATIC_TUTOR: tutor,
            AgentType.CORRECTOR: corrector,
            AgentType.DIAGNOSTICIAN: diagnostician,
        }

    def _build_graph(self):
        """构建调度状态图."""
        graph = StateGraph(OrchestratorState)

        graph.add_node("classify_intent", intent_classifier)
        graph.add_node("execute_agent", route_and_execute)

        graph.add_edge(START, "classify_intent")
        graph.add_edge("classify_intent", "execute_agent")
        graph.add_conditional_edges(
            "execute_agent",
            route_after_execution,
            {"__end__": END},
        )

        memory = MemorySaver()
        return graph.compile(checkpointer=memory)

    async def process(
        self,
        input_type: str,
        data: dict,
        session_id: str = "default",
    ) -> dict:
        """处理用户请求.

        Args:
            input_type: 请求类型 ("text" | "image" | "command")
            data: 请求数据
            session_id: 会话标识

        Returns:
            处理结果
        """
        config = {"configurable": {"thread_id": session_id}}

        # 构建 input message
        content_parts = []
        if input_type == "image":
            content_parts.append({"type": "text", "text": data.get("prompt", "请分析这张图片")})
            img_url = data.get("image_url", "")
            if img_url.startswith(("http://", "https://")):
                content_parts.append({"type": "image_url", "image_url": {"url": img_url}})
            else:
                import base64
                with open(img_url, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                })
        else:
            content_parts.append(data.get("text") or data.get("message", ""))

        initial_state: OrchestratorState = {
            "messages": [HumanMessage(content=content_parts)],
            "intent": "",
            "target_agent": "",
            "raw_input": data,
            "result": {},
            "session_id": session_id,
        }

        result_state = await self._graph.ainvoke(initial_state, config=config)

        return {
            **result_state.get("result", {}),
            "_metadata": {
                "intent": result_state.get("intent"),
                "agent": result_state.get("target_agent"),
                "session_id": session_id,
            },
        }

    async def stream_process(
        self,
        input_type: str,
        data: dict,
        session_id: str = "default",
    ) -> AsyncIterator[str]:
        """流式处理请求."""
        config = {"configurable": {"thread_id": session_id}}

        initial_state: OrchestratorState = {
            "messages": [HumanMessage(content=data.get("text", ""))],
            "intent": "",
            "target_agent": "",
            "raw_input": data,
            "result": {},
            "session_id": session_id,
        }

        async for chunk in self._graph.astream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                if node_name == "execute_agent":
                    result = node_output.get("result", {})
                    if "message" in result:
                        yield result["message"]

    @property
    def agents(self):
        """获取注册的 Agent 字典."""
        return self._agents


# 全局单例
orchestrator = TuringMateOrchestrator()
