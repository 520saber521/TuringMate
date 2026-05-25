"""Learning Path Planner Agent — 动态学习路径规划器.

差异化核心:
  - 不是固定章节排列，而是基于薄弱点动态排序
  - 知识点关联感知（知识图谱驱动）
  - 支持诊断结果变化时动态调整

架构:
  1. 输入: 学生目标(目标分/目标校) + 当前水平
  2. 调用 Diagnostician 获取薄弱点数据
  3. 查询知识图谱获取知识点关联关系
  4. LLM 生成动态优先级排序的复习计划
  5. 输出: LearningPathPlan (每日任务 + 阶段划分 + 关联链路)
"""

import json
import logging
import uuid
from datetime import datetime, timedelta

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway
from app.core.tools import knowledge_graph, question_search
from app.agents.diagnostician import diagnostician_agent
from app.api.utils import retry_async
from app.schemas.learning_path import (
    LearningPathPlan, StudentProfile, KnowledgePriority,
    DailyTask, PathPhase, PathAdjustment,
)

logger = logging.getLogger(__name__)


# ── Pydantic 结构化输出 ──────────────────────────────────────


class PathPlanOutput(BaseModel):
    """LLM 结构化输出 — 学习路径计划."""
    summary: str = Field(description="路线总结（200字左右）")
    phases_json: str = Field(
        description='''JSON 数组，每个阶段:
        [{"phase_id": "p1", "phase_name": "...", "start_day": 1, "end_day": 14,
          "goal": "...", "key_topics": [...], "strategy": "..."}]'''
    )
    priorities_json: str = Field(
        description='''JSON 数组，知识点优先级:
        [{"topic": "内存管理", "subject": "操作系统", "priority_score": 95,
          "reason": "诊断显示严重薄弱且是高频考点",
          "related_topics": ["页表与地址转换", "进程调度"],
          "estimated_days": 3}]'''
    )
    daily_tasks_json: str = Field(
        description='''JSON 数组，前7天详细任务示例:
        [{"day": 1, "subject": "操作系统", "focus_topic": "内存管理",
          "tasks": ["复习虚拟内存基本概念", "做2道页式管理真题"],
          "difficulty": "medium", "estimated_minutes": 120}]'''
    )
    association_chains_json: str = Field(
        description='''JSON 数组，关联学习链路:
        [["内存管理", "页表与地址转换", "进程调度"],
         ["TCP拥塞控制", "滑动窗口", "流量控制"]]'''
    )
    milestones_json: str = Field(
        description='JSON 数组，关键里程碑: ["Day 14: 完成OS基础补强", ...]'
    )


LEARNING_PATH_SYSTEM_PROMPT = """你是 TuringMate 的「动态学习导航」规划师。

你的职责不是机械地按章节排课表，而是像私人教练一样：
- **根据学生的薄弱点重新排列优先级**（最弱的先补）
- **利用知识点内在关联设计学习顺序**
- **考虑时间约束和目标分数**

## 核心原则：

### 1. 弱点优先排序
如果学生"内存管理"薄弱：
- ❌ 不要按教材顺序：进程→调度→内存→文件...
- ✅ 应该：先集中突破内存管理 → 关联复习页表/地址转换 → 再回到进程调度（此时理解更深）

### 2. 关联感知
计算机考研408的知识点是高度关联的：
- 内存管理 ↔ 页表 ↔ 进程调度 ↔ 地址空间
- TCP拥塞控制 ↔ 滑动窗口 ↔ 流量控制
- 二叉树 ↔ 排序算法 ↔ 查找结构

你要主动发现并利用这些关联。

### 3. 时间自适应
- 距考试90天 vs 距30天：策略完全不同
- 每天2小时 vs 每天6小时：任务密度不同
- 目标300分 vs 目标120分：深度和广度不同

## 输出要求：
1. 计划要具体到每天做什么（前7天详细，后面可以按阶段概括）
2. 每个任务要有明确的可交付成果（如"做完X道题"、"背会Y个公式"）
3. 标注关键里程碑节点
4. 列出所有发现的重要知识点关联链路"""


class LearningPathPlannerAgent:
    """动态学习路径规划器 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        self._structured_llm = self._llm.with_structured_output(PathPlanOutput)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", LEARNING_PATH_SYSTEM_PROMPT),
            ("human", "{input}"),
        ])
        # 已生成的计划缓存 {plan_id: plan_dict}
        self._plans: dict[str, dict] = {}

    @retry_async(max_attempts=3)
    async def generate_path(
        self,
        student_profile: dict | StudentProfile,
    ) -> dict:
        """生成动态学习路径.

        Args:
            student_profile: 学生画像 (dict 或 StudentProfile 对象)

        Returns:
            LearningPathPlan 字典
        """
        if isinstance(student_profile, dict):
            profile = StudentProfile(**student_profile)
        else:
            profile = student_profile

        # 1. 获取诊断数据（调用 Diagnostician）
        logger.info(f"LearningPath: 为用户 {profile.user_id} 生成路径...")
        diagnosis = await diagnostician_agent.diagnose(
            user_id=profile.user_id,
            time_range="recent_30d",
        )

        # 2. 获取知识图谱关联数据
        kg_nodes_result = await knowledge_graph.ainvoke({"action": "get_nodes"})
        kg_edges_result = await knowledge_graph.ainvoke({"action": "get_edges"})
        all_nodes = kg_nodes_result.get("nodes", [])
        all_edges = kg_edges_result.get("edges", [])

        # 3. 构建 LLM 输入
        input_text = self._build_input(profile, diagnosis, all_nodes, all_edges)

        try:
            chain = self._prompt | self._structured_llm
            output: PathPlanOutput = await chain.ainvoke({"input": input_text})
            return self._to_plan(output, profile, diagnosis)
        except Exception as e:
            logger.error(f"LearningPath 规划失败: {e}")
            return self._generate_fallback_path(profile, diagnosis)

    async def adjust_path(
        self,
        plan_id: str,
        trigger_type: str,
        new_diagnosis: dict | None = None,
        feedback: str = "",
    ) -> dict:
        """动态调整已有学习路径.

        Args:
            plan_id: 原计划 ID
            trigger_type: 调整触发类型
            new_diagnosis: 新的诊断数据（可选）
            feedback: 用户反馈

        Returns:
            更新后的 LearningPathPlan 字典
        """
        old_plan = self._plans.get(plan_id)
        if not old_plan:
            raise ValueError(f"Plan {plan_id} 不存在")

        adjustment = PathAdjustment(
            adjustment_id=f"adj_{uuid.uuid4().hex[:8]}",
            trigger=trigger_type,
            original_plan=old_plan.get("summary", "")[:100],
            adjusted_plan="",
            reason=feedback or f"Triggered by {trigger_type}",
            timestamp=datetime.now().isoformat(),
        )

        # 如果有新诊断，重新生成部分计划
        if new_diagnosis and trigger_type == "diagnosis_update":
            profile_data = old_plan.get("student_profile", {})
            new_profile = StudentProfile(**{k: v for k, v in profile_data.items()
                                            if k in StudentProfile.model_fields})
            new_plan = await self.generate_path(new_profile)
            new_plan["adjustments"] = old_plan.get("adjustments", []) + [adjustment.model_dump()]
            new_plan["version"] = (old_plan.get("version", 1) or 1) + 1
            self._plans[new_plan["plan_id"]] = new_plan
            return new_plan

        # 否则仅记录调整（深拷贝避免污染缓存）
        import copy
        updated_plan = copy.deepcopy(old_plan)
        updated_plan["adjustments"] = updated_plan.get("adjustments", []) + [adjustment.model_dump()]
        updated_plan["version"] = (updated_plan.get("version", 1) or 1) + 1
        # 同步更新缓存引用
        self._plans[plan_id] = updated_plan
        return updated_plan

    def _build_input(
        self,
        profile: StudentProfile,
        diagnosis: dict,
        nodes: list[dict],
        edges: list[dict],
    ) -> str:
        """构建 LLM 输入文本."""
        weak_points = diagnosis.get("weak_points", [])
        radar = diagnosis.get("radar_scores", {})

        node_summary = "\n".join([
            f"- [{n.get('subject', '?')}] {n.get('name', '')}"
            for n in nodes[:50]
        ]) if nodes else "(暂无)"

        edge_summary = "\n".join([
            f"- {e.get('source', '')} → {e.get('target', '')}"
            f" ({e.get('relation', '相关')})"
            for e in edges[:30]
        ]) if edges else "(暂无)"

        weak_summary = "\n".join([
            f"- [{wp.get('subject', '')}] {wp.get('topic', '')}: "
            f"{wp.get('score', 0)}分 - {wp.get('description', '')}"
            for wp in weak_points[:10]
        ])

        return f"""## 学生画像
- 用户ID: {profile.user_id}
- 目标总分: {profile.target_score}
- 目标院校: {profile.target_school or '未指定'}
- 当前水平: {profile.current_level}
- 剩余天数: {profile.available_days} 天
- 每天可用: {profile.daily_hours} 小时
- 自评薄弱科目: {', '.join(profile.weak_subjects) or '无'}
- 自评强项科目: {', '.join(profile.strong_subjects) or '无'}

## 最新诊断结果
雷达图分数: {json.dumps(radar, ensure_ascii=False)}
薄弱环节 ({len(weak_points)} 个):
{weak_summary}

## 知识图谱结构
节点 (共 {len(nodes)} 个):
{node_summary}

跨科目关联边 (共 {len(edges)} 条):
{edge_summary}

请基于以上信息，生成一份动态调整的学习路径计划。"""

    def _to_plan(
        self,
        output: PathPlanOutput,
        profile: StudentProfile,
        diagnosis: dict,
    ) -> dict:
        """将 LLM 输出转换为 LearningPathPlan."""
        plan_id = f"path_{uuid.uuid4().hex[:8]}"

        def safe_json_load(s, default=None):
            if not s:
                return default or []
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return default or []

        raw_phases = safe_json_load(output.phases_json)
        phases = []
        for p in (raw_phases or []):
            phases.append(PathPhase(
                phase_id=p.get("phase_id", ""),
                phase_name=p.get("phase_name", ""),
                day_range=(p.get("start_day", 0), p.get("end_day", 0)),
                goal=p.get("goal", ""),
                key_topics=p.get("key_topics", []),
                strategy=p.get("strategy", ""),
            ))

        raw_tasks = safe_json_load(output.daily_tasks_json)
        tasks = []
        for t in (raw_tasks or []):
            tasks.append(DailyTask(
                day=t.get("day", 0),
                subject=t.get("subject", ""),
                focus_topic=t.get("focus_topic", ""),
                tasks=t.get("tasks", []),
                difficulty=t.get("difficulty", "medium"),
                estimated_minutes=t.get("estimated_minutes", 120),
                resources=t.get("resources", []),
            ))

        raw_priorities = safe_json_load(output.priorities_json)
        priorities = []
        for pr in (raw_priorities or []):
            priorities.append(KnowledgePriority(
                topic=pr.get("topic", ""),
                subject=pr.get("subject", ""),
                priority_score=pr.get("priority_score", 0),
                reason=pr.get("reason", ""),
                related_topics=pr.get("related_topics", []),
                estimated_days=pr.get("estimated_days", 1),
            ))

        chains = safe_json_load(output.association_chains_json)
        milestones = safe_json_load(output.milestones_json)

        plan = {
            "plan_id": plan_id,
            "student_profile": profile.model_dump(),
            "total_days": profile.available_days,
            "phases": [p.model_dump() for p in phases],
            "daily_tasks": [t.model_dump() for t in tasks],
            "knowledge_priorities": [pr.model_dump() for pr in priorities],
            "association_chains": chains or [],
            "generated_at": datetime.now().isoformat(),
            "version": 1,
            "adjustments": [],
            "summary": output.summary,
            "milestone_checkpoints": milestones or [],
        }

        self._plans[plan_id] = plan
        return plan

    @staticmethod
    def _generate_fallback_path(profile: StudentProfile, diagnosis: dict = None) -> dict:
        """兜底学习路径."""
        weak_subjects = list(diagnosis.get("radar_scores", {}).keys()) if diagnosis else []
        weak_subjects.sort(key=lambda s: diagnosis.get("radar_scores", {}).get(s, 100))

        phases = [
            {"phase_id": "p1", "phase_name": "基础补强期",
             "day_range": (1, min(30, profile.available_days // 3)),
             "goal": "补强最薄弱科目的基础概念和核心考点",
             "key_topics": weak_subjects[:2] if weak_subjects else ["数据结构", "操作系统"],
             "strategy": "以真题为导向，每学一个知识点立即配合练习"},
            {"phase_id": "p2", "phase_name": "重点突破期",
             "day_range": (min(31, profile.available_days // 3), min(60, profile.available_days * 2 // 3)),
             "goal": "攻克中高频难点和综合题型",
             "key_topics": weak_subjects[2:] if len(weak_subjects) > 2 else ["计组", "网络"],
             "strategy": "专题突破 + 跨科综合练习"},
            {"phase_id": "p3", "phase_name": "冲刺提升期",
             "day_range": (max(61, profile.available_days * 2 // 3), profile.available_days),
             "goal": "真题模拟 + 查漏补缺",
             "key_topics": [],
             "strategy": "限时模拟 + 错题回顾"},
        ]

        tasks = []
        for d in range(1, min(8, profile.available_days + 1)):
            subj = weak_subjects[d % len(weak_subjects)] if weak_subjects else "数据结构"
            tasks.append({
                "day": d, "subject": subj, "focus_topic": "",
                "tasks": [f"复习{subj}核心知识点", f"完成{subj}相关练习"],
                "difficulty": "medium", "estimated_minutes": int(profile.daily_hours * 60),
                "resources": [],
            })

        return {
            "plan_id": f"path_fallback_{uuid.uuid4().hex[:8]}",
            "student_profile": profile.model_dump(),
            "total_days": profile.available_days,
            "phases": phases,
            "daily_tasks": tasks,
            "knowledge_priorities": [],
            "association_chains": [
                ["内存管理", "页表与地址转换", "进程调度"],
                ["TCP拥塞控制", "滑动窗口", "流量控制"],
            ],
            "generated_at": datetime.now().isoformat(),
            "version": 1,
            "adjustments": [],
            "summary": "基于当前诊断结果的动态学习路径已生成。",
            "milestone_checkpoints": [f"Day {p['day_range'][1]}: 完成{p['phase_name']}" for p in phases],
            "is_fallback": True,
        }


# 全局单例
learning_path_planner = LearningPathPlannerAgent()
