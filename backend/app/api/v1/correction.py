"""Handwriting correction API - 手写批改."""

import logging

from fastapi import APIRouter, UploadFile, File

from app.schemas.correction import CorrectionAnalyzeResponse
from app.agents.corrector import corrector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=CorrectionAnalyzeResponse)
async def analyze_handwriting(
    image: UploadFile = File(...),
    question_id: str | None = None,
):
    """上传草稿纸图片，分析手写步骤中的错误.

    Corrector Agent 识别每一步的计算/推导过程，
    定位具体哪一步出错，返回错误标注和引导订正。
    """
    logger.info(f"Correction: 收到批改请求 - filename={image.filename}")

    # 保存临时文件
    import os, uuid, tempfile

    ext = os.path.splitext(image.filename or "upload.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"turingmate_corr_{filename}")

    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 调用 Corrector Agent
        result = await corrector.analyze(file_path, question_id)

        return CorrectionAnalyzeResponse(
            correction_id=result["correction_id"],
            question_id=result["question_id"],
            steps=result["steps"],
            overall_feedback=result["overall_feedback"],
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
