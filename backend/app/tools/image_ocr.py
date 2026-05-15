"""Image OCR Tool - 图片识别工具.

使用 LangChain @tool 装饰器定义，支持多模态 LLM 图片识别。
完整实现见 app.core.tools.image_ocr
"""

from app.core.tools import image_ocr

__all__ = ["image_ocr"]
