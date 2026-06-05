# TuringMate

> **408 计算机考研 AI 1 对 1 私教** - 用苏格拉底式引导教学替代"直接给答案"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-orange.svg)](https://fastapi.tiangolo.com/)

---

## 目录

- [项目概述](#项目概述)
- [核心功能](#核心功能)
- [技术栈与架构](#技术栈与架构)
- [安装与配置](#安装与配置)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [贡献指南](#贡献指南)
- [更新日志](#更新日志)
- [许可证](#许可证)
- [联系方式](#联系方式)

---

## 项目概述

### 项目名称

**TuringMate** (图灵伴侣)

### 项目目标

TuringMate 是一款专为 408 计算机考研学生打造的 AI 智能学习助手。项目采用**苏格拉底式教学法**，不直接给出答案，而是通过启发式提问引导学生主动思考，帮助学生真正理解知识点，培养解题能力。

### 价值主张

| 传统学习方式 | TuringMate |
|------------|-----------|
| 抄答案 | 引导思考 |
| 看不懂解析 | 1对1个性化讲解 |
| 盲目刷题 | 精准薄弱点诊断 |
| 单科孤立 | 四科知识联动 |

---

## 核心功能

### 🚀 六大核心功能

| 功能模块 | 说明 | 技术亮点 |
|---------|------|---------|
| **AI 对话** | 基于 LangGraph 的引导式讲解 Agent | 苏格拉底提问法、多轮对话状态管理 |
| **拍照识别** | 拍题自动识别并开始引导 | 支持数学公式、代码、文字识别 |
| **手写批改** | 逐行分析草稿纸，定位错误 | 多模态理解、步骤级批改 |
| **薄弱诊断** | 智能分析错题，输出弱点报告 | RAG 检索、知识图谱关联 |
| **举一反三** | 基于知识点智能生成相似题目 | 变式生成、难度控制 |
| **代码实战** | 「代码即题目」在线编程挑战 | Monaco Editor、在线执行 |

### 🎯 特色亮点

- **苏格拉底式引导**：不直接给答案，用提问引导学生推导
- **四科联动**：打通数据结构、操作系统、计算机网络、计算机组成原理
- **多模型支持**：DeepSeek / GPT-4o / 通义千问 一键切换
- **知识图谱**：跨科目知识点关联，精准薄弱点定位
- **RAG 增强**：历年真题知识库，智能检索相似题目

---

## 技术栈与架构

### 技术架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (Vue 3)                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │  组件库  │  │  状态管理 │  │  路由    │  │  API    │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端 (FastAPI)                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │  API层   │  │ Agent层  │  │ RAG层   │  │ 工具层   │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   ChromaDB   │    │    MySQL     │    │  LLM Gateway  │
│  (向量数据库) │    │   (关系数据库) │    │  (多模型调用)  │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 前端技术栈

| 技术 | 版本 | 用途 |
|-----|------|-----|
| Vue | 3.5+ | 渐进式 JavaScript 框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 8.x | 构建工具 |
| Tailwind CSS | 4.x | 原子化 CSS |
| Pinia | 3.x | 状态管理 |
| Vue Router | 4.x | 路由管理 |
| TDesign | 1.x | UI 组件库 |
| Lucide | 1.x | 图标库 |
| ECharts | 6.x | 数据可视化 |

### 后端技术栈

| 技术 | 版本 | 用途 |
|-----|------|-----|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.115+ | Web 框架 |
| LangChain | 0.3+ | LLM 应用框架 |
| LangGraph | 0.2+ | Agent 编排 |
| ChromaDB | 0.5+ | 向量数据库 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.0+ | 数据验证 |

### AI 模型支持

```python
MODEL_REGISTRY = {
    "deepseek": {"model": "deepseek-chat"},
    "openai": {"model": "gpt-4o"},
    "qwen": {"model": "qwen-plus"},
    "doubao": {"model": "doubao-seed-2.0-lite"},
}
```

---

## 安装与配置

### 系统要求

| 要求 | 最低版本 | 推荐版本 |
|-----|---------|---------|
| Node.js | 18.x | 20.x LTS |
| Python | 3.11 | 3.12 |
| MySQL | 8.0 | 8.0+ |
| Docker | 24.0 | 最新版本 |

### 环境变量配置

在后端根目录创建 `.env` 文件：

```env
# ============================================
# LLM Configuration - Model Gateway
# ============================================
DEFAULT_LLM_MODEL=deepseek

DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# Doubao (可选)
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# ============================================
# Database Configuration
# ============================================
DATABASE_URL=mysql+pymysql://turingmate:turingmate@localhost:3306/turingmate
REDIS_URL=redis://localhost:6379/0

# ============================================
# Application Settings
# ============================================
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

---

## 快速开始

### 方式一：手动安装

#### 1. 克隆项目

```bash
git clone https://github.com/520saber521/TuringMate.git
cd TuringMate
```

#### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

#### 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API Key

# 启动服务
uvicorn app.main:app --reload --port 8000
# 访问 http://localhost:8000/docs 查看 API 文档
```

#### 4. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 可选：导入历年真题到知识库
python -m app.rag.seed
```

### 方式二：Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 验证安装

启动成功后，访问以下地址验证：

| 服务 | 地址 | 说明 |
|-----|------|-----|
| 前端 | http://localhost:5173 | 用户界面 |
| 后端 API | http://localhost:8000 | REST API |
| API 文档 | http://localhost:8000/docs | Swagger 文档 |

---

## 项目结构

```
TuringMate/
├── frontend/                    # Vue 3 前端项目
│   ├── src/
│   │   ├── api/               # API 服务层
│   │   │   ├── index.ts      # API 客户端
│   │   │   ├── auth.ts       # 认证 API
│   │   │   ├── chat.ts        # 对话 API
│   │   │   ├── question.ts    # 题目 API
│   │   │   └── ...
│   │   ├── assets/            # 静态资源
│   │   │   └── styles/        # 全局样式
│   │   │       ├── tokens.css # 设计令牌
│   │   │       └── global.css # 全局样式
│   │   ├── components/         # Vue 组件
│   │   │   ├── layout/        # 布局组件
│   │   │   │   ├── AppHeader.vue
│   │   │   │   ├── AppSidebar.vue
│   │   │   │   └── AppLayout.vue
│   │   │   ├── ui/            # 基础 UI 组件
│   │   │   │   ├── Button.vue
│   │   │   │   ├── Card.vue
│   │   │   │   ├── Avatar.vue
│   │   │   │   └── ...
│   │   │   └── upload/         # 上传组件
│   │   ├── composables/        # 组合式函数
│   │   ├── router/            # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── auth.ts         # 认证状态
│   │   │   ├── chat.ts         # 对话状态
│   │   │   └── studyTimer.ts   # 学习计时
│   │   ├── types/              # TypeScript 类型
│   │   └── views/              # 页面视图
│   │       ├── HomeView.vue
│   │       ├── ChatView.vue
│   │       ├── CameraView.vue
│   │       └── ...
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                    # Python 后端项目
│   ├── app/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   ├── api/                # API 路由层
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py     # 认证接口
│   │   │   │   ├── chat.py     # 对话接口
│   │   │   │   ├── question.py # 题目接口
│   │   │   │   └── ...
│   │   │   ├── deps.py         # 依赖注入
│   │   │   └── utils.py       # 工具函数
│   │   ├── agents/            # Agent 模块 (LangGraph)
│   │   │   ├── __init__.py
│   │   │   ├── socratic_tutor.py   # 苏格拉底导师
│   │   │   ├── question_parser.py   # 题目解析
│   │   │   ├── corrector.py         # 手写批改
│   │   │   ├── diagnostician.py     # 薄弱诊断
│   │   │   ├── learning_path_planner.py
│   │   │   ├── thinking_tracer.py
│   │   │   ├── emotion_detector.py
│   │   │   ├── problem_generator.py
│   │   │   ├── study_buddy.py
│   │   │   ├── code_practical.py
│   │   │   └── orchestrator.py      # 主调度器
│   │   ├── core/                # 核心模块
│   │   │   ├── llm_gateway.py   # LLM 网关
│   │   │   ├── prompts.py       # 提示词模板
│   │   │   ├── security.py      # 安全认证
│   │   │   └── tools.py         # 工具基类
│   │   ├── rag/                 # RAG 管线
│   │   │   ├── embeddings.py    # Embedding 模型
│   │   │   ├── loader.py        # 文档加载
│   │   │   ├── splitter.py       # 文档分割
│   │   │   ├── vectorstore.py   # 向量存储
│   │   │   └── retriever.py     # 检索器
│   │   ├── tools/               # Agent 工具链
│   │   │   ├── code_executor.py # 代码执行
│   │   │   ├── image_ocr.py    # 图片 OCR
│   │   │   ├── question_search.py
│   │   │   └── knowledge_graph.py
│   │   ├── models/             # SQLAlchemy ORM
│   │   │   ├── user.py
│   │   │   ├── question.py
│   │   │   ├── chat.py
│   │   │   └── diagnosis.py
│   │   ├── schemas/            # Pydantic Schema
│   │   ├── services/            # 业务逻辑层
│   │   ├── crud/               # 数据库操作
│   │   └── db/                 # 数据库配置
│   ├── data/                    # 数据目录
│   │   ├── chroma_db/          # ChromaDB 存储
│   │   └── knowledge/          # 知识库文件
│   ├── tests/                   # 测试文件
│   ├── alembic/                 # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                        # 文档目录
├── docker-compose.yml            # Docker 编排
└── README.md
```

### 目录说明

| 目录 | 说明 |
|-----|------|
| `frontend/src/views` | 页面级组件，对应路由 |
| `frontend/src/components` | 可复用组件，按功能分组 |
| `backend/app/agents` | LangGraph Agent 实现 |
| `backend/app/rag` | RAG 检索增强生成 |
| `backend/app/tools` | Agent 调用的工具函数 |
| `backend/data/knowledge` | 历年真题 PDF |

---

## API 文档

### 认证接口

| 方法 | 路径 | 说明 |
|-----|------|-----|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/logout` | 用户登出 |
| GET | `/api/v1/auth/me` | 获取当前用户 |

### 核心功能接口

| 方法 | 路径 | 说明 |
|-----|------|-----|
| POST | `/api/v1/question/parse` | 拍照识别题目 |
| POST | `/api/v1/chat/start` | 开始引导对话 |
| POST | `/api/v1/chat/message` | 发送对话消息 |
| POST | `/api/v1/correction/analyze` | 手写批改分析 |
| POST | `/api/v1/diagnosis/analyze` | 薄弱点诊断 |

详细 API 文档请访问：http://localhost:8000/docs

---

## 贡献指南

### 开发流程

1. **Fork 项目** 到你的 GitHub 仓库
2. **克隆** 你 Fork 的仓库到本地
3. **创建分支** 进行开发
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **编写代码** 并添加测试
5. **提交更改**
   ```bash
   git commit -m "feat: 添加新功能"
   ```
6. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **创建 Pull Request**

### 代码规范

- **前端**：遵循 ESLint + Prettier 配置
- **后端**：遵循 PEP 8 + Black 格式化
- 提交信息使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范

### 测试

```bash
# 运行后端测试
cd backend
pytest tests/ -v

# 运行前端类型检查
cd frontend
npm run type-check
```

---

## 更新日志

### v0.1.0 (开发中)

- ✅ 六大核心功能模块
- ✅ 苏格拉底式引导教学
- ✅ 多模型 LLM 网关
- ✅ RAG 知识库增强
- 🔄 移动端适配优化
- 🔄 深色模式完善

---

## 许可证

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

---

## 联系方式

| 渠道 | 地址 |
|-----|------|
| GitHub | https://github.com/520saber521/TuringMate |
| 问题反馈 | https://github.com/520saber521/TuringMate/issues |
| 交流群 | (待添加) |

---

<div align="center">

**TuringMate** - 让 AI 成为你的考研路上的最佳伴侣

*用苏格拉底式引导教学，帮你在考研路上少走弯路*

</div>
