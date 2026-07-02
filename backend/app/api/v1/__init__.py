"""API Router - V1 endpoints."""
from fastapi import APIRouter

from app.api.v1 import (
    question, chat, correction, diagnosis,
    visualization, upload,
    learning_path, thinking, emotion,
    problem_gen, code_practical,
    auth, mistake, knowledge, community,
    document,
)

router = APIRouter()

# ── 认证路由 ──
router.include_router(auth.router, prefix="/auth", tags=["用户认证"])

# ── 核心功能路由 ──
router.include_router(question.router, prefix="/question", tags=["题库 & 题目识别"])
router.include_router(mistake.router, prefix="/mistakes", tags=["错题本"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["知识点Wiki"])
router.include_router(community.router, prefix="/community", tags=["社区"])
router.include_router(chat.router, prefix="/chat", tags=["引导对话"])
router.include_router(correction.router, prefix="/correction", tags=["手写批改"])
router.include_router(diagnosis.router, prefix="/diagnosis", tags=["薄弱点诊断"])

# ── 可视化路由 ──
router.include_router(visualization.router, prefix="/visualize", tags=["代码可视化"])
router.include_router(upload.router, prefix="/upload", tags=["文件上传"])

# ══════════════════════════════════════════════════════════
# 4 大差异化功能模块 (Features 1-4)
# ══════════════════════════════════════════════════════════

# Feature 1: 动态学习路径规划器
router.include_router(
    learning_path.router, prefix="/learning-path",
    tags=["🧭 动态路径规划"],
)

# Feature 2: 思维回放（已弃用 - 保留路由以兼容旧客户端）
router.include_router(
    thinking.router, prefix="/thinking",
    tags=["💭 思维回放(已弃用)"],
)

# Feature 3: 情绪感知与状态调节
router.include_router(
    emotion.router, prefix="/emotion",
    tags=["😊 情绪感知"],
)

# Feature 4: 「举一反三」题目生成器
router.include_router(
    problem_gen.router, prefix="/problem-gen",
    tags=["🔄 举一反三"],
)

# Feature 5: 「代码即题目」实战模块
router.include_router(
    code_practical.router, prefix="/code",
    tags=["💻 代码实战"],
)

# 文档处理 (MinerU + Gotenberg)
router.include_router(
    document.router, prefix="/document",
    tags=["📄 文档处理"],
)
