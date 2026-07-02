"""文档处理 API 路由.

端点列表:
  POST   /api/v1/document/upload         - 上传并处理文档
  POST   /api/v1/document/process        - 处理已上传文件
  POST   /api/v1/document/process-url    - 处理远程 URL
  GET    /api/v1/document/tasks          - 列出任务
  GET    /api/v1/document/tasks/{id}     - 获取任务详情
  GET    /api/v1/document/health         - 健康检查
  POST   /api/v1/document/convert-pdf    - 仅 Office → PDF（不解析）
"""

from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.document.errors import (
    DocumentError,
    UnsupportedFormatError,
)
from app.services.document.gotenberg_client import (
    PageSize,
    PDFStandard,
)
from app.services.document.mineru_client import OutputFormat
from app.services.document.service import (
    DocumentService,
    FileType,
    ProcessingConfig,
    ProcessingResult,
    TaskStatus,
    get_document_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["📄 文档处理"])


# ────────────────────────────────────────
# 请求/响应模型
# ────────────────────────────────────────


class ProcessUrlRequest(BaseModel):
    """处理远程 URL 的请求."""

    url: str = Field(..., description="文件 URL（PDF/图片/Office）")
    output_format: OutputFormat = Field(default=OutputFormat.MARKDOWN)
    is_ocr: bool = Field(default=True)
    enable_formula: bool = Field(default=True)
    enable_table: bool = Field(default=True)
    language: str = Field(default="ch")


class ConvertPdfRequest(BaseModel):
    """仅 Office → PDF 转换请求."""

    output_path: Optional[str] = Field(default=None, description="输出文件路径")
    page_size: PageSize = Field(default=PageSize.A4)
    landscape: bool = Field(default=False)
    pdf_standard: Optional[PDFStandard] = Field(default=None)


class TaskInfoResponse(BaseModel):
    """任务信息响应."""

    task_id: str
    input_file: str
    file_type: str
    status: str
    final_format: Optional[str] = None
    pdf_path: Optional[str] = None
    output_path: Optional[str] = None
    markdown_length: int = 0
    page_count: Optional[int] = None
    elapsed_seconds: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应."""

    status: str
    mineru: dict[str, Any]
    gotenberg: dict[str, Any]


# ────────────────────────────────────────
# 工具函数
# ────────────────────────────────────────


async def _save_upload_file(upload: UploadFile) -> Path:
    """保存上传文件到临时目录."""
    suffix = Path(upload.filename or "file").suffix
    tmp_dir = Path(tempfile.gettempdir()) / "turingmate_uploads"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    file_path = tmp_dir / f"{uuid.uuid4().hex}{suffix}"
    with file_path.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return file_path


def _result_to_response(result: ProcessingResult) -> TaskInfoResponse:
    return TaskInfoResponse(**result.to_dict())


# ────────────────────────────────────────
# API 端点
# ────────────────────────────────────────


@router.post("/upload", response_model=TaskInfoResponse, summary="上传并处理文档")
async def upload_and_process(
    file: UploadFile = File(..., description="待处理文件（PDF/Office/图片）"),
    output_format: OutputFormat = Form(default=OutputFormat.MARKDOWN),
    is_ocr: bool = Form(default=True),
    enable_formula: bool = Form(default=True),
    enable_table: bool = Form(default=True),
    language: str = Form(default="ch"),
    skip_office_conversion: bool = Form(default=False),
    keep_intermediate: bool = Form(default=False),
) -> TaskInfoResponse:
    """上传文档并完成端到端处理.

    处理流程：
      1. Office 文档 → Gotenberg → PDF
      2. PDF/图片 → MinerU → Markdown/JSON
    """
    service = get_document_service()

    # 检查文件类型
    suffix = Path(file.filename or "").suffix
    if not service.is_supported(f"fake{suffix}"):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {suffix}",
        )

    # 保存临时文件
    file_path = await _save_upload_file(file)
    logger.info(f"文件已上传: {file_path} ({file_path.stat().st_size} bytes)")

    try:
        config = ProcessingConfig(
            mineru_output_format=output_format,
            mineru_is_ocr=is_ocr,
            mineru_enable_formula=enable_formula,
            mineru_enable_table=enable_table,
            mineru_language=language,
            skip_office_conversion=skip_office_conversion,
            keep_intermediate=keep_intermediate,
        )
        result = await service.process(file_path, config)
        return _result_to_response(result)
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DocumentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理上传文件
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            pass


@router.post("/process-url", response_model=TaskInfoResponse, summary="处理远程 URL")
async def process_url(body: ProcessUrlRequest) -> TaskInfoResponse:
    """处理远程 URL 的文档（MinerU 直接处理）。"""
    service = get_document_service()

    try:
        parse_result = await service.mineru.parse_url(
            body.url,
            output_format=body.output_format,
            is_ocr=body.is_ocr,
            enable_formula=body.enable_formula,
            enable_table=body.enable_table,
            language=body.language,
        )
        # 包装成 ProcessingResult
        result = ProcessingResult(
            task_id=f"url-{uuid.uuid4().hex[:8]}",
            input_file=body.url,
            file_type=FileType.OTHER,
            status=TaskStatus.COMPLETED,
            final_format=body.output_format,
            markdown=parse_result.get("markdown"),
            json_result=parse_result.get("json"),
            page_count=parse_result.get("meta", {}).get("page_count"),
            finished_at=__import__("time").time(),
        )
        return _result_to_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL 处理失败: {e}")


@router.post("/convert-pdf", summary="仅 Office → PDF 转换")
async def convert_to_pdf(
    file: UploadFile = File(..., description="Office 文档"),
    page_size: PageSize = Form(default=PageSize.A4),
    landscape: bool = Form(default=False),
    pdf_standard: Optional[PDFStandard] = Form(default=None),
) -> JSONResponse:
    """仅执行 Office → PDF 转换（不调用 MinerU）。"""
    service = get_document_service()
    file_path = await _save_upload_file(file)

    try:
        # 生成输出路径
        suffix = Path(file.filename or "file").stem
        output_path = file_path.parent / f"{suffix}.pdf"

        pdf_bytes = await service.gotenberg.convert_to_pdf(
            file_path,
            output_path=output_path,
            page_size=page_size,
            landscape=landscape,
            pdf_standard=pdf_standard,
        )

        return JSONResponse({
            "success": True,
            "input": str(file_path),
            "output": str(output_path),
            "size": len(pdf_bytes),
            "page_size": page_size.value,
            "landscape": landscape,
        })
    except DocumentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            pass


@router.get("/tasks", response_model=list[TaskInfoResponse], summary="列出任务")
async def list_tasks(
    status: Optional[TaskStatus] = Query(default=None, description="按状态过滤"),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[TaskInfoResponse]:
    """列出已处理任务，可按状态过滤。"""
    service = get_document_service()
    tasks = service.list_tasks(status)
    return [_result_to_response(t) for t in tasks[:limit]]


@router.get("/tasks/{task_id}", response_model=TaskInfoResponse, summary="任务详情")
async def get_task(task_id: str) -> TaskInfoResponse:
    """获取任务详情。"""
    service = get_document_service()
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return _result_to_response(task)


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check() -> HealthResponse:
    """检查 MinerU 和 Gotenberg 服务健康状态。"""
    service = get_document_service()
    mineru_status: dict[str, Any] = {"status": "unknown"}
    gotenberg_status: dict[str, Any] = {"status": "unknown"}

    # MinerU 健康
    try:
        mineru_status = await service.mineru.health_check()
    except DocumentError as e:
        mineru_status = {"status": "unhealthy", "error": str(e)}

    # Gotenberg 健康
    try:
        version = await service.gotenberg.get_version()
        gotenberg_status = {"status": "healthy", "version": version}
    except DocumentError as e:
        gotenberg_status = {"status": "unhealthy", "error": str(e)}

    overall = "ok" if (
        mineru_status.get("status") != "unhealthy"
        and gotenberg_status.get("status") != "unhealthy"
    ) else "degraded"

    return HealthResponse(
        status=overall,
        mineru=mineru_status,
        gotenberg=gotenberg_status,
    )
