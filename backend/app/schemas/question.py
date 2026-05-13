"""Question schemas."""
from pydantic import BaseModel
from typing import Optional


class QuestionParseResponse(BaseModel):
    """题目识别结果."""
    question_id: str
    subject: str  # 数据结构/计组/OS/网络
    knowledge_tags: list[str]
    difficulty: int  # 1-5
    content: str
    image_url: Optional[str] = None
