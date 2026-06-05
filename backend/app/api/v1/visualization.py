"""Code visualization API - 代码可视化."""
import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.schemas.visualization import VisualizeExecuteResponse, VisualStep
from app.core.tools import code_executor

logger = logging.getLogger(__name__)
router = APIRouter()


class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    test_input: str | None = None


@router.post("/execute", response_model=VisualizeExecuteResponse)
async def execute_and_visualize(body: ExecuteRequest):
    """执行代码并生成执行步骤快照.

    调用安全的 code_executor 沙箱执行用户代码，
    记录每步变量状态变化，返回步骤数据供前端可视化渲染。
    """
    execution_id = f"exec_{uuid.uuid4().hex[:12]}"

    result = await code_executor.ainvoke({
        "code": body.code,
        "language": body.language,
        "test_input": body.test_input,
    })

    if not result.get("success"):
        raise HTTPException(status_code=422, detail=result.get("error", "执行失败"))

    steps = [
        VisualStep(
            step_no=s["step_no"],
            line=s["line"],
            description=s["description"],
            variables=s.get("variables", {}),
            visual_state=s.get("visual_state", {}),
        )
        for s in result.get("steps", [])
    ]

    return VisualizeExecuteResponse(
        execution_id=execution_id,
        language=body.language,
        steps=steps,
        total_steps=len(steps),
        output=result.get("output", ""),
        success=result.get("success", False),
        error=result.get("error"),
    )
