# 豆包拍照识别Agent 使用文档

## 概述

基于豆包Doubao-Seed-2.0-lite的拍照识别Agent，实现图像采集、预处理、识别分析的完整流程。

支持识别：
- 数学公式（LaTeX格式输出）
- 代码片段
- 文字题目
- 混合内容

---

## 快速开始

### 1. 环境配置

在 `.env` 文件中添加豆包API配置：

```env
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 2. Python调用示例

```python
from app.agents import recognize_photo, PhotoRecognitionResult

# 基本识别
result = await recognize_photo("/path/to/question.jpg")

# 带上下文提示
result = await recognize_photo(
    "/path/to/question.jpg",
    context={
        "subject": "data_structure",
        "hint": "可能是二叉树遍历题目"
    }
)

print(result)
```

### 3. API调用示例

#### 方式一：上传并识别

```bash
curl -X POST http://localhost:8000/api/v1/photo/upload-and-recognize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/question.jpg" \
  -F "subject=data_structure"
```

#### 方式二：识别已有图片

```bash
curl -X POST http://localhost:8000/api/v1/photo/recognize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "/path/to/question.jpg",
    "subject": "data_structure"
  }'
```

---

## API接口

### POST /api/v1/photo/upload-and-recognize

上传图片并立即识别。

**请求参数：**
- `file`: 图片文件（multipart/form-data）
- `subject`: 可选，科目提示
- `hint`: 可选，其他提示信息

**响应示例：**
```json
{
  "success": true,
  "processing_time_ms": 1234.56,
  "content": {
    "content_type": "text_question",
    "subject": "data_structure",
    "raw_text": "已知一棵二叉树的前序遍历是ABC...",
    "formatted_content": "已知一棵二叉树的前序遍历是ABC..."
  },
  "question_info": {
    "question_type": "calculation",
    "difficulty": "medium",
    "key_points": ["二叉树", "前序遍历", "中序遍历"]
  },
  "suggestions": []
}
```

### POST /api/v1/photo/recognize

识别已有的图片文件。

**请求体：**
```json
{
  "image_url": "/path/to/image.jpg",
  "subject": "data_structure",
  "hint": "二叉树相关题目"
}
```

### GET /api/v1/photo/health

健康检查接口。

---

## 数据模型

### PhotoRecognitionResult

完整识别结果。

| 字段 | 类型 | 说明 |
|-----|------|-----|
| success | bool | 是否识别成功 |
| processing_time_ms | float | 处理耗时（毫秒） |
| content | RecognizedContent \| null | 识别内容 |
| question_info | QuestionInfo \| null | 题目分析信息 |
| error_message | string \| null | 错误信息 |
| suggestions | string[] | 改进建议 |

### RecognizedContent

识别内容详情。

| 字段 | 类型 | 说明 |
|-----|------|-----|
| content_type | string | 内容类型：math_formula/code/text_question/mixed |
| subject | string \| null | 科目 |
| raw_text | string | 原始识别文本 |
| formatted_content | string | 格式化后内容 |

### QuestionInfo

题目分析信息。

| 字段 | 类型 | 说明 |
|-----|------|-----|
| question_type | string \| null | 题型 |
| difficulty | string \| null | 难度 |
| key_points | string[] | 核心知识点 |

---

## 科目列表

可用科目：
- `data_structure`: 数据结构
- `os`: 操作系统
- `computer_network`: 计算机网络
- `computer_organization`: 计算机组成原理
- `general`: 综合题目

---

## 错误处理

Agent会自动处理以下异常情况：

| 异常类型 | 说明 |
|---------|------|
| ImageTooSmallError | 图片小于10KB |
| ImageTooLargeError | 图片大于10MB |
| UnsupportedFormatError | 不支持的格式 |
| BlurryImageError | 图片模糊（可选检测） |
| RecognitionTimeoutError | 识别超时（默认60秒） |
| RecognitionFailedError | 识别失败 |

---

## 图片要求

- **格式支持**：JPG, PNG, GIF, BMP, WebP
- **文件大小**：10KB ~ 10MB
- **建议**：
  - 图片清晰，光线良好
  - 题目内容完整
  - 避免倾斜、模糊
  - 尽量减少无关背景

---

## 高级用法

### 批量识别

```python
from app.agents import photo_recognizer

results = await photo_recognizer.recognize_batch([
    "/path/to/image1.jpg",
    "/path/to/image2.jpg",
    "/path/to/image3.jpg"
])
```

### 同步调用

```python
from app.agents import photo_recognizer

result = photo_recognizer.recognize_sync(
    "/path/to/image.jpg",
    context={"subject": "os"}
)
```

---

## 完整示例

### 前端集成示例

```typescript
// 使用 fetch 上传并识别
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('subject', 'data_structure');

const response = await fetch('/api/v1/photo/upload-and-recognize', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
  },
  body: formData,
});

const data = await response.json();

if (data.success) {
  console.log('识别成功:', data.content);
  console.log('格式化内容:', data.content.formatted_content);
} else {
  console.error('识别失败:', data.error_message);
  console.log('建议:', data.suggestions);
}
```

---

## 常见问题

**Q: 识别准确率低怎么办？**
A: 确保图片清晰、光线充足、内容完整。可以添加 subject 提示。

**Q: 如何提高识别速度？**
A: 调整代码中的超时时间，或裁剪不必要的图片区域。

**Q: 支持哪些数学公式？**
A: 支持 LaTeX 格式的各类数学公式，包括行内公式和块级公式。
