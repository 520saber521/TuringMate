"""TuringMate Agents - 基于 LangChain / LangGraph 的 Agent 集合.

所有 Agent 使用 LangChain 组件:
  - ChatOpenAI (via LLM Gateway) 对话
  - @tool 工具调用
  - ChromaDB RAG 检索
  - LangGraph StateGraph 编排

核心 Agent:
  - SocraticTutor:   苏格拉底教学 (LangGraph StateGraph)
  - QuestionParser:  题目识别解析 (LangChain Chain)
  - Corrector:       手写批改 (LangChain + 多模态)
  - Diagnostician:   薄弱点诊断 (LangChain Chain)
  - Orchestrator:    主调度器 (LangGraph StateGraph)

6 大差异化功能模块 (Features):
  - LearningPathPlanner:    F1 动态学习路径规划器
  - ThinkingTracer:         F2 思维过程可视化回放
  - EmotionDetector:        F3 情绪感知与状态调节
  - ProblemGenerator:       F4 「举一反三」题目生成器
  - StudyBuddyAgent:        F5 AI 研友多角色系统
  - CodePracticalManager:   F6 「代码即题目」实战模块
"""

from .socratic_tutor import socratic_tutor_agent, SocraticTutorAgent, TutorStage, TutorState
from .question_parser import question_parser_agent, QuestionParserAgent, ParsedQuestion
from .corrector import corrector_agent, CorrectorAgent
from .diagnostician import diagnostician_agent, DiagnosticianAgent
from .orchestrator import orchestrator, TuringMateOrchestrator, AgentType, UserIntent

# F1: 动态学习路径规划
from .learning_path_planner import learning_path_planner, LearningPathPlannerAgent

# F2: 思维过程可视化
from .thinking_tracer import ThinkingTracer, create_tracer

# F3: 情绪感知与状态调节
from .emotion_detector import emotion_detector, EmotionDetector, TeachingMode

# F4: 「举一反三」题目生成
from .problem_generator import problem_generator, ProblemGeneratorAgent

# F5: AI 研友多角色系统
from .study_buddy import study_buddy_agent, StudyBuddyAgent

# F6: 「代码即题目」实战模块
from .code_practical import code_practical_manager, code_practical_execute, CodeChallenge, ChallengeType

__all__ = [
    # 核心Agents
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
    "TutorStage", "TutorState", "ParsedQuestion",
    "AgentType", "UserIntent",
    # F1-F6 功能模块
    "learning_path_planner", "LearningPathPlannerAgent",
    "ThinkingTracer", "create_tracer",
    "emotion_detector", "EmotionDetector", "TeachingMode",
    "problem_generator", "ProblemGeneratorAgent",
    "study_buddy_agent", "StudyBuddyAgent",
    "code_practical_manager", "code_practical_execute",
    "CodeChallenge", "ChallengeType",
]
