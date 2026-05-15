"""Orchestrator Agent - 主调度器 (LangGraph StateGraph).

根据用户意图路由到对应子 Agent：
- 题目识别 → QuestionParser
- 引导讲解 → SocraticTutor
- 手写批改 → Corrector
- 薄弱点诊断 → Diagnostician

MVP 阶段使用简单路由逻辑，后续升级为 LangGraph 状态图。
"""

import logging
from enum import Enum

from app.agents.question_parser import QuestionParserAgent
from app.agents.socratic_tutor import SocraticTutorAgent
from app.agents.corrector import CorrectorAgent
from app.agents.diagnostician import DiagnosticianAgent

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    QUESTION_PARSER = "question_parser"
    SOCRATIC_TUTOR = "socratic_tutor"
    CORRECTOR = "corrector"
    DIAGNOSTICIAN = "diagnostician"


class OrchestratorAgent:
    """主调度 Agent - 路由用户请求到对应子 Agent."""

    def __init__(self):
        self._agents: dict[AgentType, object] = {
            AgentType.QUESTION_PARSER: QuestionParserAgent(),
            AgentType.SOCRATIC_TUTOR: SocraticTutorAgent(),
            AgentType.CORRECTOR: CorrectorAgent(),
            AgentType.DIAGNOSTICIAN: DiagnosticianAgent(),
        }

    def register_agent(self, agent_type: AgentType, agent: object):
        """注册子 Agent."""
        self._agents[agent_type] = agent

    def get_agent(self, agent_type: AgentType):
        """获取已注册的 Agent."""
        return self._agents.get(agent_type)

    def route(self, intent: str, **kwargs) -> AgentType | None:
        """根据意图路由到对应的 Agent."""
        route_map = {
            "parse_question": AgentType.QUESTION_PARSER,
            "start_chat": AgentType.SOCRATIC_TUTOR,
            "continue_chat": AgentType.SOCRATIC_TUTOR,
            "stream_chat": AgentType.SOCRATIC_TUTOR,
            "analyze_correction": AgentType.CORRECTOR,
            "generate_diagnosis": AgentType.DIAGNOSTICIAN,
        }
        return route_map.get(intent)

    async def execute(self, intent: str, **kwargs) -> dict:
        """执行路由并调用对应 Agent.

        Args:
            intent: 意图标识
            **kwargs: 传递给 Agent 的参数

        Returns:
            Agent 执行结果
        """
        agent_type = self.route(intent)
        if not agent_type:
            raise ValueError(f"Unknown intent: {intent}")

        agent = self._agents.get(agent_type)
        if not agent:
            raise ValueError(f"Agent not registered: {agent_type}")

        logger.info(f"Orchestrator: 路由 intent={intent} → agent={agent_type.value}")

        # 根据意图调用对应方法
        if agent_type == AgentType.QUESTION_PARSER:
            return await agent.parse_image(**kwargs)
        elif agent_type == AgentType.SOCRATIC_TUTOR:
            if intent == "start_chat":
                return await agent.generate_first_message(**kwargs)
            else:
                return await agent.generate_response(**kwargs)
        elif agent_type == AgentType.CORRECTOR:
            return await agent.analyze(**kwargs)
        elif agent_type == AgentType.DIAGNOSTICIAN:
            return await agent.generate_report(**kwargs)
        else:
            raise ValueError(f"Unhandled agent type: {agent_type}")


orchestrator = OrchestratorAgent()
