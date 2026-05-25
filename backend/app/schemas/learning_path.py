"""Learning Path Schemas — 动态学习路径规划器数据模型.

Pydantic 模型定义：
  - StudentProfile: 学生画像（目标/水平/时间）
  - LearningPathPlan: 动态学习路径计划
  - PathNode / PathPhase / DailyTask: 路径节点结构
  - PathAdjustmentRequest: 动态调整请求
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class StudentProfile(BaseModel):
    """学生画像 — 路径规划输入."""
    user_id: str = Field(description="学生ID")
    target_score: int = Field(description="目标总分", ge=0, le=500)
    target_school: str = Field(default="", description="目标院校")
    current_level: str = Field(
        default="intermediate",
        description="当前水平: beginner(刚起步) / intermediate(有基础) / advanced(冲刺)"
    )
    available_days: int = Field(default=90, description="距考试剩余天数", ge=1, le=365)
    daily_hours: float = Field(default=4.0, description="每天可用学习小时数", ge=0.5, le=16)
    weak_subjects: list[str] = Field(default_factory=list, description="自评薄弱科目")
    strong_subjects: list[str] = Field(default_factory=list, description="自评强项科目")


class KnowledgePriority(BaseModel):
    """知识点优先级评估."""
    topic: str = Field(description="知识点名称")
    subject: str = Field(description="所属科目")
    priority_score: float = Field(description="优先级分数 0-100", ge=0, le=100)
    reason: str = Field(default="", description="优先级原因")
    related_topics: list[str] = Field(default_factory=list, description="关联知识点")
    estimated_days: int = Field(default=1, description="建议投入天数")


class DailyTask(BaseModel):
    """每日学习任务."""
    day: int = Field(description="第几天")
    date_hint: str = Field(default="", description="日期提示，如 'Day 15'")
    subject: str = Field(description="主要科目")
    focus_topic: str = Field(description="重点知识点")
    tasks: list[str] = Field(description="具体任务列表")
    difficulty: str = Field(default="medium", description="难度: easy / medium / hard")
    estimated_minutes: int = Field(default=120, description="预估时长(分钟)")
    resources: list[str] = Field(default_factory=list, description="推荐资源/题号")


class PathPhase(BaseModel):
    """学习阶段（如：基础补强 / 重点突破 / 综合提升）."""
    phase_id: str = Field(description="阶段标识")
    phase_name: str = Field(description="阶段名称")
    day_range: tuple[int, int] = Field(description="起止天数 (start, end)")
    goal: str = Field(description="本阶段目标")
    key_topics: list[str] = Field(description="本阶段核心知识点")
    strategy: str = Field(default="", description="教学策略描述")


class PathAdjustment(BaseModel):
    """路径调整记录."""
    adjustment_id: str = Field(description="调整ID")
    trigger: str = Field(description="调整触发原因")
    original_plan: str = Field(description="原计划摘要")
    adjusted_plan: str = Field(description="调整后计划")
    affected_days: list[int] = Field(default_factory=list, description="受影响的天数")
    reason: str = Field(default="", description="调整原因说明")
    timestamp: str = Field(default="", description="调整时间")


class LearningPathPlan(BaseModel):
    """完整动态学习路径计划.

    核心差异化特性:
      - 不是固定章节排列，而是基于薄弱点动态排序
      - 知识点关联感知（如：内存管理 → 自动关联进程调度）
      - 支持动态调整（诊断结果变化时重新优化）
    """
    plan_id: str = Field(description="计划ID")
    student_profile: StudentProfile = Field(description="学生画像")

    # 顶层规划
    total_days: int = Field(description="总规划天数")
    phases: list[PathPhase] = Field(default_factory=list, description="学习阶段列表")
    daily_tasks: list[DailyTask] = Field(default_factory=list, description="每日任务详情")

    # 知识点优先级矩阵（动态计算）
    knowledge_priorities: list[KnowledgePriority] = Field(
        default_factory=list,
        description="知识点优先级排序（基于诊断+知识图谱+目标）"
    )

    # 关联链路（差异化核心）
    association_chains: list[list[str]] = Field(
        default_factory=list,
        description="""知识点关联链路。
        例: ["内存管理", "页表与地址转换", "进程调度"]
        表示学完A后自动推荐B和C（因为存在内在关联）"""
    )

    # 元信息
    generated_at: str = Field(default="", description="生成时间")
    version: int = Field(default=1, description="版本号")
    adjustments: list[PathAdjustment] = Field(default_factory=list, description="历史调整记录")

    # 总结
    summary: str = Field(default="", description="路线总结（200字左右）")
    milestone_checkpoints: list[str] = Field(
        default_factory=list,
        description="关键里程碑节点"
    )


class PathAdjustmentRequest(BaseModel):
    """路径动态调整请求."""
    plan_id: str = Field(description="原计划ID")
    trigger_type: str = Field(
        description="触发类型: diagnosis_update(新诊断)/performance_change(表现变化)/time_constraint(时间变动)/manual(手动)"
    )
    new_diagnosis: Optional[dict] = Field(default=None, description="最新诊断结果（如果有的话）")
    feedback: str = Field(default="", description="用户反馈/备注")
