"""Correction API - 手写批改.

使用统一响应格式和依赖注入。
"""

import logging
from fastapi import APIRouter, Depends

from app.schemas.correction import CorrectionRequest
from app.api.deps import get_current_user_id, get_response_meta
from app.api.response import success, ResponseMeta
from app.services.correction_service import correction_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze")
async def analyze_correction(
    body: CorrectionRequest,
    user_id: str = Depends(get_current_user_id),
    meta: ResponseMeta = Depends(get_response_meta),
):
    """分析手写草稿.

    批改学生的手写解题过程，给出反馈和建议。
    """
    logger.info(f"Correction: 分析手写草稿 - user={user_id}, question={body.question_id}")

    result = await correction_service.analyze(
        image_url=body.image_url,
        question_id=body.question_id,
    )

    return success(
        data=result,
        message="批改分析完成",
        meta=meta,
    )