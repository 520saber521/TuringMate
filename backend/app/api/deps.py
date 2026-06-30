"""统一依赖注入模块.

提供所有API端点所需的公共依赖:
1. 数据库会话
2. 用户认证
3. 配置访问
4. 服务实例注入

使用 FastAPI Depends 进行依赖注入。
"""

import uuid
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import get_settings, Settings
from app.db.session import get_db
from app.core.security import decode_token
from app.crud.user import user_crud
from app.api.response import ResponseMeta


# ============================================================
# 配置依赖
# ============================================================


def get_app_settings() -> Settings:
    """获取应用配置."""
    return get_settings()


# ============================================================
# 数据库依赖
# ============================================================


def get_db_session() -> Session:
    """获取数据库会话 (同步).

    FastAPI 依赖注入用法:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db_session)):
            ...
    """
    return get_db()


# ============================================================
# 认证依赖
# ============================================================


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """获取当前认证用户 (完整验证).

    从 JWT Bearer Token 解析用户信息，并验证用户存在。

    Returns:
        用户信息字典 {"id": ..., "email": ..., ...}

    Raises:
        HTTPException: 401 未认证或令牌无效
    """
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

    return {"id": user.id, "email": user.email, "username": user.username}


async def get_current_user_id(
    authorization: Optional[str] = Header(default=None),
) -> str:
    """获取当前用户ID (轻量级，无数据库查询).

    仅从 JWT 解析 user_id，适用于无需用户完整信息的场景。

    Returns:
        用户ID字符串

    Raises:
        HTTPException: 401 未认证或令牌无效
    """
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


async def get_optional_user_id(
    authorization: Optional[str] = Header(default=None),
) -> Optional[str]:
    """可选用户ID (允许匿名访问).

    尝试从 JWT 解析 user_id，失败时返回 None。
    适用于支持匿名访问的端点。

    Returns:
        用户ID字符串或 None
    """
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    try:
        payload = decode_token(token)
        return payload.get("sub")
    except Exception:
        return None


# ============================================================
# 请求追踪
# ============================================================


def get_request_id(request: Request) -> str:
    """获取请求追踪ID.

    优先使用客户端提供的 X-Request-Id，
    否则自动生成。

    Returns:
        请求追踪ID字符串
    """
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        request_id = str(uuid.uuid4())
    return request_id


def get_response_meta(
    request_id: str = Depends(get_request_id),
) -> ResponseMeta:
    """获取响应元数据.

    用于构建统一响应格式。

    Returns:
        ResponseMeta 实例
    """
    return ResponseMeta(request_id=request_id)


# ============================================================
# 服务依赖工厂
# ============================================================


def get_service(service_class):
    """服务实例依赖工厂.

    创建服务实例的依赖函数。

    Args:
        service_class: 服务类

    Returns:
        依赖函数

    用法:
        from app.services.chat_service import ChatService

        @router.post("/chat")
        async def chat(
            service: ChatService = Depends(get_service(ChatService)),
        ):
            ...
    """
    def dependency():
        return service_class()
    return dependency