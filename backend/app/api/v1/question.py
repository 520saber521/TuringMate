"""Question parsing API - 图片题目识别."""
from fastapi import APIRouter, UploadFile, File
from app.schemas.question import QuestionParseResponse

router = APIRouter()


@router.post("/parse", response_model=QuestionParseResponse)
async def parse_question_image(
    image: UploadFile = File(...),
):
    """上传图片，识别并解析题目内容.

    调用 QuestionParser Agent (多模态LLM) 解析图片中的题目。
    返回结构化的题目信息：科目、知识点、难度、题面内容等。
    """
    # TODO: 调用 QuestionParser Agent
    return QuestionParseResponse(
        question_id="q_mock_001",
        subject="数据结构",
        knowledge_tags=["线性表", "链表"],
        difficulty=3,
        content="设单链表的表头指针为 L，设计算法删除链表中所有值等于 x 的结点。",
        image_url=f"/uploads/{image.filename}",
    )
