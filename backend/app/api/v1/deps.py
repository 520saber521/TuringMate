"""Common dependencies for API routes."""
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.core.security import decode_token
from app.crud.user import user_crud


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    """Get current authenticated user from JWT Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="认证格式错误，请使用 Bearer Token")

    try:
        payload = decode_token(token)
        if payload.get("type") == "refresh":
            raise HTTPException(status_code=401, detail="请使用访问令牌，而非刷新令牌")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="令牌无效")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")

    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


async def get_current_user_id(
    authorization: Optional[str] = Header(default=None),
) -> str:
    """Extract user_id from JWT without DB lookup. Lightweight."""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="认证格式错误")

    try:
        payload = decode_token(token)
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")
