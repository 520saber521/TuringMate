"""Gotenberg Office → PDF 转换客户端.

Gotenberg 是一款基于 Chromium 和 LibreOffice 的文档转换服务：
  - 支持 Word / Excel / PowerPoint / HTML / Markdown 等多种格式
  - 批量并发转换
  - 提供丰富的元数据选项（页眉、页脚、水印、PDF/A 合规等）

官方文档: https://gotenberg.dev/
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import aiofiles
import httpx

from app.services.document.errors import (
    GotenbergError,
    GotenbergRequestError,
    GotenbergTimeoutError,
)

logger = logging.getLogger(__name__)


class PageSize(str, Enum):
    """PDF 页面大小."""

    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    A6 = "A6"
    LETTER = "Letter"
    LEGAL = "Legal"


class PDFStandard(str, Enum):
    """PDF 标准."""

    PDF_A1A = "PDF/A-1a"
    PDF_A1B = "PDF/A-1b"
    PDF_A2A = "PDF/A-2a"
    PDF_A2B = "PDF/A-2b"
    PDF_A2U = "PDF/A-2u"
    PDF_A3A = "PDF/A-3a"
    PDF_A3B = "PDF/A-3b"
    PDF_A3U = "PDF/A-3u"


class GotenbergClient:
    """Gotenberg 异步客户端.

    核心功能：
      1. 单文件转换（libreoffice/convert）
      2. 批量并发转换
      3. 自定义页眉页脚/水印

    Example:
        >>> client = GotenbergClient(base_url="http://localhost:3000")
        >>> pdf_bytes = await client.convert_to_pdf("report.docx")
        >>> with open("report.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3000",
        timeout: float = 120.0,
        max_retries: int = 3,
    ) -> None:
        """初始化客户端.

        Args:
            base_url: Gotenberg 服务地址
            timeout: 单次请求超时
            max_retries: 失败重试次数
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"User-Agent": "TuringMate-DocProcessor/1.0"},
        )

        logger.info(f"GotenbergClient 初始化: {self.base_url}")

    async def __aenter__(self) -> "GotenbergClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()
        logger.debug("GotenbergClient 已关闭")

    # ───────────────────────────────────────────
    # 健康检查
    # ───────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """检查 Gotenberg 健康状态（返回版本信息）."""
        try:
            r = await self._client.get("/health")
            r.raise_for_status()
            return r.json()
        except httpx.RequestError as e:
            raise GotenbergError(f"无法连接 Gotenberg ({self.base_url}): {e}") from e

    async def get_version(self) -> str:
        """获取 Gotenberg 版本."""
        r = await self._client.get("/version")
        r.raise_for_status()
        return r.text.strip()

    # ───────────────────────────────────────────
    # 单文件转换
    # ───────────────────────────────────────────

    async def convert_to_pdf(
        self,
        file_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        page_size: PageSize = PageSize.A4,
        landscape: bool = False,
        pdf_standard: Optional[PDFStandard] = None,
        native_page_ranges: Optional[str] = None,
        wait_timeout: float = 30.0,
        header_html: Optional[str] = None,
        footer_html: Optional[str] = None,
        extra_metadata: Optional[dict[str, str]] = None,
    ) -> bytes:
        """将 Office 文档转换为 PDF.

        支持的输入格式（依赖 LibreOffice）：
          - .doc, .docx, .odt
          - .xls, .xlsx, .ods
          - .ppt, .pptx, .odp
          - .rtf, .txt, .html, .md
          - .csv

        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径（None 则不保存到磁盘）
            page_size: 页面大小
            landscape: 是否横向
            pdf_standard: PDF 标准（合规性）
            native_page_ranges: 原生页范围，如 "1-5" 或 "1-3,5,7-9"
            wait_timeout: 等待 LibreOffice 启动的超时（秒）
            header_html: 自定义页眉 HTML
            footer_html: 自定义页脚 HTML
            extra_metadata: PDF 元数据

        Returns:
            PDF 二进制内容
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 限制 Office 文件类型
        office_exts = {
            ".doc", ".docx", ".odt",
            ".xls", ".xlsx", ".ods",
            ".ppt", ".pptx", ".odp",
            ".rtf", ".txt", ".html", ".md", ".csv",
        }
        if file_path.suffix.lower() not in office_exts:
            raise GotenbergError(
                f"不支持的文件类型: {file_path.suffix}，"
                f"仅支持 Office 文档 ({', '.join(sorted(office_exts))})"
            )

        logger.info(f"Gotenberg 转换开始: {file_path.name} → PDF")

        # 构建 multipart form
        async with aiofiles.open(file_path, "rb") as f:
            file_content = await f.read()

        files = {"files": (file_path.name, file_content)}
        form_data: dict[str, str] = {
            "landscape": str(landscape).lower(),
            "pageSize": page_size.value,
            "waitTimeout": str(int(wait_timeout)),
        }
        if pdf_standard:
            form_data["pdfFormat"] = pdf_standard.value
        if native_page_ranges:
            form_data["nativePageRanges"] = native_page_ranges
        if header_html:
            files["header.html"] = ("header.html", header_html.encode())
        if footer_html:
            files["footer.html"] = ("footer.html", footer_html.encode())
        if extra_metadata:
            for k, v in extra_metadata.items():
                form_data[k] = v

        # 重试逻辑
        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                response = await self._client.post(
                    "/forms/libreoffice/convert",
                    files=files,
                    data=form_data,
                )
                response.raise_for_status()
                pdf_bytes = response.content
                elapsed = round(time.time() - start_time, 2)

                # 保存到磁盘（如果指定）
                if output_path:
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    async with aiofiles.open(output_path, "wb") as f:
                        await f.write(pdf_bytes)

                logger.info(
                    f"✅ Gotenberg 转换完成: {file_path.name} → {output_path or 'bytes'} "
                    f"({len(pdf_bytes)/1024:.1f}KB, {elapsed}s)"
                )
                return pdf_bytes

            except httpx.TimeoutException as e:
                last_error = GotenbergTimeoutError(f"转换超时: {file_path.name}")
                logger.warning(f"Gotenberg 第 {attempt} 次尝试超时")
            except httpx.HTTPStatusError as e:
                last_error = GotenbergRequestError(
                    f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                )
                logger.warning(f"Gotenberg HTTP 错误 (尝试 {attempt}): {e}")
            except httpx.RequestError as e:
                last_error = GotenbergError(f"网络错误: {e}")
                logger.warning(f"Gotenberg 网络错误 (尝试 {attempt}): {e}")

            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)

        raise last_error or GotenbergError("Gotenberg 转换失败")

    # ───────────────────────────────────────────
    # 批量转换
    # ───────────────────────────────────────────

    async def convert_batch(
        self,
        file_paths: list[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        max_concurrent: int = 3,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """批量转换多个文件为 PDF.

        Args:
            file_paths: 输入文件列表
            output_dir: 输出目录（None 则不保存）
            max_concurrent: 最大并发数
            **kwargs: 透传给 convert_to_pdf

        Returns:
            转换结果列表：
            [
                {
                    "success": True/False,
                    "input": "report.docx",
                    "output": "report.pdf" or None,
                    "size": 12345,
                    "error": None or "错误信息"
                }
            ]
        """
        if not file_paths:
            return []

        output_dir = Path(output_dir) if output_dir else None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Gotenberg 批量转换 {len(file_paths)} 个文件 → {output_dir or '内存'} "
            f"(并发={max_concurrent})"
        )

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _convert_with_semaphore(
            path: Union[str, Path],
        ) -> dict[str, Any]:
            async with semaphore:
                try:
                    output = None
                    if output_dir:
                        output = output_dir / (Path(path).stem + ".pdf")

                    pdf_bytes = await self.convert_to_pdf(
                        path,
                        output_path=output,
                        **kwargs,
                    )
                    return {
                        "success": True,
                        "input": str(path),
                        "output": str(output) if output else None,
                        "size": len(pdf_bytes),
                        "error": None,
                    }
                except Exception as e:
                    logger.error(f"❌ Gotenberg 转换失败: {path} - {e}")
                    return {
                        "success": False,
                        "input": str(path),
                        "output": None,
                        "size": 0,
                        "error": str(e),
                    }

        tasks = [_convert_with_semaphore(p) for p in file_paths]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r["success"])
        logger.info(f"Gotenberg 批量完成: {success}/{len(file_paths)} 成功")
        return results

    # ───────────────────────────────────────────
    # HTML → PDF（额外能力）
    # ───────────────────────────────────────────

    async def html_to_pdf(
        self,
        html: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> bytes:
        """HTML 字符串转 PDF.

        Args:
            html: HTML 内容
            output_path: 输出文件路径

        Returns:
            PDF 字节
        """
        files = {"files": ("index.html", html.encode())}
        form_data = {"paperWidth": "8.27", "paperHeight": "11.69"}  # A4

        response = await self._client.post(
            "/forms/chromium/convert/html",
            files=files,
            data=form_data,
        )
        response.raise_for_status()
        pdf_bytes = response.content

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(output_path, "wb") as f:
                await f.write(pdf_bytes)

        return pdf_bytes


# 全局单例
_default_client: Optional[GotenbergClient] = None


def get_gotenberg_client() -> GotenbergClient:
    """获取全局 Gotenberg 客户端单例."""
    global _default_client
    if _default_client is None:
        from app.config import settings
        _default_client = GotenbergClient(
            base_url=getattr(settings, "GOTENBERG_BASE_URL", "http://localhost:3000"),
            timeout=getattr(settings, "GOTENBERG_TIMEOUT", 120.0),
        )
    return _default_client
