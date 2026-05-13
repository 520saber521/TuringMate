"""Common dependencies for API routes."""

from fastapi import Depends, Header
from typing import Optional


async def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """Get current user from authorization header. MVP: return mock user."""
    # TODO: Implement JWT authentication
    return {"id": "user_001", "name": "考研同学", "avatar": ""}


# Session dependency for chat state management
async def get_chat_session(session_id: str) -> dict:
    """Get or create a chat session."""
    # TODO: Implement session retrieval from Redis/DB
    return {"session_id": session_id, "status": "active"}
