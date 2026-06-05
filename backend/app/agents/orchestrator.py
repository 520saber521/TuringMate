"""Orchestrator Agent - 基于 LangGraph + RunnableBranch 的主调度器.

重构要点 (M3 + M5):
  - 使用 with_structured_output() 替代手动 JSON 解析意图分类
  - 使用 LangGraph 条件边 + 分发表替代 if-elif 路由
  - 工具自动绑定 via create_react_agent 模式

状态图:
  START → [intent_classify] → [route_by_intent] → [exec_*] → END

路由分发:
  search_question      → exec_question_parser
  start_chat           → exec_socratic_tutor
  continue_chat        → exec_socratic_tutor
  correct_homework     → exec_corrector
  get_diagnosis        → exec_diagnostician
  general_qa / unknown → exec_general_qa
"""

import logging
from enum import Enum
from typing import TypedDict, Annotated, AsyncIterator
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.llm_gateway import llm_gateway
from app.core.prompts import get_prompt
from app.core.tools import ALL_TOOLS, get_tool_descriptions
from .socratic_tutor import socratic_tutor_agent as tutor
from .question_parser import question_parser_agent as parser
from .corrector import corrector_agent as corrector
from .diagnostician import diagnostician_agent as diagnostician
# 6 大功能模块 Agents
from .learning_path_planner import learning_path_planner          # F1
from .problem_generator import problem_generator                   # F4
from .study_buddy import study_buddy_agent                         # F5
from .code_practical import code_practical_manager, code_practical_execute  # F6

logger = logging.getLogger(__name__)


# ============================================================
# 类型定义
# ============================================================

class AgentType(str, Enum):
    """Agent 类型 — 包含核心 Agent + 6 大差异化功能模块."""
    # 核心Agent
    QUESTION_PARSER = "question_parser"
    SOCRATIC_TUTOR = "socratic_tutor"
    CORRECTOR = "corrector"
    DIAGNOSTICIAN = "diagnostician"
    # 6 大功能模块
    LEARNING_PATH_PLANNER = "learning_path_planner"       # F1: 动态路径规划
    PROBLEM_GENERATOR = "problem_generator"               # F4: 举一反三生成器
    STUDY_BUDDY = "study_buddy"                           # F5: AI研友
    CODE_PRACTICAL = "code_practical"                     # F6: 代码实战
    UNKNOWN = "unknown"


class UserIntent(str, Enum):
    """用户意图 — 扩展支持 6 大新功能."""
    SEARCH_QUESTION = "search_question"
    START_CHAT = "start_chat"
    CONTINUE_CHAT = "continue_chat"
    CORRECT_HOMEWORK = "correct_homework"
    GET_DIAGNOSIS = "get_diagnosis"
    PLAN_LEARNING_PATH = "plan_learning_path"             # F1: 规划学习路径
    ADJUST_PATH = "adjust_path"                           # F1: 调整路径
    GENERATE_VARIANTS = "generate_variants"               # F4: 举一反三
    VALIDATE_MASTERY = "validate_mastery"                 # F4: 验证掌握
    START_STUDY_GROUP = "start_study_group"               # F5: 启动研友小组
    BUDDY_CHAT = "buddy_chat"                             # F5: 研友对话
    CODE_CHALLENGE = "code_challenge"                     # F6: 代码挑战
    EXECUTE_CODE = "execute_code"                         # F6: 执行代码
    THINKING_TRACE = "thinking_trace"                     # F2: 思维追踪 (内部)
    EMOTION_DETECT = "emotion_detect"                     # F3: 情绪检测 (内部)
    CODE_VISUALIZE = "code_visualize"
    GENERAL_QA = "general_qa"


class OrchestratorState(TypedDict):
    """调度器状态."""
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    target_agent: str
    raw_input: dict
    result: dict
    session_id: str


# ============================================================
# 结构化输出模型 — 意图分类 (M4 延伸)
# ============================================================

class IntentClassification(BaseModel):
    """意图分类结构化输出."""
    intent: UserIntent = Field(description="识别的意图类型")
    target_agent: AgentType = Field(description="目标 Agent")
    confidence: float = Field(default=0.8, description="置信度 0~1")
    extracted_params: dict = Field(default_factory=dict, description="提取的参数")


# ============================================================
# Graph Nodes
# ============================================================

async def intent_classifier(state: OrchestratorState) -> dict:
    """节点: 意图分类 (with_structured_output).

    使用 LLM 结构化输出替代手动 JSON 解析 + 正则兜底。
    """
    llm = llm_gateway.get_chat_model()
    structured_llm = llm.with_structured_output(IntentClassification)

    user_text = ""
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, 'content'):
            user_text = last_msg.content[:500]

    # 使用集中式 Prompt
    prompt_template = get_prompt("intent_classifier")

    tool_descs = get_tool_descriptions()
    prompt_input = {
        "agent_list": "question_parser(搜题) | socratic_tutor(引导对话) | corrector(批改) | diagnostician(诊断)",
        "tool_list": "\n".join(f"- {t['name']}: {t['description']}" for t in tool_descs),
        "user_input": user_text or "(无文字输入，可能是图片)",
    }

    try:
        chain = prompt_template | structured_llm
        classification: IntentClassification = await chain.ainvoke(prompt_input)
        return {
            "intent": classification.intent.value,
            "target_agent": classification.target_agent.value,
            "raw_input": classification.extracted_params or state.get("raw_input", {}),
        }
    except Exception as e:
        logger.warning(f"结构化意图分类失败 ({e}), 回退到关键词匹配")
        return _fallback_classify(user_text)


def _fallback_classify(user_text: str) -> dict:
    """关键词匹配兜底 — 包含 6 大功能模块."""
    lower = (user_text or "").lower()
    if any(kw in lower for kw in ["搜题", "拍照", "识别题目", "parse"]):
        return {"intent": "search_question", "target_agent": "question_parser", "raw_input": {}}
    if any(kw in lower for kw in ["引导", "对话", "聊天", "chat"]):
        return {"intent": "start_chat", "target_agent": "socratic_tutor", "raw_input": {}}
    if any(kw in lower for kw in ["批改", "纠正", "correct"]):
        return {"intent": "correct_homework", "target_agent": "corrector", "raw_input": {}}
    if any(kw in lower for kw in ["诊断", "薄弱", "diagnosis"]):
        return {"intent": "get_diagnosis", "target_agent": "diagnostician", "raw_input": {}}
    # F1: 学习路径
    if any(kw in lower for kw in ["规划", "学习计划", "路径", "复习计划", "安排"]):
        return {"intent": "plan_learning_path", "target_agent": "learning_path_planner", "raw_input": {}}
    # F4: 举一反三
    if any(kw in lower for kw in ["举一反三", "变式题", "同类题", "类似题目", "再出几道"]):
        return {"intent": "generate_variants", "target_agent": "problem_generator", "raw_input": {}}
    # F5: AI研友
    if any(kw in lower for kw in ["研友", "小组讨论", "讨论模式", "ai同学", "一起学"]):
        return {"intent": "start_study_group", "target_agent": "study_buddy", "raw_input": {}}
    # F6: 代码实战
    if any(kw in lower for kw in ["代码挑战", "代码题", "写代码", "编程", "debug", "补全"]):
        return {"intent": "code_challenge", "target_agent": "code_practical", "raw_input": {}}
    return {"intent": "general_qa", "target_agent": "socratic_tutor", "raw_input": {}}


# ── M3: 分发节点 — 每个 Agent 一个独立 Node ───────────────

async def exec_question_parser(state: OrchestratorState) -> dict:
    """执行: QuestionParser Agent."""
    raw = state.get("raw_input", {})
    if raw.get("image_url"):
        result = await parser.parse_image(image_url=raw["image_url"])
    else:
        result = await parser.parse_text(raw.get("text", ""))
    return {"result": result}


async def exec_socratic_tutor(state: OrchestratorState) -> dict:
    """执行: SocraticTutor Agent."""
    intent = state.get("intent", "")
    session_id = state.get("session_id", "default")
    messages = state.get("messages", [])
    raw = state.get("raw_input", {})

    user_msg = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break

    if intent == UserIntent.START_CHAT.value:
        result = await tutor.generate_first_message(
            session_id=session_id,
            question_context=raw.get("question_context"),
        )
    else:
        result = await tutor.generate_response(
            session_id=session_id,
            user_message=user_msg,
            question_context=raw.get("question_context"),
        )
    return {"result": result}


async def exec_corrector(state: OrchestratorState) -> dict:
    """执行: Corrector Agent."""
    raw = state.get("raw_input", {})
    result = await corrector.correct(
        image_url=raw.get("image_url", ""),
        question_info=raw.get("question_info"),
    )
    return {"result": result}


async def exec_diagnostician(state: OrchestratorState) -> dict:
    """执行: Diagnostician Agent."""
    raw = state.get("raw_input", {})
    result = await diagnostician.diagnose(
        user_id=raw.get("user_id", "default"),
        time_range=raw.get("time_range", "recent_30d"),
    )
    return {"result": result}


async def exec_general_qa(state: OrchestratorState) -> dict:
    """执行: 通用 QA 兜底."""
    llm = llm_gateway.get_chat_model()
    messages = state.get("messages", [])
    response = await llm.ainvoke(list(messages))
    return {"result": {"message": response.content}}


# ── 6 大功能模块执行节点 ─────────────────────────────────────

async def exec_learning_path_planner(state: OrchestratorState) -> dict:
    """F1: 执行 — 动态学习路径规划."""
    raw = state.get("raw_input", {})
    profile_data = raw.get("student_profile") or {
        "user_id": raw.get("user_id", "default"),
        "target_score": raw.get("target_score", 360),
        "target_school": "",
        "current_level": "intermediate",
        "available_days": 90,
        "daily_hours": 4.0,
        "weak_subjects": [],
        "strong_subjects": [],
    }
    
    if raw.get("action") == "adjust":
        result = await learning_path_planner.adjust_path(
            plan_id=raw.get("plan_id", ""),
            trigger_type=raw.get("trigger_type", "manual"),
            new_diagnosis=raw.get("new_diagnosis"),
            feedback=raw.get("feedback", ""),
        )
    else:
        result = await learning_path_planner.generate_path(profile_data)
    return {"result": result}


async def exec_problem_generator(state: OrchestratorState) -> dict:
    """F4: 执行 — 举一反三题目生成."""
    raw = state.get("raw_input", {})
    action = raw.get("action", "generate")
    
    if action == "validate":
        result = await problem_generator.validate_mastery(
            topic=raw.get("topic", ""),
            attempt_results=raw.get("attempt_results", []),
        )
    else:
        result = await problem_generator.generate_variants(
            original_question=raw.get("original_question", ""),
            topic=raw.get("topic", ""),
            subject=raw.get("subject", ""),
            count=raw.get("count", 3),
            difficulty=raw.get("difficulty", "medium"),
        )
    return {"result": result}


async def exec_study_buddy(state: OrchestratorState) -> dict:
    """F5: 执行 — AI 研友对话."""
    raw = state.get("raw_input", {})
    session_id = state.get("session_id")
    user_msg = ""
    for m in reversed(state.get("messages", [])):
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break
    
    if raw.get("action") == "start" or not session_id or session_id == "default":
        from app.schemas.emotion import StudyBuddyConfig, StudyBuddyRole
        roles_raw = raw.get("roles", ["scholar"])
        role_enums = []
        for r in roles_raw:
            try: role_enums.append(StudyBuddyRole(r))
            except ValueError: pass
        
        config = StudyBuddyConfig(
            roles=role_enums or [StudyBuddyRole.SCHOLAR],
            topic=raw.get("topic", ""),
            mode=raw.get("mode", "debate"),
            difficulty=raw.get("difficulty", "medium"),
        )
        result = await study_buddy_agent.start_session(config)
    elif raw.get("action") == "end":
        result = await study_buddy_agent.end_session(session_id)
    else:
        result = await study_buddy_agent.continue_discussion(
            session_id=session_id, user_message=user_msg
        )
    return {"result": result}


async def exec_code_practical(state: OrchestratorState) -> dict:
    """F6: 执行 — 代码实战挑战."""
    raw = state.get("raw_input", {})
    
    if raw.get("action") == "execute":
        result = await code_practical_execute.ainvoke({
            "code": raw.get("code", ""),
            "challenge_id": raw.get("challenge_id", ""),
            "language": raw.get("language", "python"),
        })
    elif raw.get("action") == "list":
        challenges = code_practical_manager.list_challenges(
            subject=raw.get("subject"), topic=raw.get("topic"),
            challenge_type=raw.get("type"), difficulty=raw.get("difficulty"),
        )
        result = {"challenges": challenges}
    elif raw.get("action") == "explain":
        explanation = code_practical_manager.reveal_explanation(raw.get("challenge_id", ""))
        result = {"explanation": explanation}
    else:
        challenge_id = raw.get("challenge_id")
        challenge = code_practical_manager.get_challenge(challenge_id)
        result = challenge or {"error": "Challenge not found"}
    return {"result": result}


# ── M3: 路由函数 — 返回目标节点名称 ───────────────────────

AGENT_ROUTER_MAP: dict[str, str] = {
    # 核心Agent
    "question_parser": "exec_question_parser",
    "socratic_tutor": "exec_socratic_tutor",
    "corrector": "exec_corrector",
    "diagnostician": "exec_diagnostician",
    # 6 大功能模块
    "learning_path_planner": "exec_learning_path_planner",   # F1
    "problem_generator": "exec_problem_generator",           # F4
    "study_buddy": "exec_study_buddy",                       # F5
    "code_practical": "exec_code_practical",                 # F6
    # 兜底
    "unknown": "exec_general_qa",
}


def route_to_executor(state: OrchestratorState) -> str:
    """M3: 条件边 — 根据 target_agent 路由到对应执行节点.

    替代之前的 route_and_execute 中的 if-elif match/case.
    使用查找表 (dispatch table) 模式，符合 Open-Closed 原则：
      新增 Agent 只需添加节点 + 更新 AGENT_ROUTER_MAP，无需改此函数。
    """
    target = state.get("target_agent", "unknown")
    node_name = AGENT_ROUTER_MAP.get(target, "exec_general_qa")
    logger.debug(f"Orchestrator 路由: target={target} → node={node_name}")
    return node_name


# ============================================================
# TuringMateOrchestrator 主类
# ============================================================

class TuringMateOrchestrator:
    """基于 LangGraph 条件边分发的调度器.

    架构改进 (vs 旧版):
      旧: classify → route_and_execute (if-elif 一坨)
      新: classify → route_to_executor (查找表) → exec_* (独立节点)
    """

    def __init__(self):
        self._graph = self._build_graph()
        self._agents = {
            AgentType.QUESTION_PARSER: parser,
            AgentType.SOCRATIC_TUTOR: tutor,
            AgentType.CORRECTOR: corrector,
            AgentType.DIAGNOSTICIAN: diagnostician,
            # 6 大功能模块
            AgentType.LEARNING_PATH_PLANNER: learning_path_planner,
            AgentType.PROBLEM_GENERATOR: problem_generator,
            AgentType.STUDY_BUDDY: study_buddy_agent,
            AgentType.CODE_PRACTICAL: code_practical_manager,
        }

    def _build_graph(self):
        """构建调度状态图 — 使用条件边分发 (含 6 大功能模块)."""

        graph = StateGraph(OrchestratorState)

        # ── 注册所有节点 ──
        graph.add_node("classify_intent", intent_classifier)

        # 核心Agent 节点
        graph.add_node("exec_question_parser", exec_question_parser)
        graph.add_node("exec_socratic_tutor", exec_socratic_tutor)
        graph.add_node("exec_corrector", exec_corrector)
        graph.add_node("exec_diagnostician", exec_diagnostician)
        graph.add_node("exec_general_qa", exec_general_qa)

        # 6 大功能模块节点 (F1-F6)
        graph.add_node("exec_learning_path_planner", exec_learning_path_planner)
        graph.add_node("exec_problem_generator", exec_problem_generator)
        graph.add_node("exec_study_buddy", exec_study_buddy)
        graph.add_node("exec_code_practical", exec_code_practical)

        # ── 边连接 ──
        graph.add_edge(START, "classify_intent")

        # M3 核心: 条件边 — 从 classify 路由到对应 exec_* 节点
        graph.add_conditional_edges(
            "classify_intent",
            route_to_executor,
            {
                "exec_question_parser": "exec_question_parser",
                "exec_socratic_tutor": "exec_socratic_tutor",
                "exec_corrector": "exec_corrector",
                "exec_diagnostician": "exec_diagnostician",
                # 6 大功能模块路由目标
                "exec_learning_path_planner": "exec_learning_path_planner",
                "exec_problem_generator": "exec_problem_generator",
                "exec_study_buddy": "exec_study_buddy",
                "exec_code_practical": "exec_code_practical",
                # 兜底
                "exec_general_qa": "exec_general_qa",
            },
        )

        # 所有 exec 节点汇聚到 END
        all_exec_nodes = (
            "exec_question_parser", "exec_socratic_tutor",
            "exec_corrector", "exec_diagnostician", "exec_general_qa",
            # F1-F6
            "exec_learning_path_planner", "exec_problem_generator",
            "exec_study_buddy", "exec_code_practical",
        )
        for node in all_exec_nodes:
            graph.add_conditional_edges(
                node,
                lambda s: "__end__",
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
        """处理用户请求."""
        config = {"configurable": {"thread_id": session_id}}

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
                if node_name.startswith("exec_"):
                    result = node_output.get("result", {})
                    if "message" in result:
                        yield result["message"]

    @property
    def agents(self):
        return self._agents

    @property
    def router_map(self) -> dict[str, str]:
        """返回当前路由映射表（便于调试和动态修改）."""
        return dict(AGENT_ROUTER_MAP)


# 全局单例
orchestrator = TuringMateOrchestrator()
