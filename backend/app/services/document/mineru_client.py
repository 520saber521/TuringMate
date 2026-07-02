"""MinerU 文档解析客户端.

MinerU 是一款开源的高质量文档数据提取工具，支持：
  - PDF / 图片 / DOCX / PPT 等多种格式
  - 保留文档结构（标题、段落、表格、公式、图片）
  - 输出 Markdown / JSON / Layout JSON 等多种格式
  - 支持本地部署和在线 API 两种模式

官方文档: https://github.com/opendatalab/MinerU
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
    MinerUError,
    MinerUAuthError,
    MinerURequestError,
    MinerUTimeoutError,
)

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """MinerU 输出格式."""

    MARKDOWN = "markdown"
    JSON = "json"
    LAYOUT_JSON = "layout_json"
    CONTENT_LIST = "content_list"


class MinerUClient:
    """MinerU 异步客户端.

    两种运行模式：
      1. **API 模式** (推荐): 调用远程部署的 MinerU 服务
      2. **本地模式**: 通过 subprocess 调用本地 mineru 命令

    Example:
        >>> client = MinerUClient(base_url="http://localhost:8001")
        >>> result = await client.parse_file("report.pdf")
        >>> print(result["markdown"][:200])
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_token: Optional[str] = None,
        timeout: float = 300.0,
        max_retries: int = 3,
    ) -> None:
        """初始化客户端.

        Args:
            base_url: MinerU 服务地址
            api_token: API Token（部分部署需要）
            timeout: 单次请求超时（秒）
            max_retries: 失败重试次数
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.max_retries = max_retries

        headers = {"User-Agent": "TuringMate-DocProcessor/1.0"}
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers,
        )

        logger.info(f"MinerUClient 初始化: {self.base_url}")

    async def __aenter__(self) -> "MinerUClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def close(self) -> None:
        """关闭 HTTP 连接."""
        await self._client.aclose()
        logger.debug("MinerUClient 已关闭")

    # ───────────────────────────────────────────
    # 健康检查
    # ───────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """检查 MinerU 服务健康状态.

        Returns:
            包含 status、version 等字段的字典
        """
        try:
            r = await self._client.get("/health")
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            raise MinerURequestError(f"MinerU 健康检查失败: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise MinerUError(f"无法连接 MinerU 服务 ({self.base_url}): {e}") from e

    # ───────────────────────────────────────────
    # 文件解析
    # ───────────────────────────────────────────

    async def parse_file(
        self,
        file_path: Union[str, Path],
        output_format: OutputFormat = OutputFormat.MARKDOWN,
        is_ocr: bool = True,
        enable_formula: bool = True,
        enable_table: bool = True,
        language: str = "ch",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """解析单个文档.

        Args:
            file_path: 本地文件路径
            output_format: 输出格式
            is_ocr: 是否启用 OCR（扫描件需开启）
            enable_formula: 是否识别数学公式
            enable_table: 是否识别表格
            language: OCR 语言（ch / en / ch_server / ...）
            extra_params: 额外参数透传

        Returns:
            解析结果字典：
            {
                "markdown": "...",   # 当 output_format=MARKDOWN
                "json": {...},        # 当 output_format=JSON
                "layout_json": [...], # 当 output_format=LAYOUT_JSON
                "meta": {
                    "file_name": "...",
                    "page_count": 10,
                    "parse_time": 5.2,
                    ...
                }
            }
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        logger.info(
            f"MinerU 开始解析: {file_path.name} "
            f"(format={output_format.value}, ocr={is_ocr})"
        )

        params: dict[str, Any] = {
            "output_format": output_format.value,
            "is_ocr": str(is_ocr).lower(),
            "enable_formula": str(enable_formula).lower(),
            "enable_table": str(enable_table).lower(),
            "language": language,
        }
        if extra_params:
            params.update(extra_params)

        # 带重试机制
        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                async with aiofiles.open(file_path, "rb") as f:
                    file_content = await f.read()

                files = {"file": (file_path.name, file_content)}
                response = await self._client.post(
                    "/file_parse",
                    files=files,
                    data=params,
                )
                response.raise_for_status()
                result = response.json()

                # 注入处理元信息
                result.setdefault("meta", {})
                result["meta"].update({
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "parse_time": round(time.time() - start_time, 2),
                    "attempt": attempt,
                })

                logger.info(
                    f"✅ MinerU 解析完成: {file_path.name} "
                    f"耗时 {result['meta']['parse_time']}s"
                )
                return result

            except httpx.TimeoutException as e:
                last_error = MinerUTimeoutError(f"解析超时: {file_path.name}")
                logger.warning(f"MinerU 第 {attempt} 次尝试超时")
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (401, 403):
                    raise MinerUAuthError(
                        f"MinerU 认证失败: {e.response.text}"
                    ) from e
                last_error = MinerURequestError(
                    f"HTTP {e.response.status_code}: {e.response.text[:200]}"
                )
                logger.warning(f"MinerU HTTP 错误 (尝试 {attempt}): {e}")
            except httpx.RequestError as e:
                last_error = MinerUError(f"网络错误: {e}")
                logger.warning(f"MinerU 网络错误 (尝试 {attempt}): {e}")

            # 重试前等待（指数退避）
            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)

        # 所有重试都失败
        raise last_error or MinerUError("MinerU 解析失败")

    async def parse_url(
        self,
        url: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """解析远程 URL 文件.

        Args:
            url: 文件 URL（PDF / 图片）
            output_format: 输出格式
            **kwargs: 其他参数同 parse_file
        """
        logger.info(f"MinerU 解析远程文件: {url}")
        params: dict[str, Any] = {
            "url": url,
            "output_format": output_format.value,
            **{k: v for k, v in kwargs.items() if isinstance(v, (str, int, bool))},
        }

        try:
            response = await self._client.post("/url_parse", json=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise MinerURequestError(f"URL 解析失败: {e.response.text}") from e

    # ───────────────────────────────────────────
    # 批量解析
    # ───────────────────────────────────────────

    async def parse_batch(
        self,
        file_paths: list[Union[str, Path]],
        output_format: OutputFormat = OutputFormat.MARKDOWN,
        max_concurrent: int = 3,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """批量解析多个文件（并发执行）.

        Args:
            file_paths: 文件路径列表
            output_format: 输出格式
            max_concurrent: 最大并发数
            **kwargs: 其他参数
        """
        if not file_paths:
            return []

        logger.info(f"MinerU 批量解析 {len(file_paths)} 个文件（并发={max_concurrent}）")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def _parse_with_semaphore(path: Union[str, Path]) -> dict[str, Any]:
            async with semaphore:
                return await self.parse_file(path, output_format, **kwargs)

        tasks = [_parse_with_semaphore(p) for p in file_paths]
        # return_exceptions=True 让单个失败不影响其他
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 转换异常为统一格式
        processed: list[dict[str, Any]] = []
        for path, result in zip(file_paths, results):
            if isinstance(result, Exception):
                logger.error(f"❌ 解析失败: {path} - {result}")
                processed.append({
                    "success": False,
                    "file": str(path),
                    "error": str(result),
                })
            else:
                processed.append({
                    "success": True,
                    "file": str(path),
                    "result": result,
                })

        success_count = sum(1 for r in processed if r["success"])
        logger.info(f"MinerU 批量完成: {success_count}/{len(file_paths)} 成功")
        return processed


# 全局单例（按需创建）
_default_client: Optional[MinerUClient] = None


def get_mineru_client() -> MinerUClient:
    """获取全局 MinerU 客户端单例."""
    global _default_client
    if _default_client is None:
        from app.config import settings
        _default_client = MinerUClient(
            base_url=getattr(settings, "MINERU_BASE_URL", "http://localhost:8001"),
            api_token=getattr(settings, "MINERU_API_TOKEN", None),
            timeout=getattr(settings, "MINERU_TIMEOUT", 300.0),
        )
    return _default_client
