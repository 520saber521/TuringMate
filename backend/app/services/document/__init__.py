"""文档处理模块.

提供：
  - MinerU 客户端（文档解析）
  - Gotenberg 客户端（Office → PDF）
  - DocumentService（端到端 Pipeline）
  - 异常类型

Example:
    >>> from app.services.document import (
    ...     get_document_service,
    ...     ProcessingConfig,
    ...     OutputFormat,
    ... )
    >>>
    >>> service = get_document_service()
    >>> result = await service.process("report.docx")
    >>> print(result.markdown)
"""

from app.services.document.errors import (
    DocumentError,
    GotenbergError,
    GotenbergRequestError,
    GotenbergTimeoutError,
    MinerUAuthError,
    MinerUError,
    MinerURequestError,
    MinerUTimeoutError,
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
from app.services.document.service import (
    DocumentService,
    FileType,
    ProcessingConfig,
    ProcessingResult,
    TaskStatus,
    get_document_service,
)

__all__ = [
    # Service
    "DocumentService",
    "get_document_service",
    "ProcessingConfig",
    "ProcessingResult",
    "FileType",
    "TaskStatus",

    # Clients
    "MinerUClient",
    "get_mineru_client",
    "GotenbergClient",
    "get_gotenberg_client",

    # Enums
    "OutputFormat",
    "PageSize",
    "PDFStandard",

    # Errors
    "DocumentError",
    "MinerUError",
    "MinerUAuthError",
    "MinerURequestError",
    "MinerUTimeoutError",
    "GotenbergError",
    "GotenbergRequestError",
    "GotenbergTimeoutError",
    "PipelineError",
    "UnsupportedFormatError",
]
