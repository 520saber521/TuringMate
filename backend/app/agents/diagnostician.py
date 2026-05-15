"""Diagnostician Agent - 薄弱点诊断 Agent.

使用 LangChain Chain 分析学生错题记录和学习数据，
生成四科雷达图数据和薄弱点报告。
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.llm_gateway import llm_gateway
from app.core.tools import knowledge_graph, question_search

logger = logging.getLogger(__name__)

KNOWLEDGE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"


DIAGNOSIS_SYSTEM_PROMPT = """你是 TuringMate 的学习诊断专家。

基于学生的错题记录、练习历史和知识图谱，分析其薄弱环节并生成诊断报告。

## 输出 JSON 格式：
{
  "summary": "总体评价（100字左右）",
  "radar_scores": {
    "数据结构": 72,
    "计算机组成原理": 65,
    "操作系统": 78,
    "计算机网络": 58
  },
  "weak_points": [
    {
      "subject": "科目",
      "topic": "具体知识点",
      "score": 45,
      "description": "薄弱原因分析",
      "suggestion": "改进建议"
    }
  ],
  "study_plan": [
    {"week": 1, "focus": "本周重点", "tasks": ["任务1", "任务2"]}
  ],
  "encouragement": "鼓励话语"
}

## 诊断原则：
- 基于真实数据分析，不要凭空捏造
- 分数要有区分度，体现真实差距
- 建议要可执行、有优先级"""


class DiagnosticianAgent:
    """基于 LangChain 的诊断 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
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
            完整诊断报告
        """
        # 1. 收集学生数据
        student_data = await self._collect_student_data(user_id)

        # 2. 获取知识图谱结构作为参考
        kg_result = await knowledge_graph.ainvoke({"action": "get_nodes"})
        knowledge_structure = kg_result.get("nodes", [])

        # 3. 用 LLM 生成诊断
        input_text = f"""学生ID: {user_id}
时间范围: {time_range}

## 学生练习数据：
{json.dumps(student_data, ensure_ascii=False, indent=2)}

## 知识体系结构（共 {len(knowledge_structure)} 个知识点）：
{json.dumps(knowledge_structure[:20], ensure_ascii=False, indent=2) if knowledge_structure else '暂无'}

请基于以上数据生成诊断报告。"""

        try:
            chain = self._prompt | self._llm
            response = await chain.ainvoke({"input": input_text})
            raw_result = response.content if hasattr(response, 'content') else str(response)
            return self._extract_report(raw_result)
        except Exception as e:
            logger.error(f"Diagnostician 诊断失败: {e}")
            return self._generate_fallback_report(student_data)

    async def _collect_student_data(self, user_id: str) -> dict:
        """收集学生数据（MVP 阶段模拟 + 真实数据接入点）."""
        # TODO: 从数据库获取真实学生数据
        # 当前返回模拟数据，后续替换为 DB 查询

        # 尝试从知识图谱加载真实节点信息
        subjects_data = {}
        for prefix, name in [("ds", "数据结构"), ("co", "计组"), ("os", "操作系统"), ("cn", "网络")]:
            try:
                result = await knowledge_graph.ainvoke({"action": "get_nodes", "subject": name})
                nodes = result.get("nodes", [])
                subjects_data[name] = [n["name"] for n in nodes if isinstance(n, dict) and "name" in n]
            except Exception:
                subjects_data[name] = []

        # 模拟错题数据（后续从 DB 替换）
        mock_mistakes = {
            "数据结构": [
                {"topic": "链表操作", "count": 3, "last_wrong": "2026-05-10"},
                {"topic": "二叉树遍历", "count": 2, "last_wrong": "2026-05-08"},
                {"topic": "快速排序", "count": 1, "last_wrong": "2026-05-12"},
                {"topic": "哈希表冲突解决", "count": 1, "last_wrong": "2026-05-13"},
            ],
            "计组": [
                {"topic": "浮点数表示", "count": 4, "last_wrong": "2026-05-11"},
                {"topic": "指令流水线", "count": 2, "last_wrong": "2026-05-09"},
                {"topic": "Cache 映射", "count": 2, "last_wrong": "2026-05-07"},
            ],
            "操作系统": [
                {"topic": "进程调度算法", "count": 2, "last_wrong": "2026-05-06"},
                {"topic": "死锁检测", "count": 1, "last_wrong": "2026-05-11"},
                {"topic": "页面置换算法", "count": 3, "last_wrong": "2026-05-14"},
            ],
            "网络": [
                {"topic": "TCP拥塞控制", "count": 5, "last_wrong": "2026-05-13"},
                {"topic": "子网划分", "count": 3, "last_wrong": "2026-05-10"},
                {"topic": "DNS解析过程", "count": 2, "last_wrong": "2026-05-08"},
                {"topic": "HTTP协议", "count": 1, "last_wrong": "2026-05-12"},
            ],
        }

        total_mistakes = sum(len(v) for v in mock_mistakes.values())
        practice_days = 15  # 模拟值

        return {
            "user_id": user_id,
            "total_practices": total_mistakes + 25,  # 练习总数
            "practice_days": practice_days,
            "accuracy_rate": round(68.5 + hash(user_id) % 20, 1),  # 模拟正确率
            "mistake_summary": mock_mistakes,
            "knowledge_coverage": subjects_data,
            "data_note": "当前为模拟数据，生产环境需接入数据库",
        }

    def _extract_report(self, raw_response: str) -> dict:
        """提取结构化报告."""
        import json, re

        try:
            data = json.loads(raw_response.strip())
            if "radar_scores" in data or "weak_points" in data:
                return data
        except json.JSONDecodeError:
            pass

        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_response)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        return self._generate_fallback_report({})

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
