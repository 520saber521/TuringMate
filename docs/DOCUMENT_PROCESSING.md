# 文档处理解决方案 (MinerU + Gotenberg)

> 基于 MinerU 文档解析和 Gotenberg Office 转 PDF 的端到端文档处理方案

---

## 一、架构概览

```
┌──────────────┐
│ 输入文件     │ (PDF/图片/Office)
└──────┬───────┘
       ↓
┌──────────────┐
│ 文件类型检测 │
└──────┬───────┘
       ↓
   ┌───┴────┐
   ↓        ↓
 Office    PDF/图片
   ↓        ↓
 Gotenberg  ─┐
  转换 PDF   │
   ↓         │
   └────┬────┘
        ↓
  ┌──────────────┐
  │ MinerU 解析  │
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │ 结构化输出   │ (Markdown / JSON / Layout)
  └──────────────┘
```

## 二、环境准备

### 1. 启动 Gotenberg（Docker）

```bash
docker run -d --name gotenberg \
  -p 3000:3000 \
  gotenberg/gotenberg:8
```

### 2. 启动 MinerU

```bash
# 参考: https://github.com/opendatalab/MinerU
# 一键启动 (FastAPI 模式)
docker run -d --name mineru \
  -p 8001:8001 \
  mineru-project/mineru-api:latest
```

### 3. 配置环境变量

在 `backend/.env` 中添加：

```env
# MinerU
MINERU_BASE_URL=http://localhost:8001
MINERU_API_TOKEN=optional_token
MINERU_TIMEOUT=300.0

# Gotenberg
GOTENBERG_BASE_URL=http://localhost:3000
GOTENBERG_TIMEOUT=120.0
```

### 4. 安装依赖

```bash
pip install aiofiles httpx rich click
```

## 三、API 接口

### 1. 上传并处理文档

**请求**:
```bash
curl -X POST "http://localhost:8000/api/v1/document/upload" \
  -F "file=@report.docx" \
  -F "output_format=markdown" \
  -F "is_ocr=true" \
  -F "enable_formula=true" \
  -F "language=ch"
```

**响应**:
```json
{
  "task_id": "task-a1b2c3d4e5f6",
  "input_file": "/tmp/xxx/report.docx",
  "file_type": "office",
  "status": "completed",
  "final_format": "markdown",
  "pdf_path": "/tmp/xxx/report.pdf",
  "markdown_length": 12453,
  "page_count": 12,
  "elapsed_seconds": 8.45,
  "error": null
}
```

### 2. 处理远程 URL

```bash
curl -X POST "http://localhost:8000/api/v1/document/process-url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/paper.pdf",
    "output_format": "markdown",
    "is_ocr": true
  }'
```

### 3. 仅 Office → PDF 转换

```bash
curl -X POST "http://localhost:8000/api/v1/document/convert-pdf" \
  -F "file=@presentation.pptx" \
  -F "page_size=A4" \
  -F "landscape=false"
```

### 4. 任务查询

```bash
# 列出所有任务
curl "http://localhost:8000/api/v1/document/tasks"

# 按状态过滤
curl "http://localhost:8000/api/v1/document/tasks?status=completed"

# 任务详情
curl "http://localhost:8000/api/v1/document/tasks/task-a1b2c3d4e5f6"
```

### 5. 健康检查

```bash
curl "http://localhost:8000/api/v1/document/health"
```

**响应**:
```json
{
  "status": "ok",
  "mineru": {"status": "ok", "version": "1.0.0"},
  "gotenberg": {"status": "healthy", "version": "8.0.0"}
}
```

## 四、CLI 命令行

```bash
# 处理文档
python -m app.cli document process report.docx \
  --format markdown \
  --ocr \
  --language ch \
  --output ./output

# 批量处理
python -m app.cli document process *.pdf *.docx \
  --concurrent 5

# 仅转换 PDF
python -m app.cli document convert presentation.pptx \
  --page-size A4 \
  --landscape

# 健康检查
python -m app.cli document health

# 查看支持的格式
python -m app.cli document formats
```

## 五、Python SDK

### 1. 基础用法

```python
from app.services.document import get_document_service

service = get_document_service()
result = await service.process("report.docx")
print(result.markdown)
```

### 2. 自定义配置

```python
from app.services.document import (
    ProcessingConfig,
    OutputFormat,
    PageSize,
    PDFStandard,
)

config = ProcessingConfig(
    mineru_output_format=OutputFormat.MARKDOWN,
    mineru_is_ocr=True,
    mineru_enable_formula=True,
    mineru_language="ch",
    gotenberg_page_size=PageSize.A4,
    gotenberg_pdf_standard=PDFStandard.PDF_A1B,
    keep_intermediate=False,
    output_dir=Path("./output"),
    max_concurrent=3,
)

result = await service.process("thesis.docx", config)
```

### 3. 批量处理

```python
files = ["doc1.docx", "doc2.pdf", "doc3.pptx"]
results = await service.process_batch(files, config)

for r in results:
    print(f"{r.input_file}: {r.status.value}")
```

### 4. 单独使用客户端

```python
from app.services.document import (
    get_mineru_client,
    get_gotenberg_client,
)

# 仅使用 MinerU
mineru = get_mineru_client()
result = await mineru.parse_file("paper.pdf", output_format=OutputFormat.JSON)

# 仅使用 Gotenberg
gotenberg = get_gotenberg_client()
pdf_bytes = await gotenberg.convert_to_pdf("report.docx")
```

## 六、配置参数说明

### MinerU 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `output_format` | enum | MARKDOWN | 输出格式（markdown/json/layout_json）|
| `is_ocr` | bool | True | 是否启用 OCR |
| `enable_formula` | bool | True | 是否识别数学公式 |
| `enable_table` | bool | True | 是否识别表格 |
| `language` | str | "ch" | OCR 语言（ch/en/...）|

### Gotenberg 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `page_size` | enum | A4 | PDF 页面大小 |
| `landscape` | bool | False | 是否横向 |
| `pdf_standard` | enum | None | PDF 标准（PDF/A-1b 等）|
| `wait_timeout` | float | 30.0 | LibreOffice 启动超时 |

### Pipeline 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|------|
| `skip_office_conversion` | bool | False | 跳过 Office 转 PDF（强制 MinerU 处理）|
| `keep_intermediate` | bool | False | 保留中间 PDF 文件 |
| `max_concurrent` | int | 3 | 批量处理并发数 |
| `output_dir` | Path | None | 输出目录 |

## 七、错误处理

```python
from app.services.document import (
    DocumentError,
    MinerUError,
    MinerUAuthError,
    MinerURequestError,
    MinerUTimeoutError,
    GotenbergError,
    UnsupportedFormatError,
)

try:
    result = await service.process("file.xyz")
except UnsupportedFormatError:
    print("不支持的文件格式")
except MinerUAuthError:
    print("MinerU 认证失败")
except MinerUTimeoutError:
    print("MinerU 解析超时")
except DocumentError as e:
    print(f"处理失败: {e}")
```

## 八、性能优化建议

1. **大文件处理**：
   - 增加 `MINERU_TIMEOUT` 到 600 秒
   - 关闭 OCR (`is_ocr=False`) 可大幅加速（适用于原生 PDF）

2. **批量处理**：
   - 根据机器性能调整 `max_concurrent`（推荐 2-5）
   - 同类文件一起处理（避免反复初始化 LibreOffice）

3. **生产环境**：
   - 使用 Redis 替换内存中的任务存储
   - 添加 Prometheus metrics 监控
   - 配置 Gotenberg 的 Chromium 路由

## 九、依赖与版本

| 组件 | 版本 | 用途 |
|-----|------|------|
| aiofiles | >=23.0 | 异步文件 IO |
| httpx | >=0.25 | 异步 HTTP 客户端 |
| rich | >=13.0 | CLI 美化（可选）|
| click | >=8.0 | CLI 框架（可选）|

## 十、API 完整端点

| 端点 | 方法 | 用途 |
|-----|------|------|
| `/api/v1/document/upload` | POST | 上传并处理文档 |
| `/api/v1/document/process-url` | POST | 处理远程 URL |
| `/api/v1/document/convert-pdf` | POST | 仅 Office → PDF |
| `/api/v1/document/tasks` | GET | 列出任务 |
| `/api/v1/document/tasks/{id}` | GET | 任务详情 |
| `/api/v1/document/health` | GET | 健康检查 |
