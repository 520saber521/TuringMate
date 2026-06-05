"""Diagnostician Agent - 薄弱点诊断 Agent.

使用 LangChain + with_structured_output() 分析学生错题记录和学习数据，
生成四科雷达图数据和薄弱点报告。
"""

import json
import logging
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway
from app.core.tools import knowledge_graph

logger = logging.getLogger(__name__)

KNOWLEDGE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"


# ── Pydantic 输出模型 ────────────────────────────────────────────


class RadarScores(BaseModel):
    """四科雷达图分数."""
    数据结构: int = Field(description="数据结构得分 0-100")
    计算机组成原理: int = Field(description="计算机组成原理得分 0-100")
    操作系统: int = Field(description="操作系统得分 0-100")
    计算机网络: int = Field(description="计算机网络得分 0-100")


class WeakPointDetail(BaseModel):
    """薄弱点详情."""
    subject: str = Field(description="科目")
    topic: str = Field(description="具体知识点")
    score: int = Field(description="掌握程度分 (0-100)")
    description: str = Field(description="薄弱原因分析")
    suggestion: str = Field(description="改进建议")


class StudyPlanWeek(BaseModel):
    """学习计划周."""
    week: int = Field(description="第几周")
    focus: str = Field(description="本周重点")
    tasks: list[str] = Field(description="任务列表")


class DiagnosisReport(BaseModel):
    """完整诊断报告."""
    summary: str = Field(description="总体评价（100字左右）")
    radar_scores: RadarScores = Field(description="四科雷达分数")
    weak_points: list[WeakPointDetail] = Field(default_factory=list, description="薄弱环节")
    study_plan: list[StudyPlanWeek] = Field(default_factory=list, description="学习计划")
    encouragement: str = Field(default="", description="鼓励话语")


DIAGNOSIS_SYSTEM_PROMPT = """你是 TuringMate 的学习诊断专家。

基于学生的错题记录、练习历史和知识图谱，分析其薄弱环节并生成诊断报告。

## 诊断原则：
- 基于真实数据分析，不要凭空捏造
- 分数要有区分度，体现真实差距
- 建议要可执行、有优先级"""


class DiagnosticianAgent:
    """基于 LangChain + Structured Output 的诊断 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        # 结构化 LLM — 自动输出 DiagnosisReport
        self._structured_llm = self._llm.with_structured_output(DiagnosisReport)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", DIAGNOSIS_SYSTEM_PROMPT),
            ("human", "{input}"),
        ])

    async def diagnose(
        self,
        user_id: str,
        time_range: str = "recent_30d",
    ) -> dict:
        """生成学习诊断报告.

        Args:
            user_id: 学生 ID
            time_range: 时间范围 (recent_7d / recent_30d / all)

        Returns:
            完整诊断报告字典
        """
        # 1. 收集学生数据
        student_data = await self._collect_student_data(user_id)

        # 2. 获取知识图谱结构作为参考
        kg_result = await knowledge_graph.ainvoke({"action": "get_nodes"})
        knowledge_structure = kg_result.get("nodes", [])

        # 3. 构建输入
        input_text = f"""学生ID: {user_id}
时间范围: {time_range}

## 学生练习数据：
{json.dumps(student_data, ensure_ascii=False, indent=2)}

## 知识体系结构（共 {len(knowledge_structure)} 个知识点）：
{json.dumps(knowledge_structure[:20], ensure_ascii=False, indent=2) if knowledge_structure else '暂无'}

请基于以上数据生成诊断报告。"""

        try:
            chain = self._prompt | self._structured_llm
            report: DiagnosisReport = await chain.ainvoke({"input": input_text})
            return report.model_dump()
        except Exception as e:
            logger.error(f"Diagnostician 诊断失败: {e}")
            return self._generate_fallback_report(student_data)

    async def _collect_student_data(self, user_id: str) -> dict:
        """收集学生数据 — 从数据库查询真实错题记录."""
        from app.models.database import SessionLocal
        from app.crud.diagnosis import diagnosis_crud

        subject_names = [("ds", "数据结构"), ("co", "计组"), ("os", "操作系统"), ("cn", "网络")]

        # 知识图谱知识节点
        subjects_data = {}
        for _prefix, name in subject_names:
            try:
                result = await knowledge_graph.ainvoke({"action": "get_nodes", "subject": name})
                nodes = result.get("nodes", [])
                subjects_data[name] = [n["name"] for n in nodes if isinstance(n, dict) and "name" in n]
            except Exception:
                subjects_data[name] = []

        # 从数据库查询真实错题数据
        db = SessionLocal()
        try:
            mistakes = diagnosis_crud.list_mistakes_by_user(db, user_id, limit=200)
            total_practices = len(mistakes)

            # 按科目和知识点聚合错误统计
            mistake_summary: dict[str, dict[str, dict]] = {}
            for m in mistakes:
                subject = getattr(m, "subject", None)
                if not subject:
                    # 尝试从 knowledge_tags 推断科目
                    tags = m.knowledge_tags or []
                    subject = tags[0] if tags else "未知"

                if subject not in mistake_summary:
                    mistake_summary[subject] = {}
                for tag in (m.knowledge_tags or [])[:2]:
                    if tag not in mistake_summary[subject]:
                        mistake_summary[subject][tag] = {"count": 0, "last_wrong": ""}
                    mistake_summary[subject][tag]["count"] += 1
                    last_date = str(m.created_at.date()) if m.created_at else ""
                    if last_date > mistake_summary[subject][tag]["last_wrong"]:
                        mistake_summary[subject][tag]["last_wrong"] = last_date

            # 转换为前端格式
            formatted_mistakes = {}
            for subject, topics in mistake_summary.items():
                formatted_mistakes[subject] = [
                    {"topic": topic, "count": data["count"], "last_wrong": data["last_wrong"]}
                    for topic, data in sorted(topics.items(), key=lambda x: -x[1]["count"])[:6]
                ]

            # 计算正确率
            correct_count = total_practices - len(mistakes)
            accuracy_rate = round(correct_count / max(total_practices, 1) * 100, 1)

            return {
                "user_id": user_id,
                "total_practices": total_practices,
                "practice_days": len({str(m.created_at.date()) for m in mistakes if m.created_at}),
                "accuracy_rate": accuracy_rate,
                "mistake_summary": formatted_mistakes,
                "knowledge_coverage": subjects_data,
            }
        finally:
            db.close()

    @staticmethod
    def _generate_fallback_report(data: dict = None) -> dict:
        """兜底报告生成."""
        mistakes = (data or {}).get("mistake_summary", {})
        weak_points = []
        for subject, items in mistakes.items():
            for item in items:
                count = item.get("count", 0)
                score = max(30, 85 - count * 8)
                weak_points.append({
                    "subject": subject,
                    "topic": item.get("topic", ""),
                    "score": score,
                    "description": f"近30天错误{count}次",
                    "suggestion": f"建议重点复习{item.get('topic', '')}",
                })

        weak_points.sort(key=lambda x: x["score"])

        return {
            "summary": "根据近期练习情况分析，学生在部分知识点上存在明显薄弱环节。",
            "radar_scores": {
                "数据结构": 75,
                "计算机组成原理": 62,
                "操作系统": 70,
                "计算机网络": 55,
            },
            "weak_points": weak_points[:6],
            "study_plan": [
                {"week": 1, "focus": "补强网络基础", "tasks": ["复习TCP拥塞控制", "子网划分练习"]},
                {"week": 2, "focus": "巩固计组核心", "tasks": ["浮点数专题", "流水线习题"]},
                {"week": 3, "focus": "综合提升", "tasks": ["跨科关联题", "真题模拟"]},
            ],
            "encouragement": "坚持就是胜利！每天进步一点点，408一定没问题！",
            "is_fallback": True,
        }


# 全局单例
diagnostician_agent = DiagnosticianAgent()
