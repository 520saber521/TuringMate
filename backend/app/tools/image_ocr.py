"""Image OCR Tool - 图片识别工具.

支持两种模式：
1. 多模态 LLM 直接理解图片 (GPT-4o / DeepSeek VL)
2. 传统 OCR 文字识别 + 后续 LLM 分析

MVP 阶段使用多模态 LLM 模式。
"""

from app.core.tools import BaseTool, ToolResult


class ImageOCRTool(BaseTool):
    """图片识别工具."""

    name = "image_ocr"
    description = "识别图片中的文字、题目内容或手写步骤"

    async def execute(self, image_url: str, task: str = "recognize") -> ToolResult:
        """执行图片识别.

        Args:
            image_url: 图片 URL
            task: 识别任务类型 ("recognize" | "parse_question" | "analyze_handwriting")

        Returns:
            识别结果
        """
        # TODO: 调用 LLM Gateway 的 chat_with_image 方法
        match task:
            case "recognize":
                return ToolResult(
                    success=True,
                    data={"text": "[Mock] 识别到的文字内容..."},
                )
            case "parse_question":
                return ToolResult(
                    success=True,
                    data={
                        "subject": "数据结构",
                        "content": "[Mock] 识别到的题目内容...",
                        "tags": ["链表"],
                    },
                )
            case _:
                return ToolResult(success=False, error=f"Unknown task: {task}")


# 注册到全局工具表
from app.core.tools import tool_registry
tool_registry.register(ImageOCRTool())
