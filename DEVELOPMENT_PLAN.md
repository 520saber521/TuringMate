# TuringMate 7-Day Sprint Plan

> 写作规约：每个 Feature 用 **User Story + Acceptance Criteria（Given-When-Then）** 描述；只描述"是什么"和"怎么算做完"，实现细节交给代码。
>
> 状态枚举：
> - `Done` —— 已合入主干、可演示、可验证。
> - `In Progress` —— 当前正在开发，有活跃分支/改动。
> - `Planned` —— 仅在计划中，未动代码。
>
> 当前项目状态：**后端 API + 6大差异化 Agent 全部已实现，前端核心页面（首页/搜题/对话/批改/诊断）已实现**；核心缺口为 **数据库持久化、用户认证、6大差异化功能前端页面、端到端联调**。

---

## 缺口覆盖矩阵

> 以下为 7 天冲刺需覆盖的全部缺口，按优先级排列。P1 必须在 D1-D7 内形成可演示闭环；P2 允许降级实现但必须出现在文档中。

| 缺口 | 优先级 | 计划覆盖 | 验收口径 |
|------|--------|----------|----------|
| 数据库持久化（ORM→真实查询） | P1 | D1-D2 | 所有 API 端点均从 MySQL 读写，不再使用内存 mock |
| 用户注册/登录/JWT 认证 | P1 | D2 | 注册→登录→JWT 鉴权链路完整，未登录无法调用受保护 API |
| 举一反三·变式题生成前端页 | P1 | D3 | 用户可从首页/对话页触发变式题生成→查看→作答→验证掌握度 |
| AI 研友多角色前端页 | P1 | D4 | 用户可选择研友角色→进入多角色对话→查看会话记录 |
| 代码实战前端完整化 | P1 | D4 | 4种代码挑战可浏览→进入→编码→提交→查看解析 |
| 动态学习路径前端页 | P1 | D5 | 基于诊断报告生成→展示路径→可调整→追踪进度 |
| 思维过程可视化前端页 | P1 | D5 | 对话中实时记录思考步骤→可视化回放路径图→成长报告 |
| 情绪感知前端反馈 | P2 | D5 | 对话中展示情绪状态指示→教学模式切换可感知 |
| 代码可视化执行沙箱 | P2 | D6 | Python 代码真实执行→步骤快照→播放器回放 |
| 端到端联调与 Bug 修复 | P1 | D6-D7 | 全流程可演示，核心链路 P0 Bug 清零 |
| 文档定稿与演示准备 | P1 | D7 | README/API 文档/架构图/演示脚本全部就绪 |

---

## 阶段 D1-D2：架构加固与数据持久化

> 目标：将项目从"mock 数据原型"升级为"真实数据驱动"的生产级架构，完成用户认证闭环。

### F-D1-1 — Alembic 数据库迁移与 ORM 激活 · `Planned`

**User Story**：作为开发者，我希望所有 API 端点都从 MySQL 读写数据，而不是依赖内存缓存和 mock 数据，确保服务重启后数据不丢失。

**Acceptance Criteria**：

- GIVEN Docker Compose 中 MySQL 服务已启动且 `turingmate` 数据库已创建
- WHEN 执行 `alembic upgrade head`
- THEN 所有 5 张表（users, questions, chat_sessions, mistakes, diagnosis_reports）必须正确创建，字段类型与 ORM 模型一致
- AND 现有 ORM 模型的 JSON 字段（knowledge_tags, messages, scores, weak_points, recommendations, solution_steps, weak_subjects）必须使用 MySQL JSON 列类型
- AND chat_sessions.messages 字段必须能存储至少 200 条对话消息的 JSON 数组
- AND 迁移脚本必须幂等，重复执行不报错

**核心技术实现点**：

1. 初始化 Alembic：`alembic init alembic`，配置 `env.py` 读取 `Base.metadata`
2. 生成初始迁移：`alembic revision --autogenerate -m "init_tables"`
3. 为 JSON 字段添加 `mysql_type="JSON"` 声明
4. 创建 `backend/app/db/session.py` 统一 Session 工厂（engine → sessionmaker → get_db 依赖注入）
5. 替换 `backend/app/api/deps.py` 中 `get_db` 为真实 DB session

**交付物**：
- `alembic/` 目录及初始迁移脚本
- `backend/app/db/session.py` 数据库会话管理
- 5 张表在 MySQL 中可验证创建

---

### F-D1-2 — API 端点数据库接入 · `Planned`

**User Story**：作为用户，我希望我的对话历史、错题记录、诊断报告在刷新页面后依然存在，而不是每次重启服务都归零。

**Acceptance Criteria**：

- GIVEN 数据库迁移已完成且 MySQL 中有数据
- WHEN 调用以下 API 端点
  - `POST /api/v1/chat/start` — 创建 chat_session 写入 DB
  - `POST /api/v1/chat/message` — 追加消息到 chat_session.messages
  - `GET /api/v1/diagnosis/report` — 从 diagnosis_reports 读取或生成后持久化
  - `GET /api/v1/diagnosis/practice` — 从 questions + mistakes 关联查询
  - `POST /api/v1/correction/analyze` — 批改结果写入 mistakes
- THEN 每个端点必须使用 SQLAlchemy Session 执行真实 SQL 查询
- AND 服务重启后，相同请求参数应返回持久化的历史数据
- AND 所有 JSON 字段的读写必须正确序列化/反序列化

**核心技术实现点**：

1. 为每张表创建 CRUD 操作封装（`backend/app/crud/` 目录）
2. chat_sessions.messages 使用 `json.dumps/loads` + MySQL JSON 列
3. diagnosis_reports 的 scores/weak_points/recommendations 同理
4. 替换所有 `# TODO: 用真实 DB 查询` 注释处的 mock 代码
5. 添加数据库连接池配置（pool_size=10, max_overflow=20）

**交付物**：
- `backend/app/crud/` 目录下 CRUD 模块
- 所有核心 API 端点使用真实 DB 读写
- curl/Postman 测试脚本验证数据持久化

---

### F-D2-1 — 用户注册与登录 · `Planned`

**User Story**：作为新用户，我想注册账号并登录，以便系统记住我的学习进度和诊断报告。

**Acceptance Criteria**：

- GIVEN 数据库中 users 表已创建
- WHEN 用户 `POST /api/v1/auth/register` 提交 `{username, password, name}`
- THEN 服务端必须对密码做 bcrypt 哈希后存入 DB，返回 `201 Created` 含 user_id
- AND 当 username 重复时返回 `409 Conflict`
- AND WHEN 用户 `POST /api/v1/auth/login` 提交 `{username, password}`
- THEN 验证通过后返回 `{access_token, token_type: "bearer", user_info}`
- AND access_token 必须为 JWT，过期时间 24h，payload 含 `sub=user_id`
- AND 密码错误时返回 `401 Unauthorized`，不提示具体是用户名还是密码错误

**核心技术实现点**：

1. `backend/app/api/v1/auth.py` 新增 register/login 路由
2. `passlib[bcrypt]` 哈希 + `python-jose[cryptography]` JWT 签发
3. JWT 配置写入 `backend/app/config.py`（SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES）
4. `backend/app/api/deps.py` 的 `get_current_user` 从 Authorization header 解析 JWT
5. 所有受保护端点添加 `Depends(get_current_user)` 依赖

**交付物**：
- 注册/登录 API 端点
- JWT 签发与验证中间件
- curl 测试脚本

---

### F-D2-2 — 前端登录/注册页与鉴权集成 · `Planned`

**User Story**：作为用户，我想在浏览器中完成注册和登录，登录后所有请求自动携带身份凭证。

**Acceptance Criteria**：

- GIVEN 前端应用已启动
- WHEN 未登录用户访问任意受保护页面
- THEN 应重定向到登录页
- AND 登录页同时提供注册入口，切换无需跳转新页面
- AND 登录成功后 JWT token 存储到 localStorage，axios 拦截器自动附加 `Authorization: Bearer <token>` header
- AND 刷新页面后若 token 未过期，自动恢复登录态
- AND 顶部 Header 显示用户头像和名称，而非固定的 "用户"

**核心技术实现点**：

1. 新建 `frontend/src/views/AuthView.vue`（登录/注册双态切换）
2. 新建 `frontend/src/stores/auth.ts`（Pinia store: token, user, login/register/logout actions）
3. 路由守卫 `router.beforeEach` 检查 token 有效性
4. Axios 请求拦截器注入 Authorization header
5. Axios 响应拦截器处理 401 → 自动跳转登录页

**交付物**：
- 登录/注册前端页面
- Pinia auth store + 路由守卫
- Header 用户信息动态显示

---

## 阶段 D3-D5：6 大差异化功能前端实现

> 目标：将后端已就绪的 6 大差异化 Agent 能力完整呈现到前端，形成差异化产品体验闭环。

### F-D3-1 — 举一反三·变式题生成页 · `Planned`

**User Story**：作为学生，我在做完一道题后希望系统能自动生成类似的变式题让我练习，直到我真正掌握这个知识点。

**Acceptance Criteria**：

- GIVEN 用户在对话页完成一道题的学习，或在首页点击"举一反三"入口
- WHEN 触发变式题生成
- THEN 页面应展示：原题→变式题（含题目、选项/填空、知识点标签、难度）→作答区→提交验证
- AND 变式题必须标注所用的知识点和与原题的关联
- AND 用户提交答案后，调用 `/problem-gen/validate` 返回掌握程度评估（未掌握/部分掌握/已掌握）
- AND 若未掌握，自动推荐下一道变式题；若已掌握，展示鼓励反馈
- AND 可查看内置模板列表（8 个模板，覆盖 DS/OS/CO/CN）

**核心技术实现点**：

1. 新建 `frontend/src/views/ProblemGenView.vue`
2. 新增路由 `/problem-gen` 和 `/problem-gen/:questionId`
3. 调用 `POST /api/v1/problem-gen/generate`（传入原题信息 + 科目 + 知识点）
4. 调用 `POST /api/v1/problem-gen/validate`（提交用户答案）
5. 调用 `GET /api/v1/problem-gen/templates`（模板列表展示）
6. 作答流程状态机：生成中 → 作答中 → 验证中 → 结果展示 → 下一题/完成

**交付物**：
- 变式题生成前端页面
- 作答→验证→推荐闭环流程
- 模板列表展示

---

### F-D3-2 — 变式题生成 API 数据库持久化 · `Planned`

**User Story**：作为用户，我希望我生成的变式题和作答记录能被保存，方便我回顾练习历史。

**Acceptance Criteria**：

- GIVEN 用户已登录且生成了变式题
- WHEN 变式题生成或作答完成
- THEN 生成的题目必须写入 questions 表，作答记录写入 mistakes 表
- AND 同一用户的历史变式题可按科目和知识点筛选查看

**核心技术实现点**：

1. 扩展 mistakes 表记录变式题作答（关联原题 question_id）
2. 在 `/problem-gen/generate` 和 `/validate` 中增加 DB 写入逻辑
3. 新增 `GET /api/v1/problem-gen/history` 端点返回用户练习历史

**交付物**：
- 变式题生成/作答结果持久化
- 练习历史查询 API

---

### F-D4-1 — AI 研友多角色对话页 · `Planned`

**User Story**：作为考研学生，我想和不同性格的 AI 研友一起讨论问题，比如让"学霸"出题考我，或和"努力型研友"互相鼓励。

**Acceptance Criteria**：

- GIVEN 用户从首页点击"AI 研友"入口
- WHEN 进入研友页
- THEN 应展示 3 种研友角色卡片（学霸/努力型/讨论型），每个卡片含角色介绍和擅长领域
- AND 用户选择角色后进入对话页，研友以该角色性格回复
- AND 对话页顶部显示当前角色标识和切换入口
- AND 支持 3 种模式：辩论模式/协作模式/测验模式，模式切换不丢失当前对话
- AND 会话结束时可查看讨论摘要

**核心技术实现点**：

1. 新建 `frontend/src/views/BuddyView.vue`（角色选择 + 对话页合体或分离）
2. 新增路由 `/buddy` 和 `/buddy/:sessionId`
3. 调用 `POST /api/v1/buddy/start`（指定角色和模式）
4. 调用 `POST /api/v1/buddy/{sessionId}/chat`（发送消息）
5. 调用 `GET /api/v1/buddy/{sessionId}`（恢复会话状态）
6. 调用 `POST /api/v1/buddy/{sessionId}/end`（结束会话）

**交付物**：
- AI 研友角色选择页
- 多角色对话页（含模式切换）
- 会话状态管理

---

### F-D4-2 — 代码实战完整化 · `Planned`

**User Story**：作为计算机考研学生，我想通过实际编码来巩固数据结构和算法知识，系统给出代码挑战，我编写代码后自动评测。

**Acceptance Criteria**：

- GIVEN 用户从首页点击"代码实战"入口
- WHEN 进入代码实战页
- THEN 应展示 4 种挑战类型卡片（补全/调试/追踪/设计），每种含难度和知识点标签
- AND 选择挑战后进入编码页：左侧题目描述 + 右侧代码编辑器（Monaco Editor 或简化版 textarea）
- AND 点击"提交"后调用代码执行 API，返回执行结果和评测反馈
- AND 可查看挑战的详细解析
- AND 已完成的挑战标记为已完成状态

**核心技术实现点**：

1. 重构 `frontend/src/views/CodeVisualView.vue` 或新建 `frontend/src/views/CodeChallengeView.vue`
2. 调用 `GET /api/v1/code/challenges`（挑战列表）
3. 调用 `GET /api/v1/code/challenges/{id}`（挑战详情）
4. 调用 `POST /api/v1/code/execute`（执行代码）
5. 调用 `POST /api/v1/code/{id}/submit`（提交答案评测）
6. 调用 `GET /api/v1/code/{id}/explanation`（查看解析）
7. 代码编辑器集成（Codemirror 或 Monaco 轻量版）

**交付物**：
- 代码挑战列表页
- 编码→执行→评测闭环页
- 解析查看功能

---

### F-D5-1 — 动态学习路径页 · `Planned`

**User Story**：作为学生，我希望系统基于我的薄弱点诊断结果，自动生成个性化的每日学习计划，我可以按计划推进并看到进度。

**Acceptance Criteria**：

- GIVEN 用户已完成薄弱点诊断
- WHEN 点击"学习路径"或从诊断页触发
- THEN 页面应展示时间线形式的学习路径，每日任务含：复习知识点、做题、总结
- AND 每个阶段标注预估时长和关联知识点
- AND 用户可点击"调整路径"修改学习节奏（如增加/减少每日任务量）
- AND 已完成的任务标记进度，总体进度条实时更新
- AND 路径可基于新诊断结果动态调整

**核心技术实现点**：

1. 新建 `frontend/src/views/LearningPathView.vue`
2. 新增路由 `/learning-path`
3. 调用 `POST /api/v1/learning-path/generate`（传入诊断报告 ID）
4. 调用 `POST /api/v1/learning-path/adjust`（调整学习节奏）
5. 时间线组件：阶段 → 任务 → 进度标记
6. 与 DiagnosisView 联动：诊断完成→一键生成路径

**交付物**：
- 学习路径可视化页（时间线 + 进度追踪）
- 路径调整交互
- 诊断→路径联动入口

---

### F-D5-2 — 思维过程可视化页 · `Planned`

**User Story**：作为学生，我希望看到自己在解题过程中的思维路径，知道在哪一步卡住了、哪一步走了弯路，帮助我改进思维方式。

**Acceptance Criteria**：

- GIVEN 用户完成了一次或多次苏格拉底式引导对话
- WHEN 点击"思维回放"入口
- THEN 页面应展示思维路径图：节点 = 思考步骤，边 = 步骤间的逻辑关系
- AND 标注关键节点类型：正确推理/思维跳跃/偏离/卡点
- AND 点击节点可展开该步骤的详细内容（原始对话片段）
- AND 提供思维成长报告：各维度（逻辑性/完整性/速度）趋势图
- AND 在对话页中实时显示当前情绪状态指示器（P2 降级为对话页内嵌小部件）

**核心技术实现点**：

1. 新建 `frontend/src/views/ThinkingTraceView.vue`
2. 新增路由 `/thinking/:sessionId`（单次思维回放）和 `/thinking/report`（成长报告）
3. 调用 `POST /api/v1/thinking/record`（对话中自动记录，已由 SocraticTutor 内部调用）
4. 调用 `GET /api/v1/thinking/{sessionId}/path`（路径图数据）
5. 调用 `GET /api/v1/thinking/{userId}/report`（成长报告）
6. 情绪指示器：调用 `GET /api/v1/emotion/{sessionId}/state`，在对话页底部显示情绪标签

**交付物**：
- 思维路径图可视化页
- 思维成长报告页
- 对话页情绪状态指示器（P2）

---

## 阶段 D6：端到端联调与沙箱集成

> 目标：打通所有前后端链路，补齐代码可视化沙箱，确保核心流程可端到端演示。

### F-D6-1 — Python 代码沙箱集成 · `Planned`

**User Story**：作为学生，我在代码实战中提交 Python 代码后，系统真实执行代码并返回结果，而不是返回硬编码的 mock 数据。

**Acceptance Criteria**：

- GIVEN 用户在代码实战页提交 Python 代码
- WHEN 调用 `POST /api/v1/visualize/execute`
- THEN 后端必须在沙箱中真实执行代码，返回执行结果（stdout/stderr）和步骤快照
- AND 代码执行超时限制 10 秒，超时返回 timeout 错误
- AND 禁止执行危险操作（os.system, subprocess, file write 等），违反时返回安全错误
- AND 代码可视化页的步骤播放器能基于返回的快照数据渲染

**核心技术实现点**：

1. 使用 Docker 隔离沙箱或 `RestrictedPython` 执行用户代码
2. 实现 `backend/app/sandbox/executor.py`（代码执行器）
3. 超时控制：`asyncio.wait_for(coro, timeout=10)`
4. 安全策略：AST 白名单过滤危险调用
5. 步骤快照生成：在关键行插入 print 语句记录变量状态
6. 替换 `/visualize/execute` 中的 mock 数据

**交付物**：
- Python 沙箱执行器
- 安全策略与超时控制
- 代码可视化 API 真实数据返回

---

### F-D6-2 — 核心链路端到端联调 · `Planned`

**User Story**：作为产品经理/评审，我希望以下核心用户旅程可以完整走通，不需要任何 mock 或后门。

**验收旅程清单**：

| 旅程 | 步骤 | 验收标准 |
|------|------|----------|
| **注册→登录→首页** | 注册→登录→跳转首页 | 用户信息正确显示，首页数据加载正常 |
| **拍照搜题→AI对话** | 上传图片→识别题目→进入苏格拉底引导→流式回复 | 题目识别准确，对话流式输出正常，RAG 检索生效 |
| **手写批改** | 上传草稿→AI批改→查看步骤评分→跳转引导订正 | 批改结果逐步骤展示，可跳转对话继续学习 |
| **薄弱点诊断→学习路径** | 触发诊断→查看雷达图→一键生成路径 | 诊断数据准确，路径生成基于诊断结果 |
| **举一反三** | 原题→变式题→作答→掌握度评估 | 变式题知识点关联正确，作答后评估准确 |
| **AI 研友** | 选角色→辩论/协作/测验→查看摘要 | 角色性格差异明显，对话流畅 |
| **代码实战** | 选挑战→编码→提交评测→查看解析 | 代码真实执行，评测结果准确 |

**核心技术实现点**：

1. 前后端联合调试所有 API 调用路径
2. 修复 CORS、请求/响应格式不一致问题
3. SSE 流式连接稳定性验证（断线重连）
4. 错误处理统一：前端 axios 拦截器 + 后端 HTTPException 格式统一
5. 加载状态与空状态 UI 兜底

**交付物**：
- 7 条核心旅程可完整演示
- Bug 列表（按 P0/P1/P2 分级）

---

### F-D6-3 — 图片上传至腾讯云 COS · `Planned`（P2）

**User Story**：作为用户，我上传的题目图片应该持久存储在云端，而不是在服务器本地。

**Acceptance Criteria**：

- GIVEN 腾讯云 COS 配置（SecretId/SecretKey/Bucket/Region）已填入环境变量
- WHEN 用户上传图片
- THEN 图片应上传至 COS，返回公网可访问 URL
- AND COS 不可用时自动降级为本地存储，不影响核心流程

**核心技术实现点**：

1. `backend/app/services/cos.py` 封装 COS SDK 上传
2. 降级策略：try COS → fallback 本地 → fallback base64
3. 配置项写入 `config.py`

**交付物**：
- COS 上传服务
- 降级策略与配置

---

## 阶段 D7：全面测试、Bug 修复与交付准备

> 目标：P0 Bug 清零，文档就绪，可进行正式演示和答辩。

### F-D7-1 — P0/P1 Bug 修复 · `Planned`

**User Story**：作为开发者，我希望在 D6 联调中发现的所有 P0 和 P1 级 Bug 在 D7 结束前全部修复。

**Acceptance Criteria**：

- GIVEN D6 联调 Bug 列表
- WHEN 所有 P0 Bug（功能完全不可用）和 P1 Bug（功能可用但体验严重受损）已修复
- THEN 7 条核心旅程必须全部走通无阻
- AND P2 Bug（体验瑕疵）至少修复 50%，剩余项记录为 known issues

**交付物**：
- Bug 修复记录
- 核心旅程回归测试通过

---

### F-D7-2 — 后端自动化测试 · `Planned`

**User Story**：作为开发者，我希望核心 API 端点有自动化测试覆盖，确保后续迭代不引入回归。

**Acceptance Criteria**：

- GIVEN 后端测试环境已配置
- WHEN 运行 `pytest backend/tests/`
- THEN 以下模块的测试用例必须通过：
  - 认证流程（注册/登录/token 验证/过期 token）
  - 核心业务（搜题/对话/批改/诊断）
  - 变式题生成与验证
  - AI 研友会话管理
- AND 测试覆盖率 ≥ 60%（核心业务模块）

**核心技术实现点**：

1. `pytest + httpx` 异步测试客户端
2. 测试数据库使用 SQLite 内存库或 MySQL test database
3. fixture: 测试用户、测试题目、mock LLM 响应
4. 关键测试场景：正常流程、边界条件、错误处理

**交付物**：
- `backend/tests/` 测试套件
- CI 可运行的测试脚本

---

### F-D7-3 — 文档定稿 · `Planned`

**User Story**：作为评审/答辩者，我希望项目的 README、API 文档和架构图完整且与代码一致。

**Acceptance Criteria**：

- `README.md` 必须包含：一键启动命令、功能清单、演示路径、已知限制、技术栈
- API 文档（Swagger `/docs`）所有端点描述完整，请求/响应 schema 准确
- 架构文档说明：6 大 Agent 调度链路、RAG 管线、情绪-教学联动机制
- 所有 `Planned` 状态在结项前必须改为 `Done`、`Deferred` 或 `Dropped`

**交付物**：
- 更新后的 `README.md`
- API 文档完善
- 架构设计文档

---

### F-D7-4 — 演示脚本与验收 · `Planned`

**User Story**：作为项目负责人，我希望有一份可执行的演示脚本，确保演示时不会出现意外。

**Acceptance Criteria**：

- 演示脚本必须覆盖 7 条核心旅程（见 F-D6-2）
- 每条旅程含：前置条件、操作步骤、预期结果
- 演示数据（seed data）已准备好，确保开箱可演示
- 5 分钟演示视频或实时演示无阻断

**交付物**：
- 演示脚本文档
- Seed 数据脚本
- 演示验证通过

---

## 每日时间线总览

| 日期 | 阶段 | 核心任务 | 交付物 | 验收标准 |
|------|------|----------|--------|----------|
| **D1** | 架构加固 | Alembic 迁移 + ORM 激活 + API DB 接入 | 迁移脚本 + CRUD 模块 + DB 连接池 | 5 张表创建，核心 API 从 DB 读写 |
| **D2** | 用户认证 | 注册/登录 API + JWT + 前端登录页 | Auth API + 前端登录/注册页 | 注册→登录→鉴权链路完整 |
| **D3** | 差异化前端 I | 举一反三页 + 变式题 DB 持久化 | ProblemGenView + 练习历史 | 变式题生成→作答→验证闭环 |
| **D4** | 差异化前端 II | AI 研友页 + 代码实战页 | BuddyView + CodeChallengeView | 研友对话 + 代码挑战可演示 |
| **D5** | 差异化前端 III | 学习路径页 + 思维可视化页 + 情绪指示器 | LearningPathView + ThinkingTraceView | 路径生成 + 思维回放可演示 |
| **D6** | 联调与沙箱 | 代码沙箱 + 7条核心旅程联调 + COS 上传 | 沙箱执行器 + 联调通过 | 全链路可演示，Bug 列表整理 |
| **D7** | 测试与交付 | Bug 修复 + 自动化测试 + 文档 + 演示准备 | 测试套件 + 文档 + 演示脚本 | P0 清零，核心旅程全通，可答辩 |

---

## 技术风险与降级策略

| 风险 | 影响 | 降级策略 |
|------|------|----------|
| LLM API 不稳定/超时 | 对话、批改、诊断等核心功能受阻 | 本地缓存常见回复 + 重试机制 + 超时提示 |
| ChromaDB 向量检索质量不佳 | RAG 检索结果不相关 | 降级为纯 BM25 检索 + 知识图谱补充 |
| Python 沙箱安全漏洞 | 代码实战功能不可用 | 使用预置执行结果 + 限制可用语言/库 |
| 腾讯云 COS 配置问题 | 图片上传失败 | 降级为本地存储 + base64 内联 |
| 前端页面开发时间不足 | 6 大差异化页面不完整 | 优先完成举一反三和 AI 研友（最差异化），其余用对话页内嵌 |
| 7 天时间紧迫 | 部分功能无法完成 | P2 功能（情绪可视化、COS、沙箱）可延后，P1 必须完成 |

---

## 核心技术实现点汇总

### 后端
1. **Alembic 迁移**：`alembic init` → `autogenerate` → `upgrade head`
2. **JWT 认证**：`python-jose` + `passlib[bcrypt]` + FastAPI `Depends`
3. **CRUD 封装**：SQLAlchemy 2.0 `select()` 风格 + async session
4. **代码沙箱**：Docker 隔离 / RestrictedPython + AST 白名单 + asyncio 超时
5. **COS 上传**：`cos-python-sdk-v5` + 降级策略

### 前端
1. **Auth 流程**：Pinia store + localStorage + axios interceptor + router guard
2. **变式题流程**：状态机（生成→作答→验证→推荐）
3. **AI 研友**：角色选择 + 模式切换 + 会话管理
4. **代码编辑器**：Codemirror/Monaco 轻量集成
5. **学习路径**：时间线组件 + 进度追踪 + ECharts 图表
6. **思维可视化**：路径图（Canvas/SVG）+ 节点交互 + 成长报告图表

### 联调
1. **SSE 稳定性**：EventSource 重连 + 心跳 + 错误边界
2. **错误统一**：后端 HTTPException → 前端 Toast 全局捕获
3. **加载状态**：Skeleton + Spinner + 空状态三件套
4. **响应式**：移动端底部导航 + 桌面端侧边栏，内容区居中适配
