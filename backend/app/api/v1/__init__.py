"""API Router - V1 endpoints."""
from fastapi import APIRouter

from app.api.v1 import question, chat, correction, diagnosis, visualization, upload

router = APIRouter()

router.include_router(question.router, prefix="/question", tags=["题目识别"])
router.include_router(chat.router, prefix="/chat", tags=["引导对话"])
router.include_router(correction.router, prefix="/correction", tags=["手写批改"])
router.include_router(diagnosis.router, prefix="/diagnosis", tags=["薄弱点诊断"])
router.include_router(visualization.router, prefix="/visualize", tags=["代码可视化"])
router.include_router(upload.router, prefix="/upload", tags=["文件上传"])
