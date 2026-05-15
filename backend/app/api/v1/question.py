"""Question parsing API - 图片题目识别."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.question import QuestionParseResponse
from app.agents.question_parser import QuestionParserAgent

router = APIRouter()
agent = QuestionParserAgent()


@router.post("/parse", response_model=QuestionParseResponse)
async def parse_question_image(image: UploadFile = File(...)):
    """上传图片，识别并解析题目内容.

    调用 QuestionParser Agent (多模态LLM) 解析图片中的题目。
    返回结构化的题目信息：科目、知识点、难度、题面内容等。

    流程：
    1. 接收前端上传的图片文件
    2. 保存到临时目录（后续改为 COS）
    3. 调用 QuestionParser Agent 解析
    4. 返回结构化结果
    """
    import os, uuid, tempfile

    # 1. 保存上传的图片
    ext = os.path.splitext(image.filename or "upload.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"turingmate_{filename}")

    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 2. 调用 QuestionParser Agent
        result = await agent.parse_image(image_path=file_path)

        # 3. 返回结构化响应
        return QuestionParseResponse(
            question_id=result["question_id"],
            subject=result["subject"],
            knowledge_tags=result.get("knowledge_tags", []),
            difficulty=result["difficulty"],
            content=result["content"],
            image_url=f"/uploads/{image.filename}",
        )
    finally:
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/subjects")
async def get_subject_list():
    """获取支持的科目列表."""
    return {
        "subjects": [
            {"id": "ds", "name": "数据结构", "icon": "🌲"},
            {"id": "co", "name": "计组", "icon": "⚙️"},
            {"id": "os", "name": "操作系统", "icon": "🖥️"},
            {"id": "cn", "name": "计算机网络", "icon": "🌐"},
        ]
    }
