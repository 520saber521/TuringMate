"""Handwriting correction API - 手写批改."""
from fastapi import APIRouter, UploadFile, File
from app.schemas.correction import CorrectionAnalyzeResponse

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
    # TODO: 调用 Corrector Agent 分析
    return CorrectionAnalyzeResponse(
        correction_id="corr_mock_001",
        question_id=question_id or "q_mock_001",
        steps=[
            {
                "step_no": 1,
                "content": "初始化指针 p = L->next",
                "is_correct": True,
            },
            {
                "step_no": 2,
                "content": "while (p != NULL) 遍历链表",
                "is_correct": False,
                "error_type": "逻辑错误",
                "hint": "删除结点时需要维护前驱结点指针，直接遍历会丢失前驱信息哦~",
            },
        ],
        overall_feedback="整体思路正确，但在删除操作上遗漏了前驱结点的处理。建议回顾一下单链表删除的标准写法！",
    )
