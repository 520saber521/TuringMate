"""Code visualization API - 代码可视化."""
from fastapi import APIRouter
from app.schemas.visualization import VisualizeExecuteResponse

router = APIRouter()


@router.post("/execute", response_model=VisualizeExecuteResponse)
async def execute_and_visualize(
    code: str,
    language: str = "python",
):
    """执行代码并生成执行步骤快照.

    代码执行沙箱运行用户提交的算法代码，
    记录每步状态变化（变量值、数据结构状态），
    返回前端用于动画渲染的步骤数据。
    """
    # TODO: 调用 Code Executor 工具执行代码 + 生成快照
    return VisualizeExecuteResponse(
        execution_id="exec_mock_001",
        language=language,
        steps=[
            {
                "step_no": 1,
                "line": 1,
                "description": "初始化链表头结点",
                "variables": {"L": {"type": "Node", "value": "head"}},
                "visual_state": {"nodes": [{"id": "head", "val": None, "next": None}]},
            },
            {
                "step_no": 2,
                "line": 2,
                "description": "插入第一个元素 10",
                "variables": {"L": {"type": "Node", "value": "head"}},
                "visual_state": {
                    "nodes": [
                        {"id": "head", "val": None, "next": "node1"},
                        {"id": "node1", "val": 10, "next": None},
                    ]
                },
            },
        ],
        total_steps=2,
    )
