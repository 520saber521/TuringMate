"""TuringMate Agents - 基于 LangChain / LangGraph 的 Agent 集合.

所有 Agent 使用 LangChain 组件:
  - ChatOpenAI (via LLM Gateway) 对话
  - @tool 工具调用
  - ChromaDB RAG 检索
  - LangGraph StateGraph 编排

Agent 清单:
  - SocraticTutor:   苏格拉底教学 (LangGraph StateGraph)
  - QuestionParser:  题目识别解析 (LangChain Chain)
  - Corrector:       手写批改 (LangChain + 多模态)
  - Diagnostician:   薄弱点诊断 (LangChain Chain)
  - Orchestrator:    主调度器 (LangGraph StateGraph)
"""

from .socratic_tutor import socratic_tutor_agent, SocraticTutorAgent, TutorStage, TutorState
from .question_parser import question_parser_agent, QuestionParserAgent, ParsedQuestion
from .corrector import corrector_agent, CorrectorAgent
from .diagnostician import diagnostician_agent, DiagnosticianAgent
from .orchestrator import orchestrator, TuringMateOrchestrator, AgentType, UserIntent

__all__ = [
    # Agents
    "socratic_tutor_agent",
    "question_parser_agent",
    "corrector_agent",
    "diagnostician_agent",
    "orchestrator",
    # Classes
    "SocraticTutorAgent",
    "QuestionParserAgent",
    "CorrectorAgent",
    "DiagnosticianAgent",
    "TuringMateOrchestrator",
    # Types
    "TutorStage",
    "TutorState",
    "ParsedQuestion",
    "AgentType",
    "UserIntent",
]
