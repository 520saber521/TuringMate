# TuringMate

> **408 计算机考研 AI 1 对 1 私教** - 用苏格拉底式引导教学替代"直接给答案"

## 产品定位

不是给你答案，而是帮你长出解题能力的 AI 学长。

## 核心功能

| 功能 | 说明 |
|------|------|
| 拍照搜题 | 拍题目自动识别，开始引导讲解 |
| 手写批改 | 拍草稿纸，定位具体哪一步出错 |
| 引导式讲解 | 不直接给答案，用提问带学生推导 |
| 薄弱点诊断 | 自动分析错题，输出弱点报告和专项练习 |
| 四科联动 | 跨科目关联知识点，打通408全局 |
| 代码可视化 | 算法题自动生成运行过程图示 |

## 技术架构

```
Vue 3 (前端) ←HTTP/SSE→ FastAPI (后端) → LangGraph Agent + RAG + 工具链
```

### 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Tailwind CSS + TDesign + Pinia + Vue Router
- **后端**: Python FastAPI + LangGraph Agent + LangChain RAG
- **AI**: 多模型网关（DeepSeek / GPT-4o / 通义千问 可切换）
- **部署**: Docker Compose + 腾讯云生态（CVM / VectorDB / COS / MySQL）

## 快速开始

### 前置要求

- Node.js >= 18
- Python >= 3.11
- Docker & Docker Compose（可选）
- Git

### 1. 克隆项目

```bash
git clone https://github.com/520saber521/TuringMate.git
cd TuringMate
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 3. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 配置环境变量
uvicorn app.main:app --reload --port 8000
# 访问 http://localhost:8000/docs 查看 API 文档
```

### 4. Docker 一键启动（推荐开发使用）

```bash
docker-compose up -d
```

## 项目结构

```
TuringMate/
├── frontend/          # Vue 3 前端项目
│   ├── src/
│   │   ├── api/       # API 服务层
│   │   ├── assets/    # 静态资源 + 全局样式
│   │   ├── components/# 通用组件
│   │   ├── composables/
│   │   ├── router/    # 路由配置
│   │   ├── stores/    # Pinia 状态管理
│   │   ├── types/     # TypeScript 类型
│   │   └── views/     # 页面视图
│   └── ...
├── backend/           # Python 后端项目
│   ├── app/
│   │   ├── main.py    # FastAPI 入口
│   │   ├── config.py  # 配置管理
│   │   ├── api/       # API 路由层
│   │   ├── agents/    # Agent 模块 (LangGraph)
│   │   ├── core/      # LLM Gateway + Tool 基类
│   │   ├── rag/       # RAG 管线
│   │   ├── tools/     # Agent 工具链
│   │   ├── models/    # SQLAlchemy ORM
│   │   ├── schemas/   # Pydantic Schema
│   │   └── services/  # 业务逻辑层
│   └── requirements.txt
├── docker-compose.yml  # 编排文件
└── README.md
```

## 开发计划

| Step | 任务 | 状态 |
|------|------|------|
| 1 | 项目初始化 | ✅ 进行中 |
| 2 | 布局框架 + LLM Gateway | ⏳ 待开始 |
| 3 | 首页 + 拍照搜题 | ⏳ 待开始 |
| 4 | 引导式对话 | ⏳ 待开始 |
| 5 | 手写批改 + 薄弱点诊断 | ⏳ 待开始 |
| 6 | 代码可视化 | ⏳ 待开始 |
| 7 | RAG + 工具链 + 联调 | ⏳ 待开始 |

## License

MIT
