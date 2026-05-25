"""Thinking Tracer Agent — 思维过程可视化回放系统.

在苏格拉底对话中自动记录学生每一步思考，
完成题目后生成「思考路径图」，
定期生成「思维成长报告」。

核心价值：
  - 把"粗心""不会"变成可量化、可追踪的数据
  - 展示从哪个节点偏离、如何被引导回来
  - 追踪思维漏洞的改善趋势
"""

import json
import logging
import uuid
import re
from datetime import datetime
from collections import Counter, defaultdict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.schemas.thinking import (
    ThinkingStep, ThinkingPath, ThinkingGrowthReport,
    StepType, DeviationLevel, ThinkingWeaknessTag,
    WeeklyThinkingStats,
)

logger = logging.getLogger(__name__)

# ── 偏离检测关键词规则 ────────────────────────────────────

DEVIATION_PATTERNS = {
    DeviationLevel.SLIGHT: [
        r"我觉得?是", r"可能是", r"大概", r"好像",
        r"不确定", r"不太确定", r"也许",
    ],
    DeviationLevel.MODERATE: [
        r"不对", r"等下", r"等等", r"我搞错了",
        r"不是这样", r"搞混了", r"混淆",
        r"忘了", r"记不清", r"想不起来了",
    ],
    DeviationLevel.SEVERE: [
        r"完全不会", r"没思路", r"不知道",
        r"太难了", r"放弃", r"不想做了",
        r"完全不懂", r"这什么啊",
    ],
}

# ── 思维漏洞标签映射 ──────────────────────────────────────

WEAKNESS_KEYWORDS = {
    ThinkingWeaknessTag.CONCEPT_CONFUSION: [
        r"混淆", r"搞混了", r"分不清", r"以为.*其实是",
    ],
    ThinkingWeaknessTag.LOGIC_GAP: [
        r"跳过", r"跳步", r"中间.*省略", r"直接.*得出",
    ],
    ThinkingWeaknessTag.RIGOROUS_LACK: [
        r"差不多", r"应该行", r"大概对", r"差不多吧",
    ],
    ThinkingWeaknessTag.OVERLOOK_EDGE_CASE: [
        r"边界", r"特殊情况", r"没考虑到", r"遗漏",
    ],
    ThinkingWeaknessTag.WRONG_METHOD_CHOICE: [
        r"用错", r"方法不对", r"不该用", r"应该用.*而不是",
    ],
    ThinkingWeaknessTag.CALCULATION_ERROR: [
        r"算错了", r"算术", r"计算错误", r"数值不对",
    ],
    ThinkingWeaknessTag.READING_MISTAKE: [
        r"看错了", r"没看清", r"题目说", r"原来是这样",
    ],
    ThinkingWeaknessTag.MEMORY_FAILURE: [
        r"公式", r"定理", r"定义", r"记不", r"忘了",
    ],
}


class ThinkingTracer:
    """思维轨迹追踪器.

    集成到 SocraticTutor 的每次对话中，自动记录和分析思维过程。
    
    使用方式:
      tracer = ThinkingTracer(session_id, question_id)
      tracer.record_step(content, role="user")
      path = tracer.build_path()       # 构建完整路径
      report = tracer.generate_report() # 生成成长报告
    """

    def __init__(self, session_id: str, question_id: str = "", user_id: str = ""):
        self.path_id = f"tp_{uuid.uuid4().hex[:12]}"
        self.session_id = session_id
        self.question_id = question_id
        self.user_id = user_id
        self._steps: list[ThinkingStep] = []
        self._start_time = datetime.now()

    def record_step(
        self,
        content: str,
        role: str = "user",
        step_type: StepType = StepType.INPUT,
        metadata: dict | None = None,
        related_topic: str = "",
    ) -> ThinkingStep:
        """记录一步思考.

        自动分析:
          - 偏离程度 (DeviationLevel)
          - 触发的思维漏洞标签
          - 是否需要纠正
        """
        step = ThinkingStep(
            step_id=f"s_{len(self._steps):03d}",
            session_id=self.session_id,
            step_type=step_type,
            timestamp=datetime.now().isoformat(),
            content=content[:2000],  # 截断超长内容
            role=role,
            metadata=metadata or {},
            deviation_level=self._detect_deviation(content),
            deviation_reason=self._explain_deviation(content),
            correction_applied=False,
            related_topic=related_topic,
            mastery_signal=self._detect_mastery_signal(content, role),
        )
        self._steps.append(step)
        return step

    def mark_correction(self, step_index: int) -> None:
        """标记某步骤已被纠正."""
        if 0 <= step_index < len(self._steps):
            self._steps[step_index].correction_applied = True

    def build_path(self) -> dict:
        """构建完整的思考路径图 (ThinkingPath)."""
        total_time = (datetime.now() - self._start_time).total_seconds()
        deviations = [s for s in self._steps if s.deviation_level != DeviationLevel.NONE]
        corrections = [s for s in self._steps if s.correction_applied]
        insights = [s for s in self._steps if s.step_type == StepType.INSIGHT]

        # 判断最终状态
        last_steps = self._steps[-5:] if len(self._steps) >= 5 else self._steps
        final_status = "mastered"
        for s in reversed(last_steps):
            if s.role == "user":
                if any(kw in s.content for kw in ["不会", "不懂", "太难"]):
                    final_status = "stuck"
                    break
                elif s.deviation_level in (DeviationLevel.MODERATE, DeviationLevel.SEVERE):
                    final_status = "in_progress"
                    break

        conclusion = self._generate_conclusion()

        return ThinkingPath(
            path_id=self.path_id,
            question_id=self.question_id,
            session_id=self.session_id,
            user_id=self.user_id,
            steps=[s.model_dump() for s in self._steps],
            total_steps=len(self._steps),
            deviation_count=len(deviations),
            correction_count=len(corrections),
            insight_moments=len(insights),
            final_status=final_status,
            conclusion=conclusion,
            time_spent_seconds=int(total_time),
        ).model_dump()

    def generate_weekly_report(
        self,
        historical_paths: list[dict] | None = None,
    ) -> dict:
        """生成周/月思维成长报告.
        
        Args:
            historical_paths: 历史思考路径列表 (来自数据库或缓存)

        Returns:
            ThinkingGrowthReport 字典
        """
        paths = (historical_paths or []) + [self.build_path()]

        # 按周期统计漏洞频率
        weakness_counter = Counter()
        weekly_stats_map: dict[str, dict] = defaultdict(lambda: {
            "sessions": 0, "questions": 0, "weaknesses": {},
            "deviations": 0, "correction_times": [],
        })

        for path in paths:
            # 统计漏洞频率（单次遍历，避免双重计数）
            weakness_counter_local = Counter()
            for step in path.get("steps", []):
                tags = self._tag_weakness(step.get("content", ""))
                for tag in tags:
                    name = tag.value if hasattr(tag, 'value') else str(tag)
                    weakness_counter_local[name] += 1
                    weakness_counter[name] += 1

            week_key = path.get("session_id", "")[:10]
            stats = weekly_stats_map[week_key]
            stats["sessions"] += 1
            stats["questions"] += 1
            stats["deviations"] += path.get("deviation_count", 0)
            stats["correction_times"].append(path.get("time_spent_seconds", 0))

            for name, count in weakness_counter_local.items():
                stats["weaknesses"][name] = stats["weaknesses"].get(name, 0) + count

        # 构建 weekly stats
        weekly_stats_list = []
        for week_label, data in sorted(weekly_stats_map.items()):
            avg_corr = sum(data["correction_times"]) / max(len(data["correction_times"]), 1)
            top_weaknesses = sorted(data["weaknesses"].items(), key=lambda x: -x[1])[:5]

            weekly_stats_list.append(WeeklyThinkingStats(
                week_label=week_label,
                total_sessions=data["sessions"],
                total_questions=data["questions"],
                weakness_frequency=dict(top_weaknesses),
                improvement_areas=[],  # 需要历史对比才能判断
                persistent_weaknesses=[k for k, v in top_weaknesses if v >= 2],
                avg_deviation_rate=data["deviations"] / max(data["sessions"], 1),
                avg_correction_time=avg_corr / 60,  # 转 分钟
            ).model_dump())

        # 雷达图数据
        radar = {}
        for tag in ThinkingWeaknessTag:
            count = weakness_counter.get(tag.value, 0)
            radar[tag.value] = min(100, count * 15)  # 归一化到 0-100

        top_issues = [item[0] for item in weakness_counter.most_common(3)]
        report_id = f"tr_{uuid.uuid4().hex[:8]}"

        return ThinkingGrowthReport(
            report_id=report_id,
            user_id=self.user_id,
            period=f"week_{datetime.now().strftime('%Y_W%W')}",
            generated_at=datetime.now().isoformat(),
            weekly_stats=weekly_stats_list,
            current_weakness_radar=radar,
            overall_trend="improving" if len(paths) > 1 else "stable",
            top_improvements=["持续追踪后将展示改善趋势"] if len(paths) <= 1 else [],
            top_concerns=top_issues if top_issues else [],
            recommendations=self._generate_recommendations(radar),
            encouragement="每一次思考都是进步！继续加油！",
        ).model_dump()

    # ── 内部分析方法 ───────────────────────────────────────

    def _detect_deviation(self, content: str) -> DeviationLevel:
        """通过关键词模式检测偏离程度."""
        for level, patterns in DEVIATION_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, content, re.IGNORECASE):
                    return level
        return DeviationLevel.NONE

    def _explain_deviation(self, content: str) -> str:
        """解释偏离原因."""
        level = self._detect_deviation(content)
        reasons = {
            DeviationLevel.SLIGHT: "回答不够确定，可能存在轻微疑惑",
            DeviationLevel.MODERATE: "出现明显错误认知或记忆模糊",
            DeviationLevel.SEVERE: "遇到重大困难或情绪障碍",
        }
        return reasons.get(level, "")

    def _detect_mastery_signal(self, content: str, role: str) -> str | None:
        """检测掌握信号."""
        if role != "user":
            return None
        confident_words = ["明白了", "懂了", "对的", "没错", "清楚了"]
        confused_words = ["不会", "不懂", "不清楚", "为什么", "怎么"]

        if any(w in content for w in confident_words):
            return "strong"
        if any(w in content for w in confused_words):
            return "confused"
        return None

    def _tag_weakness(self, content: str) -> list[ThinkingWeaknessTag]:
        """给内容打思维漏洞标签."""
        tags = []
        for tag, patterns in WEAKNESS_KEYWORDS.items():
            for pat in patterns:
                if re.search(pat, content, re.IGNORECASE):
                    tags.append(tag)
                    break
        return tags

    def _generate_conclusion(self) -> str:
        """生成路径结论摘要."""
        if not self._steps:
            return "暂无足够数据进行分析。"

        deviations = [s for s in self._steps if s.deviation_level != DeviationLevel.NONE]
        corrections = [s for s in self._steps if s.correction_applied]

        if not deviations:
            return "本次思考过程顺畅，没有明显偏离。继续保持！"

        if len(corrections) >= len(deviations):
            return f"共经历 {len(deviations)} 次偏离，但全部被成功纠正回来。纠偏能力良好！"

        severe_count = sum(1 for s in deviations if s.deviation_level == DeviationLevel.SEVERE)
        if severe_count > 0:
            return f"存在 {severe_count} 处严重困惑，建议针对这些知识点重点复习。"

        return f"有 {len(deviations)} 处轻微偏离，其中 {len(corrections)} 处已自行修正。整体表现稳定。"

    @staticmethod
    def _generate_recommendations(radar: dict) -> list[str]:
        """根据雷达图生成建议."""
        recs = []
        top_items = sorted(radar.items(), key=lambda x: -x[1])[:3]
        for name, score in top_items:
            if score > 50:
                recs.append(f"重点关注「{name}」，出现频率较高")
            elif score > 20:
                recs.append(f"适当加强「{name}」方面的训练")

        if not recs:
            recs.append("保持当前学习节奏，各项思维能力均衡发展")
        return recs


# 全局工厂函数
def create_tracer(session_id: str, question_id: str = "", user_id: str = "") -> ThinkingTracer:
    """创建思维追踪器实例."""
    return ThinkingTracer(session_id, question_id, user_id)
