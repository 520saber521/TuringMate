"""文档处理 CLI 命令.

使用方式:
    # 处理单个文件
    python -m app.cli doc-process report.docx
    
    # 批量处理
    python -m app.cli doc-process *.pdf
    
    # 仅转换 PDF（不解析）
    python -m app.cli doc-convert presentation.pptx
    
    # 健康检查
    python -m app.cli doc-health
    
    # 自定义配置
    python -m app.cli doc-process thesis.docx \\
        --format markdown \\
        --ocr \\
        --language ch \\
        --output ./output
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from app.core.logging import setup_logging
from app.services.document.gotenberg_client import PageSize, PDFStandard
from app.services.document.mineru_client import OutputFormat
from app.services.document.service import (
    DocumentService,
    ProcessingConfig,
    TaskStatus,
    get_document_service,
)

console = Console()


@click.group(name="doc", help="📄 文档处理工具（MinerU + Gotenberg）")
def doc_cli() -> None:
    """文档处理命令组."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# ────────────────────────────────────────
# 单文件处理
# ────────────────────────────────────────


@doc_cli.command("process", help="处理文档（Office → PDF → Markdown）")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--format", "output_format",
    type=click.Choice([f.value for f in OutputFormat]),
    default=OutputFormat.MARKDOWN.value,
    help="MinerU 输出格式",
)
@click.option("--ocr/--no-ocr", default=True, help="是否启用 OCR")
@click.option("--formula/--no-formula", default=True, help="是否识别公式")
@click.option("--table/--no-table", default=True, help="是否识别表格")
@click.option("--language", default="ch", help="OCR 语言")
@click.option("--skip-convert", is_flag=True, help="跳过 Office 转 PDF")
@click.option("--keep-intermediate", is_flag=True, help="保留中间 PDF")
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="./output",
    help="输出目录",
)
@click.option("--concurrent", "-c", default=3, help="最大并发数")
def process_cmd(
    files: tuple[str, ...],
    output_format: str,
    ocr: bool,
    formula: bool,
    table: bool,
    language: str,
    skip_convert: bool,
    keep_intermediate: bool,
    output: str,
    concurrent: int,
) -> None:
    """处理一个或多个文档."""
    asyncio.run(_process_files(
        files=list(files),
        output_format=OutputFormat(output_format),
        ocr=ocr,
        formula=formula,
        table=table,
        language=language,
        skip_convert=skip_convert,
        keep_intermediate=keep_intermediate,
        output=Path(output),
        concurrent=concurrent,
    ))


async def _process_files(
    files: list[str],
    output_format: OutputFormat,
    ocr: bool,
    formula: bool,
    table: bool,
    language: str,
    skip_convert: bool,
    keep_intermediate: bool,
    output: Path,
    concurrent: int,
) -> None:
    """异步处理文件."""
    service = get_document_service()
    config = ProcessingConfig(
        mineru_output_format=output_format,
        mineru_is_ocr=ocr,
        mineru_enable_formula=formula,
        mineru_enable_table=table,
        mineru_language=language,
        skip_office_conversion=skip_convert,
        keep_intermediate=keep_intermediate,
        output_dir=output,
        max_concurrent=concurrent,
    )

    console.print(f"\n📚 [bold]开始处理 {len(files)} 个文件[/bold]")
    console.print(f"   输出目录: [cyan]{output.absolute()}[/cyan]")
    console.print(f"   输出格式: [cyan]{output_format.value}[/cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task("处理中...", total=len(files))

        # 串行处理（方便显示进度）
        results = []
        for f in files:
            progress.update(task_id, description=f"处理 {Path(f).name}...")
            result = await service.process(f, config)
            results.append(result)
            progress.advance(task_id)

    # 显示结果表格
    _print_results_table(results)


def _print_results_table(results: list) -> None:
    """打印结果表格."""
    table = Table(title="处理结果", show_header=True, header_style="bold magenta")
    table.add_column("文件", style="cyan", no_wrap=False)
    table.add_column("类型", style="blue")
    table.add_column("状态", style="bold")
    table.add_column("页数", justify="right")
    table.add_column("耗时(s)", justify="right")
    table.add_column("备注", style="dim")

    for r in results:
        status_style = "green" if r.status == TaskStatus.COMPLETED else "red"
        status_text = r.status.value.upper()

        table.add_row(
            Path(r.input_file).name,
            r.file_type.value,
            f"[{status_style}]{status_text}[/{status_style}]",
            str(r.page_count or "-"),
            f"{r.elapsed_seconds:.2f}" if r.elapsed_seconds else "-",
            r.error or "✓",
        )

    console.print(table)

    # 统计
    success = sum(1 for r in results if r.status == TaskStatus.COMPLETED)
    console.print(
        f"\n📊 [bold]统计[/bold]: {success}/{len(results)} 成功"
    )


# ────────────────────────────────────────
# 仅 Office → PDF
# ────────────────────────────────────────


@doc_cli.command("convert", help="仅 Office → PDF 转换")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--page-size", default=PageSize.A4.value,
    type=click.Choice([p.value for p in PageSize]),
    help="PDF 页面大小",
)
@click.option("--landscape", is_flag=True, help="横向")
@click.option(
    "--pdf-standard", default=None,
    type=click.Choice([s.value for s in PDFStandard] + [None]),
    help="PDF 标准",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="./pdf_output",
    help="输出目录",
)
def convert_cmd(
    files: tuple[str, ...],
    page_size: str,
    landscape: bool,
    pdf_standard: Optional[str],
    output: str,
) -> None:
    """将 Office 文档转换为 PDF."""
    asyncio.run(_convert_files(
        files=list(files),
        page_size=PageSize(page_size),
        landscape=landscape,
        pdf_standard=PDFStandard(pdf_standard) if pdf_standard else None,
        output=Path(output),
    ))


async def _convert_files(
    files: list[str],
    page_size: PageSize,
    landscape: bool,
    pdf_standard: Optional[PDFStandard],
    output: Path,
) -> None:
    service = get_document_service()
    output.mkdir(parents=True, exist_ok=True)

    console.print(f"\n🔄 [bold]开始转换 {len(files)} 个文件 → PDF[/bold]")

    results = await service.gotenberg.convert_batch(
        file_paths=[Path(f) for f in files],
        output_dir=output,
        page_size=page_size,
        landscape=landscape,
        pdf_standard=pdf_standard,
    )

    # 打印结果
    table = Table(title="转换结果", show_header=True)
    table.add_column("输入", style="cyan")
    table.add_column("输出", style="green")
    table.add_column("大小(KB)", justify="right")
    table.add_column("状态", style="bold")

    for r in results:
        status = "✅ 成功" if r["success"] else "❌ 失败"
        output_name = Path(r["output"]).name if r["output"] else "-"
        table.add_row(
            Path(r["input"]).name,
            output_name,
            f"{r['size']/1024:.1f}",
            status,
        )

    console.print(table)


# ────────────────────────────────────────
# 健康检查
# ────────────────────────────────────────


@doc_cli.command("health", help="检查 MinerU 和 Gotenberg 服务健康")
def health_cmd() -> None:
    """检查服务健康状态."""
    asyncio.run(_health_check())


async def _health_check() -> None:
    service = get_document_service()

    console.print("\n🏥 [bold]服务健康检查[/bold]\n")

    # MinerU
    try:
        result = await service.mineru.health_check()
        console.print(f"✅ MinerU:    [green]正常[/green]  {result}")
    except Exception as e:
        console.print(f"❌ MinerU:    [red]异常[/red]    {e}")

    # Gotenberg
    try:
        version = await service.gotenberg.get_version()
        console.print(f"✅ Gotenberg: [green]正常[/green]  版本 {version}")
    except Exception as e:
        console.print(f"❌ Gotenberg: [red]异常[/red]    {e}")


# ────────────────────────────────────────
# 列出支持格式
# ────────────────────────────────────────


@doc_cli.command("formats", help="列出支持的文件格式")
def formats_cmd() -> None:
    """列出支持的文件格式."""
    table = Table(title="支持的文件格式", show_header=True)
    table.add_column("类型", style="bold cyan")
    table.add_column("扩展名", style="green")
    table.add_column("处理流程")

    table.add_row("Office 文档", ".doc/.docx/.ppt/.pptx/.xls/.xlsx/...", "Gotenberg → PDF → MinerU")
    table.add_row("PDF", ".pdf", "MinerU 直接解析")
    table.add_row("图片", ".png/.jpg/.jpeg/...", "MinerU + OCR 解析")

    console.print(table)


if __name__ == "__main__":
    doc_cli()
