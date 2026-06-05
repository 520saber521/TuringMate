"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.user import user_crud
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserInfo,
)

router = APIRouter()


def _get_current_user_id(authorization: str | None = None) -> str:
    """Extract user_id from JWT token. Used as FastAPI dependency."""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="认证格式错误")
    try:
        payload = decode_token(token)
        if payload.get("type") == "refresh":
            raise HTTPException(status_code=401, detail="请使用访问令牌")
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的令牌")


def _user_to_dict(user) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "avatar": user.avatar,
        "email": user.email or "",
        "target_school": user.target_school,
        "weak_subjects": user.weak_subjects or [],
    }


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if user_crud.get_by_username(db, req.username):
        raise HTTPException(status_code=409, detail="用户名已存在")
    if req.email and user_crud.get_by_email(db, req.email):
        raise HTTPException(status_code=409, detail="邮箱已被注册")

    user = user_crud.create(db, req.username, req.password, req.name, req.email)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=_user_to_dict(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.authenticate(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=_user_to_dict(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
        user_id = payload.get("sub")
        user = user_crud.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            user=_user_to_dict(user),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的刷新令牌")


@router.get("/me", response_model=UserInfo)
def get_me(db: Session = Depends(get_db), user_id: str = Depends(_get_current_user_id)):
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserInfo(**_user_to_dict(user))
