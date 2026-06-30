"""统一API响应模型.

所有API端点应使用此模块的响应模型，确保:
1. 响应格式一致性
2. 错误处理标准化
3. 元数据支持 (分页、请求追踪等)
"""

from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """响应元数据."""

    request_id: Optional[str] = Field(None, description="请求追踪ID")
    page: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页数量")
    total: Optional[int] = Field(None, description="总数量")
    has_more: Optional[bool] = Field(None, description="是否有更多数据")


class APIResponse(BaseModel, Generic[T]):
    """统一API响应模型.

    所有成功响应应使用此格式:
    {
        "success": true,
        "data": ...,
        "message": "操作成功",
        "meta": {...}
    }
    """

    success: bool = Field(True, description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: str = Field("操作成功", description="响应消息")
    meta: Optional[ResponseMeta] = Field(None, description="元数据")

    class Config:
        from_attributes = True


class APIErrorResponse(BaseModel):
    """统一错误响应模型.

    所有错误响应应使用此格式:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "错误详情",
            "details": {...}
        },
        "meta": {...}
    }
    """

    success: bool = Field(False, description="请求是否成功")
    error: dict = Field(
        ...,
        description="错误信息，包含 code, message, details",
    )
    meta: Optional[ResponseMeta] = Field(None, description="元数据")


class PaginatedData(BaseModel, Generic[T]):
    """分页数据容器."""

    items: list[T] = Field(default_factory=list, description="数据列表")
    page: int = Field(1, ge=1, description="当前页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    total: int = Field(0, ge=0, description="总数量")
    has_more: bool = Field(False, description="是否有更多数据")


# ============================================================
# 响应构建器
# ============================================================


def success(
    data: Any = None,
    message: str = "操作成功",
    meta: Optional[ResponseMeta] = None,
) -> dict:
    """构建成功响应.

    Args:
        data: 响应数据
        message: 成功消息
        meta: 元数据

    Returns:
        标准化的成功响应字典
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "meta": meta.model_dump(exclude_none=True) if meta else None,
    }


def error(
    code: str,
    message: str,
    details: Optional[dict] = None,
    meta: Optional[ResponseMeta] = None,
) -> dict:
    """构建错误响应.

    Args:
        code: 错误代码 (如 VALIDATION_ERROR, NOT_FOUND, INTERNAL_ERROR)
        message: 错误消息
        details: 额外错误详情
        meta: 元数据

    Returns:
        标准化的错误响应字典
    """
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "meta": meta.model_dump(exclude_none=True) if meta else None,
    }


def paginated(
    items: list,
    page: int = 1,
    page_size: int = 20,
    total: int = 0,
    has_more: bool = False,
    message: str = "获取成功",
) -> dict:
    """构建分页响应.

    Args:
        items: 数据列表
        page: 当前页码
        page_size: 每页数量
        total: 总数量
        has_more: 是否有更多数据
        message: 成功消息

    Returns:
        标准化的分页响应字典
    """
    return success(
        data=items,
        message=message,
        meta=ResponseMeta(
            page=page,
            page_size=page_size,
            total=total,
            has_more=has_more,
        ),
    )