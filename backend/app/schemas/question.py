"""Question schemas."""
from pydantic import BaseModel, Field
from typing import Optional


# ── 题目识别 ──
class QuestionParseResponse(BaseModel):
    question_id: str
    subject: str
    knowledge_tags: list[str]
    difficulty: int
    content: str
    image_url: Optional[str] = None


# ── 题目列表项 ──
class QuestionItem(BaseModel):
    id: str
    subject: str
    knowledge_tags: list[str] = []
    difficulty: int = 3
    content: str
    year: Optional[int] = None
    exam_paper: str = ""
    source_type: str = "manual"

    class Config:
        from_attributes = True


# ── 题目详情 ──
class QuestionDetail(BaseModel):
    id: str
    subject: str
    knowledge_tags: list[str] = []
    difficulty: int = 3
    content: str
    image_url: str = ""
    solution_steps: list[dict] = []
    year: Optional[int] = None
    exam_paper: str = ""
    source_type: str = "manual"
    ai_analysis: Optional[str] = None

    class Config:
        from_attributes = True


# ── 题目筛选参数 ──
class QuestionFilter(BaseModel):
    subject: Optional[str] = None
    tag: Optional[str] = None
    difficulty: Optional[int] = None
    year: Optional[int] = None
    keyword: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ── 分页响应 ──
class QuestionListResponse(BaseModel):
    items: list[QuestionItem]
    total: int
    page: int
    page_size: int
