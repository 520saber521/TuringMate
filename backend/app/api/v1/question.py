"""Question parsing API - 图片/文本题目识别.

基于 LangChain QuestionParserAgent + 多模态 LLM.
使用统一工具 (api.utils.format_agent_result).
"""
import os
import uuid
import tempfile

from fastapi import APIRouter, UploadFile, File
from app.schemas.question import QuestionParseResponse
from app.agents.question_parser import question_parser_agent
from app.api.utils import format_agent_result

router = APIRouter()


@router.post("/parse", response_model=QuestionParseResponse)
async def parse_question_image(image: UploadFile = File(...)):
    """上传图片，识别并解析题目内容.

    LangChain QuestionParserAgent 调用多模态 LLM 解析图片中的题目。
    返回结构化的题目信息：科目、知识点、难度、题面内容等。
    """
    ext = os.path.splitext(image.filename or "upload.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"turingmate_q_{filename}")

    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)

        raw_result = await question_parser_agent.parse_image(image_url=file_path)
        result = format_agent_result(raw_result)

        return QuestionParseResponse(
            question_id=result.get("question_id") or f"q_{uuid.uuid4().hex[:8]}",
            subject=result.get("subject", "未识别"),
            knowledge_tags=result.get("knowledge_tags", []),
            difficulty=result.get("difficulty", 3),
            content=result.get("content", ""),
            image_url=f"/uploads/{image.filename}",
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/subjects")
async def get_subject_list():
    """获取支持的科目列表."""
    return {
        "subjects": [
            {"id": "ds", "name": "数据结构", "icon": "Tree"},
            {"id": "co", "name": "计组", "icon": "Cpu"},
            {"id": "os", "name": "操作系统", "icon": "Monitor"},
            {"id": "cn", "name": "计算机网络", "icon": "Globe"},
        ]
    }
