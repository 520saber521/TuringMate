"""文档处理服务 - 协调 MinerU 和 Gotenberg.

核心 Pipeline 流程：
  ┌──────────────┐
  │ 输入文件     │ (PDF/图片/Office)
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │ 格式判断     │
  └──────┬───────┘
         ↓
  ┌──────┴────────┐
  ↓               ↓
Office 文档     PDF/图片
  ↓               ↓
Gotenberg       直接解析
转换 PDF
  ↓               ↓
  └──────┬────────┘
         ↓
  ┌──────────────┐
  │ MinerU 解析  │ → Markdown / JSON
  └──────────────┘
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import aiofiles

from app.services.document.errors import (
    PipelineError,
    UnsupportedFormatError,
)
from app.services.document.gotenberg_client import (
    GotenbergClient,
    PageSize,
    PDFStandard,
    get_gotenberg_client,
)
from app.services.document.mineru_client import (
    MinerUClient,
    OutputFormat,
    get_mineru_client,
)

logger = logging.getLogger(__name__)


class FileType(str, Enum):
    """文件类型分类."""

    OFFICE = "office"  # .docx/.xlsx/.pptx
    PDF = "pdf"
    IMAGE = "image"  # .png/.jpg/.jpeg
    OTHER = "other"


class TaskStatus(str, Enum):
    """任务状态."""

    PENDING = "pending"
    PROCESSING = "processing"
    CONVERTING = "converting"  # Gotenberg 阶段
    PARSING = "parsing"  # MinerU 阶段
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingConfig:
    """处理配置."""

    # MinerU 参数
    mineru_output_format: OutputFormat = OutputFormat.MARKDOWN
    mineru_is_ocr: bool = True
    mineru_enable_formula: bool = True
    mineru_enable_table: bool = True
    mineru_language: str = "ch"

    # Gotenberg 参数
    gotenberg_page_size: PageSize = PageSize.A4
    gotenberg_landscape: bool = False
    gotenberg_pdf_standard: Optional[PDFStandard] = None
    gotenberg_wait_timeout: float = 30.0

    # Pipeline 参数
    skip_office_conversion: bool = False  # 跳过 Office 转 PDF（强制 MinerU 直接处理）
    keep_intermediate: bool = False  # 保留中间 PDF 文件
    max_concurrent: int = 3

    # 输出
    output_dir: Optional[Path] = None


@dataclass
class ProcessingResult:
    """处理结果."""

    task_id: str
    input_file: str
    file_type: FileType
    status: TaskStatus
    final_format: Optional[OutputFormat] = None

    # 转换产物
    pdf_path: Optional[str] = None
    output_path: Optional[str] = None

    # MinerU 解析结果
    markdown: Optional[str] = None
    json_result: Optional[dict[str, Any]] = None

    # 元信息
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None
    elapsed_seconds: Optional[float] = None
    page_count: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "input_file": self.input_file,
            "file_type": self.file_type.value,
            "status": self.status.value,
            "final_format": self.final_format.value if self.final_format else None,
            "pdf_path": self.pdf_path,
            "output_path": self.output_path,
            "markdown_length": len(self.markdown) if self.markdown else 0,
            "page_count": self.page_count,
            "elapsed_seconds": self.elapsed_seconds,
            "error": self.error,
        }


class DocumentService:
    """文档处理服务.

    提供端到端的文档处理能力：
      1. 自动识别文件类型
      2. Office 文档自动调用 Gotenberg 转 PDF
      3. 调用 MinerU 解析（PDF/图片/转换后的 PDF）
      4. 返回结构化结果

    Example:
        >>> service = DocumentService()
        >>> result = await service.process("report.docx")
        >>> print(result.markdown[:200])
    """

    # 支持的文件扩展名
    OFFICE_EXTS = {
        ".doc", ".docx", ".odt",
        ".xls", ".xlsx", ".ods",
        ".ppt", ".pptx", ".odp",
        ".rtf",
    }
    PDF_EXTS = {".pdf"}
    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}

    def __init__(
        self,
        mineru: Optional[MinerUClient] = None,
        gotenberg: Optional[GotenbergClient] = None,
    ) -> None:
        """初始化服务.

        Args:
            mineru: MinerU 客户端（None 则用默认单例）
            gotenberg: Gotenberg 客户端（None 则用默认单例）
        """
        self.mineru = mineru or get_mineru_client()
        self.gotenberg = gotenberg or get_gotenberg_client()

        # 任务状态存储（生产环境应替换为 Redis）
        self._tasks: dict[str, ProcessingResult] = {}

        logger.info("DocumentService 已初始化")

    # ───────────────────────────────────────────
    # 文件类型识别
    # ───────────────────────────────────────────

    def detect_file_type(self, file_path: Union[str, Path]) -> FileType:
        """根据扩展名判断文件类型."""
        suffix = Path(file_path).suffix.lower()
        if suffix in self.OFFICE_EXTS:
            return FileType.OFFICE
        elif suffix in self.PDF_EXTS:
            return FileType.PDF
        elif suffix in self.IMAGE_EXTS:
            return FileType.IMAGE
        return FileType.OTHER

    def is_supported(self, file_path: Union[str, Path]) -> bool:
        """检查文件是否受支持."""
        return self.detect_file_type(file_path) != FileType.OTHER

    # ───────────────────────────────────────────
    # 单文件处理
    # ───────────────────────────────────────────

    async def process(
        self,
        file_path: Union[str, Path],
        config: Optional[ProcessingConfig] = None,
    ) -> ProcessingResult:
        """处理单个文档.

        Args:
            file_path: 输入文件
            config: 处理配置

        Returns:
            ProcessingResult 对象，包含 Markdown / JSON / 元信息
        """
        file_path = Path(file_path)
        config = config or ProcessingConfig()

        task_id = f"task-{uuid.uuid4().hex[:12]}"
        file_type = self.detect_file_type(file_path)

        logger.info(f"📄 开始处理 [{task_id}]: {file_path.name} (type={file_type.value})")

        result = ProcessingResult(
            task_id=task_id,
            input_file=str(file_path),
            file_type=file_type,
            status=TaskStatus.PROCESSING,
        )
        self._tasks[task_id] = result

        try:
            if file_type == FileType.OTHER:
                raise UnsupportedFormatError(
                    f"不支持的文件格式: {file_path.suffix}"
                )

            # Step 1: Office 文档转 PDF
            pdf_path: Optional[Path] = None
            if file_type == FileType.OFFICE and not config.skip_office_conversion:
                result.status = TaskStatus.CONVERTING
                pdf_path = await self._convert_office_to_pdf(file_path, config)
                result.pdf_path = str(pdf_path)
            else:
                # PDF/图片直接作为输入
                pdf_path = file_path

            # Step 2: MinerU 解析
            result.status = TaskStatus.PARSING
            parse_result = await self.mineru.parse_file(
                pdf_path,
                output_format=config.mineru_output_format,
                is_ocr=config.mineru_is_ocr,
                enable_formula=config.mineru_enable_formula,
                enable_table=config.mineru_enable_table,
                language=config.mineru_language,
            )

            # 提取结果
            result.final_format = config.mineru_output_format
            result.markdown = parse_result.get("markdown")
            result.json_result = parse_result.get("json") or parse_result
            result.page_count = parse_result.get("meta", {}).get("page_count")

            # 可选：保存 Markdown 到文件
            if config.output_dir and result.markdown:
                config.output_dir.mkdir(parents=True, exist_ok=True)
                output_path = config.output_dir / (file_path.stem + ".md")
                async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
                    await f.write(result.markdown)
                result.output_path = str(output_path)

            # 清理中间文件
            if (
                file_type == FileType.OFFICE
                and not config.keep_intermediate
                and pdf_path != file_path
                and pdf_path.exists()
            ):
                try:
                    pdf_path.unlink()
                    logger.debug(f"已清理中间文件: {pdf_path}")
                except OSError:
                    pass

            result.status = TaskStatus.COMPLETED
            result.finished_at = time.time()
            result.elapsed_seconds = round(result.finished_at - result.started_at, 2)
            logger.info(
                f"✅ 处理完成 [{task_id}]: {file_path.name} 耗时 {result.elapsed_seconds}s"
            )

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.finished_at = time.time()
            result.elapsed_seconds = round(result.finished_at - result.started_at, 2)
            logger.error(f"❌ 处理失败 [{task_id}]: {e}")

        return result

    async def _convert_office_to_pdf(
        self,
        file_path: Path,
        config: ProcessingConfig,
    ) -> Path:
        """使用 Gotenberg 将 Office 转换为 PDF."""
        # 生成中间 PDF 路径
        if config.output_dir:
            config.output_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = config.output_dir / (file_path.stem + ".pdf")
        else:
            # 使用临时目录
            import tempfile
            tmp_dir = Path(tempfile.gettempdir()) / "turingmate_doc"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = tmp_dir / (file_path.stem + ".pdf")

        await self.gotenberg.convert_to_pdf(
            file_path,
            output_path=pdf_path,
            page_size=config.gotenberg_page_size,
            landscape=config.gotenberg_landscape,
            pdf_standard=config.gotenberg_pdf_standard,
            wait_timeout=config.gotenberg_wait_timeout,
        )
        return pdf_path

    # ───────────────────────────────────────────
    # 批量处理
    # ───────────────────────────────────────────

    async def process_batch(
        self,
        file_paths: list[Union[str, Path]],
        config: Optional[ProcessingConfig] = None,
    ) -> list[ProcessingResult]:
        """批量处理多个文件.

        Args:
            file_paths: 文件路径列表
            config: 处理配置

        Returns:
            处理结果列表
        """
        config = config or ProcessingConfig()
        max_concurrent = config.max_concurrent

        logger.info(
            f"📚 批量处理 {len(file_paths)} 个文件（并发={max_concurrent}）"
        )

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _process_with_semaphore(path: Union[str, Path]) -> ProcessingResult:
            async with semaphore:
                return await self.process(path, config)

        tasks = [_process_with_semaphore(p) for p in file_paths]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r.status == TaskStatus.COMPLETED)
        logger.info(f"批量处理完成: {success}/{len(file_paths)} 成功")
        return results

    # ───────────────────────────────────────────
    # 任务查询
    # ───────────────────────────────────────────

    def get_task(self, task_id: str) -> Optional[ProcessingResult]:
        """获取任务结果."""
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> list[ProcessingResult]:
        """列出任务，可按状态过滤."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.started_at, reverse=True)


# 全局服务实例
_service_instance: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """获取全局文档服务单例."""
    global _service_instance
    if _service_instance is None:
        _service_instance = DocumentService()
    return _service_instance
