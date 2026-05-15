"""Handwriting correction API - 手写批改.

基于 LangChain CorrectorAgent + 多模态 LLM.
"""

import logging
import os
import uuid
import tempfile

from fastapi import APIRouter, UploadFile, File

from app.schemas.correction import CorrectionAnalyzeResponse
from app.agents.corrector import corrector_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=CorrectionAnalyzeResponse)
async def analyze_handwriting(
    image: UploadFile = File(...),
    question_id: str | None = None,
):
    """上传草稿纸图片，分析手写步骤中的错误.

    LangChain CorrectorAgent 调用多模态 LLM 分析每一步的计算/推导过程，
    定位具体哪一步出错，返回错误标注和引导订正。
    """
    logger.info(f"Correction: 收到批改请求 - filename={image.filename}")

    # 保存临时文件
    ext = os.path.splitext(image.filename or "upload.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"turingmate_corr_{filename}")

    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 调用 Corrector Agent (LangChain)
        result = await corrector_agent.correct(
            image_url=file_path,
            question_info={"id": question_id} if question_id else None,
        )

        steps = result.get("steps", [])
        formatted_steps = [
            {
                "step_no": s.get("step_no", i + 1),
                "description": s.get("description", ""),
                "is_correct": s.get("is_correct", True),
                "score": s.get("score", 0),
                "feedback": s.get("feedback", ""),
            }
            for i, s in enumerate(steps)
        ]

        return CorrectionAnalyzeResponse(
            correction_id=f"corr_{uuid.uuid4().hex[:8]}",
            question_id=question_id or "",
            steps=formatted_steps,
            overall_feedback=result.get("summary", "") or result.get("suggestions", [""])[0],
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
