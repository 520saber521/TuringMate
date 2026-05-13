"""Orchestrator Agent - 主调度器 (LangGraph StateGraph).

根据用户意图路由到对应子 Agent：
- 题目识别 → QuestionParser
- 引导讲解 → SocraticTutor
- 手写批改 → Corrector
- 薄弱点诊断 → Diagnostician

MVP 阶段使用简单路由逻辑，后续升级为 LangGraph 状态图。
"""

from enum import Enum


class AgentType(str, Enum):
    QUESTION_PARSER = "question_parser"
    SOCRATIC_TUTOR = "socratic_tutor"
    CORRECTOR = "corrector"
    DIAGNOSTICIAN = "diagnostician"


class OrchestratorAgent:
    """主调度 Agent - 路由用户请求到对应子 Agent."""

    def __init__(self):
        self._agents: dict[AgentType, object] = {}

    def register_agent(self, agent_type: AgentType, agent: object):
        """注册子 Agent."""
        self._agents[agent_type] = agent

    def route(self, intent: str, **kwargs) -> str:
        """根据意图路由到对应的 Agent."""
        # TODO: 使用 LLM 做意图识别，MVP 阶段用规则匹配
        route_map = {
            "parse_question": AgentType.QUESTION_PARSER,
            "start_chat": AgentType.SOCRATIC_TUTOR,
            "continue_chat": AgentType.SOCRATIC_TUTOR,
            "analyze_correction": AgentType.CORRECTOR,
            "generate_diagnosis": AgentType.DIAGNOSTICIAN,
        }
        return route_map.get(intent)

    async def execute(self, intent: str, **kwargs) -> dict:
        """执行路由并返回结果."""
        agent_type = self.route(intent)
        if not agent_type:
            raise ValueError(f"Unknown intent: {intent}")

        agent = self._agents.get(agent_type)
        if not agent:
            raise ValueError(f"Agent not registered: {agent_type}")

        # TODO: 调用实际 Agent 的执行方法
        return {"status": "routed", "agent": agent_type.value}


orchestrator = OrchestratorAgent()
