"""Image OCR Tool - 图片识别工具.

支持两种模式：
1. 多模态 LLM 直接理解图片 (GPT-4o / DeepSeek VL)
2. 传统 OCR 文字识别 + 后续 LLM 分析

已接入 LLM Gateway 多模态能力。
"""

import logging

from app.core.tools import BaseTool, ToolResult
from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


class ImageOCRTool(BaseTool):
    """图片识别工具 - 接入 LLM Gateway 多模态能力."""

    name = "image_ocr"
    description = "识别图片中的文字、题目内容或手写步骤"

    async def execute(self, image_url: str, task: str = "recognize", **kwargs) -> ToolResult:
        """执行图片识别.

        Args:
            image_url: 图片 URL 或本地路径
            task: 识别任务类型 ("recognize" | "parse_question" | "analyze_handwriting")

        Returns:
            识别结果
        """
        task_prompts = {
            "recognize": "请识别并提取这张图片中的所有文字内容，按原文格式输出。",
            "parse_question": "请识别这张图片中的计算机考研408题目，输出科目、知识点、难度和题面内容。",
            "analyze_handwriting": "请分析这张草稿纸图片中的手写解题步骤，识别每一步的内容。",
        }

        prompt = task_prompts.get(task, task_prompts["recognize"])

        try:
            messages = [
                {"role": "system", "content": "你是图片识别专家，请准确识别图片内容。"},
                {"role": "user", "content": prompt},
            ]

            result = await llm_gateway.chat_with_image(messages, image_url)
            return ToolResult(success=True, data={"text": result, "task": task})

        except Exception as e:
            logger.warning(f"ImageOCRTool: 识别失败 ({e})，返回 fallback")
            return ToolResult(
                success=False,
                error=f"图片识别失败: {str(e)[:100]}",
            )


from app.core.tools import tool_registry
tool_registry.register(ImageOCRTool())
