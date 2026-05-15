"""Chat schemas."""
from pydantic import BaseModel
from typing import Literal, Optional


class ChatStartRequest(BaseModel):
    """开始引导对话请求."""
    question_id: str
    user_id: Optional[str] = "user_001"


class ChatStartResponse(BaseModel):
    """引导对话启动响应."""
    session_id: str
    first_message: str
    stage: Literal["QUESTION", "HINT", "PROBE", "AFFIRM", "EXTEND", "COMPLETE"]


class ChatMessageRequest(BaseModel):
    """对话消息请求."""
    session_id: str
    message: str


class ChatMessageResponse(BaseModel):
    """对话消息响应."""
    session_id: str
    content: str
    stage: str
    hint_available: bool = False
    skip_available: bool = True
