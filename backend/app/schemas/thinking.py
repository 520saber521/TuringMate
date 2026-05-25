"""Thinking Trace Schemas — 思维过程可视化数据模型.

定义思维回放所需的数据结构:
  - ThinkingStep: 单步思考记录
  - ThinkingPath: 完整思考路径
  - ThinkingReport: 思维成长报告
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class StepType(str, Enum):
    """思考步骤类型."""
    INPUT = "input"           # 用户输入
    QUESTION = "question"     # AI提问引导
    ANSWER = "answer"        # 学生回答
    HINT = "hint"            # 提示
    MISDIRECTION = "misdirection"   # 偏离正确方向
    CORRECTION = "correction"      # 被纠正回来
    INSIGHT = "insight"       # 关键顿悟时刻
    PRACTICE = "practice"     # 变式练习
    SUMMARY = "summary"       # 阶段总结


class DeviationLevel(str, Enum):
    """偏离程度."""
    NONE = "none"             # 正常方向
    SLIGHT = "slight"         # 轻微偏离
    MODERATE = "moderate"     # 明显偏离
    SEVERE = "severe"         # 严重误区


class ThinkingStep(BaseModel):
    """单步思考记录."""
    step_id: str = Field(description="步骤唯一ID")
    session_id: str = Field(description="会话ID")
    step_type: StepType = Field(description="步骤类型")
    timestamp: str = Field(default="", description="时间戳")

    # 内容
    content: str = Field(description="内容文本")
    role: str = Field(description="角色: user / assistant / system")
    metadata: dict = Field(default_factory=dict, description="元数据")

    # 偏离分析（自动标注）
    deviation_level: DeviationLevel = Field(default=DeviationLevel.NONE, description="偏离程度")
    deviation_reason: str = Field(default="", description="偏离原因分析")
    correction_applied: bool = Field(default=False, description="是否被纠正")

    # 知识点追踪
    related_topic: str = Field(default="", description="关联知识点")
    mastery_signal: Optional[str] = Field(
        default=None,
        description="掌握信号: strong(掌握好) / weak(需加强) / confused(混淆) / new(新接触)"
    )


class ThinkingPath(BaseModel):
    """完整思考路径 — 一道题的思维轨迹图."""
    path_id: str = Field(description="路径ID")
    question_id: str = Field(description="题目ID")
    session_id: str = Field(description="会话ID")
    user_id: str = Field(description="学生ID")

    steps: list[ThinkingStep] = Field(default_factory=list, description="步骤序列")

    # 汇总统计
    total_steps: int = Field(default=0, description="总步数")
    deviation_count: int = Field(default=0, description="偏离次数")
    correction_count: int = Field(default=0, description="被纠正次数")
    insight_moments: int = Field(default=0, description="顿悟时刻数")

    # 最终结论
    final_status: str = Field(default="", description="最终状态: mastered / in_progress / stuck")
    conclusion: str = Field(default="", description="最终总结")
    time_spent_seconds: int = Field(default=0, description="总耗时秒数")


class ThinkingWeaknessTag(str, Enum):
    """思维漏洞标签（可量化追踪）."""
    CONCEPT_CONFUSION = "概念混淆"          # 混淆了相似概念
    LOGIC_GAP = "逻辑跳跃"                  # 推理跳跃，缺中间步骤
    RIGOROUS_LACK = "论证不严谨"            # 论述不够严谨
    OVERLOOK_EDGE_CASE = "忽略边界情况"     # 忽略边界条件
    WRONG_METHOD_CHOICE = "方法选择错误"     # 选错解题方法
    CALCULATION_ERROR = "计算失误"           # 计算出错
    READING_MISTAKE = "审题不清"            # 没读懂题
    MEMORY_FAILURE = "记忆遗忘"              # 公式/定理记不住


class WeeklyThinkingStats(BaseModel):
    """每周思维统计."""
    week_label: str = Field(description="周标签, 如 '2026-W20'")
    total_sessions: int = Field(default=0, description="本周对话次数")
    total_questions: int = Field(default=0, description="本题数量")
    weakness_frequency: dict[str, int] = Field(
        default_factory=dict,
        description="各漏洞出现频率 {漏洞名: 次数}"
    )
    improvement_areas: list[str] = Field(
        default_factory=list,
        description="明显进步的领域"
    )
    persistent_weaknesses: list[str] = Field(
        default_factory=list,
        description="顽固漏洞（连续多周未改善）"
    )
    avg_deviation_rate: float = Field(default=0.0, description="平均偏离率")
    avg_correction_time: float = Field(default=0.0, description="平均纠偏用时(分钟)")


class ThinkingGrowthReport(BaseModel):
    """思维成长报告 — 定期生成（周/月）."""
    report_id: str = Field(description="报告ID")
    user_id: str = Field(description="学生ID")
    period: str = Field(description="周期: weekly_YYYY_WXX / monthly_YYYY_MM")
    generated_at: str = Field(default="", description="生成时间")

    # 时间线数据
    weekly_stats: list[WeeklyThinkingStats] = Field(
        default_factory=list,
        description="逐周统计数据"
    )

    # 漏洞雷达
    current_weakness_radar: dict[str, float] = Field(
        default_factory=dict,
        description="当前漏洞严重度雷达 {漏洞名: 0-100分值}"
    )

    # 成长指标
    overall_trend: str = Field(default="", description="总体趋势: improving / stable / declining")
    top_improvements: list[str] = Field(default_factory=list, description="最大进步项")
    top_concerns: list[str] = Field(default_factory=list, description="最需关注项")

    # 建议
    recommendations: list[str] = Field(default_factory=list, description="针对性建议")
    encouragement: str = Field(default="", description="鼓励语")
