"""Problem Generation Schemas — 「举一反三」题目生成器数据模型.

支持基于模板的参数化题目生成:
  - ProblemTemplate: 题目模板
  - GeneratedProblem: 生成的变式题
  - MasteryValidation: 掌握验证结果
"""

from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ProblemTemplate(BaseModel):
    """参数化题目模板.
    
    模板中的占位符用 {{param}} 格式标记，
    生成时替换为具体值。约束规则防止无解/错误题目。
    """
    template_id: str = Field(description="模板ID")
    subject: str = Field(description="科目")
    topic: str = Field(description="知识点")
    original_question: str = Field(description="原始题目（作为参考）")

    # 模板内容
    template_text: str = Field(description="题目模板文本，含 {{param}} 占位符")
    parameters: dict = Field(
        default_factory=dict,
        description='''参数定义 {
        "n": {"type": "int", "range": [5, 20], "description": "数组长度"},
        "k": {"type": "int", "range": [2, 10], "description": "第K大"}
    }'''
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="约束条件，如 'n必须是素数' 或 'k < n'"
    )
    solution_template: str = Field(default="", description="解答模板（用于验证）")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)


class GeneratedProblem(BaseModel):
    """生成的变式题."""
    problem_id: str = Field(description="题目ID")
    source_template_id: str = Field(description="来源模板ID")
    content: str = Field(description="生成的完整题目文本")
    parameter_values: dict = Field(default_factory=dict, description="实际参数值")
    expected_answer: str = Field(default="", description="预期答案要点")
    hint: str = Field(default="", description="提示（可选显示）")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    topic: str = Field(default="")
    subject: str = Field(default="")


class MasteryValidation(BaseModel):
    """掌握验证结果（做完三道变式题后的判定）."""
    validation_id: str = Field(description="验证ID")
    topic: str = Field(description="验证的知识点")
    problems_attempted: int = Field(default=0, description="尝试题数")
    problems_passed: int = Field(default=0, description="通过题数")
    is_mastered: bool = Field(default=False, description="是否已掌握")
    confidence_score: float = Field(default=0.0, description="置信度 0-1")
    feedback: str = Field(default="", description="综合反馈")
    next_recommendation: str = Field(default="", description="下一步建议")
