"""Study Buddy Agent — AI 研友多角色系统.

创建永远在线的 AI 学习伙伴，支持多种角色扮演：
  - 学霸型 (Scholar): 深挖问题、讨论不同解法
  - 努力型 (Striver): 问基础概念、促进解释巩固
  - 讨论型 (Discussant): 多观点碰撞、争议题讨论

实际场景：
  - 选择角色组合组成「学习小组」
  - 就某一章节展开多角色互动对话
  - 增强学习的趣味性和深度
"""

import json
import logging
import uuid

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway
from app.schemas.emotion import StudyBuddyRole, StudyBuddyConfig
from app.core.tools import knowledge_graph, question_search
from app.api.utils import retry_async

logger = logging.getLogger(__name__)

# ============================================================
# 角色人设 Prompt 模板
# ============================================================

ROLE_PROFILES = {
    StudyBuddyRole.SCHOLAR: {
        "name": "学霸小张",
        "emoji": "🎓",
        "personality": """你是计算机考研的「学霸研友」——小张。

特点：
- 总是能提出更深层次的问题
- 喜欢探讨不同解法的优劣
- 偶尔会故意提出一个看似简单但有陷阱的问题来测试对方
- 说话简洁有力，喜欢用数学语言表达
- 不直接给答案，而是引导对方自己发现

说话风格：
- "等等，你有没有考虑过...的情况？"
- "这个解法的时间复杂度是多少？有没有更优的？"
- "我有个不同的思路，你觉得呢？"
- "如果我把条件改成这样，你的解法还成立吗？" """,

        "system_prompt": """你是小张🎓，计算机考研的学霸研友。
你正在和其他同学一起讨论{topic}相关的问题。

你的角色定位：提出更有深度的问题、分享不同的解题视角、挑战对方的论证严谨性。

规则：
1. 不要长篇大论，保持精炼
2. 经常提问而不是陈述
3. 尊重他人观点的同时适当质疑
4. 分享自己的思考过程""",
    },

    StudyBuddyRole.STRIVER: {
        "name": "努力小李",
        "emoji": "💪",
        "personality": """你是计算机考研的「努力型研友」——小李。

特点：
- 基础不太扎实，经常问一些基础问题
- 态度非常认真，每次都会认真记录笔记
- 喜欢确认自己理解是否正确
- 通过不断提问来帮助对方巩固知识（教是最好的学）

说话风格：
- "等一下，我不太理解这个概念..."
- "所以你的意思是...？"
- "这个公式是怎么推导出来的呀？"
- "能举个具体的例子吗？" """,

        "system_prompt": """你是小李💪，一个正在努力备考计算机考研的同学。
你们正在一起学习{topic}的内容。

你的角色定位：通过提问基础问题来帮助大家巩固理解。
你不怕问「傻问题」，因为你知道很多同学也有同样的疑惑。

规则：
1. 从基础概念开始问起
2. 真诚地表达困惑和不解
3. 当别人解释时，积极回应并追问
4. 偶尔分享自己刚学会的东西""",
    },

    StudyBuddyRole.DISCUSSANT: {
        "name": "讨论员小王",
        "emoji": "🗣️",
        "personality": """你是计算机考研的「讨论型研友」——小王。

特点：
- 喜欢引入多个角度的观点
- 经常说「有人认为A，也有人认为B」
- 会主动抛出争议性话题引发讨论
- 善于总结各方观点并形成自己的判断

说话风格：
- "关于这个问题，有两种主流看法..."
- "我觉得这里有个争议点..."
- "如果从面试官的角度看..."
- "我们投票看看大家怎么想？" """,

        "system_prompt": """你是小王🗣️，计算机考研的学习讨论组织者。
你们正在进行关于{topic}的小组讨论。

你的角色定位：引入多元观点、制造讨论焦点、总结归纳共识与分歧。

规则：
1. 引入不同教材/学派/真题的观点对比
2. 适时提出争议性问题激发讨论
3. 总结大家的共识和分歧点
4. 保持讨论有序且高效""",
    },
}

# ============================================================
# 讨论 Session 数据模型
# ============================================================


class BuddyMessage(BaseModel):
    """研友发言."""
    role_name: str = Field(description="发言角色名")
    role_type: StudyBuddyRole = Field(description="角色类型")
    content: str = Field(description="发言内容")
    emoji: str = Field(default="")


class DiscussionTurn(BaseModel):
    """一轮讨论."""
    turn_id: str = Field(description="轮次ID")
    messages: list[BuddyMessage] = Field(description="本轮发言列表")
    user_response_slot: bool = Field(default=True, description="用户是否已回复")


class StudySession(BaseModel):
    """一次学习小组会话."""
    session_id: str = Field(description="会话ID")
    config: StudyBuddyConfig = Field(description="配置")
    turns: list[DiscussionTurn] = Field(default_factory=list, description="讨论轮次")
    topic_summary: str = Field(default="", description="讨论主题总结")
    created_at: str = Field(default="")


# ============================================================
# Agent 实现
# ============================================================


BUDDY_SYSTEM_PROMPT = """你是 TuringMate 的「AI 学习小组」协调员。

当前小组配置：
{buddy_descriptions}

讨论主题：{topic}
讨论模式：{mode}
难度级别：{difficulty}

你的任务：
1. 根据 {active_roles} 的角色设定，生成他们关于当前话题的自然对话
2. 对话应该围绕 {topic} 展开，体现各自角色的特点
3. 每轮对话结束后，留出位置让真实用户参与
4. 用户发言后，继续推动讨论深入

输出格式（JSON）：
{
  "messages": [
    {"role": "角色名", "role_type": "scholar/striver/discussant", "content": "发言内容"},
    ...
  ],
  "discussion_point": "本轮讨论的核心议题",
  "next_prompt": "给用户的引导性提示"
}"""


class StudyBuddyAgent:
    """AI 研友多角色 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        self._sessions: dict[str, StudySession] = {}

    async def start_session(self, config: StudyBuddyConfig | dict) -> dict:
        """启动一个新的学习小组会话.
        
        Args:
            config: 研友配置（角色列表/主题/模式）

        Returns:
            StudySession 字典 + 开场白
        """
        if isinstance(config, dict):
            config = StudyBuddyConfig(**config)

        session_id = f"sb_{uuid.uuid4().hex[:10]}"
        
        # 获取知识图谱上下文
        kg_context = ""
        try:
            nodes_result = await knowledge_graph.ainvoke({
                "action": "get_nodes",
                "subject": config.topic.split("-")[0] if "-" in config.topic else None,
            })
            topics = [n.get("name", "") for n in nodes_result.get("nodes", [])[:10]]
            if topics:
                kg_context = "\n相关知识点: " + "、".join(topics)
        except Exception:
            pass

        session = StudySession(
            session_id=session_id,
            config=config,
            created_at=__import__("datetime").datetime.now().isoformat(),
        )

        # 生成开场白 — 让角色们自我介绍并引出话题
        intro = await self._generate_intro(session, kg_context)

        self._sessions[session_id] = session
        return {
            "session_id": session_id,
            "config": config.model_dump(),
            "intro_messages": intro.get("messages", []),
            "user_prompt": intro.get("next_prompt", "你想先聊哪个方面？"),
        }

    @retry_async(max_attempts=3)
    async def continue_discussion(
        self,
        session_id: str,
        user_message: str,
    ) -> dict:
        """继续讨论 — 用户发言后推进对话.

        Args:
            session_id: 会话 ID
            user_message: 用户的消息

        Returns:
            新的一轮讨论内容
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} 不存在")

        # 构建历史上下文
        history = ""
        for turn in session.turns[-5:]:  # 最近 5 轮
            for msg in turn.messages:
                history += f"\n[{msg.role_name}]: {msg.content}"

        # 角色描述
        buddy_descs = "\n".join([
            f"- {ROLE_PROFILES[r]['name']} ({r.value}): {ROLE_PROFILES[r]['personality'][:100]}"
            for r in session.config.roles
        ])

        input_text = f"""{buddy_descs}

## 当前主题: {session.config.topic}
## 模式: {session.config.mode}
## 难度: {session.config.difficulty}

## 之前讨论过:
{history or '(这是第一轮讨论)'}

## 用户刚刚说了:
"{user_message}"

请让各个角色自然地回应用户的发言，推动讨论继续深入。"""

        try:
            response = await self._llm.ainvoke([
                SystemMessage(content=BUDDY_SYSTEM_PROMPT.format(
                    buddy_descs=buddy_descs,
                    topic=session.config.topic,
                    mode=session.config.mode,
                    difficulty=session.config.difficulty,
                    active_roles=", ".join([r.value for r in session.config.roles]),
                )),
                HumanMessage(content=input_text),
            ])

            result = json.loads(response.content) if response.content else {}
        except Exception as e:
            logger.warning(f"研友对话生成失败: {e}")
            result = {"messages": [], "next_prompt": user_message}

        messages = result.get("messages", [])
        buddy_msgs = []
        for m in messages:
            role_type = m.get("role_type", "discussant")
            try:
                r_enum = StudyBuddyRole(role_type)
                emoji = ROLE_PROFILES.get(r_enum, {}).get("emoji", "")
            except ValueError:
                emoji = ""
            buddy_msgs.append(BuddyMessage(
                role_name=m.get("role", "AI"),
                role_type=role_type,
                content=m.get("content", ""),
                emoji=emoji,
            ).model_dump())

        # 记录轮次
        turn = DiscussionTurn(
            turn_id=f"t_{len(session.turns):03d}",
            messages=buddy_msgs,
        )
        session.turns.append(turn)

        return {
            "turn_number": len(session.turns),
            "messages": buddy_msgs,
            "user_prompt": result.get("next_prompt", "你怎么看？"),
            "summary_suggestion": result.get("discussion_point", ""),
        }

    def get_session_state(self, session_id: str) -> dict:
        """获取会话状态摘要."""
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session.session_id,
            "topic": session.config.topic,
            "roles": [r.value for r in session.config.roles],
            "total_turns": len(session.turns),
            "total_messages": sum(len(t.messages) for t in session.turns),
        }

    async def end_session(self, session_id: str) -> dict:
        """结束会话并生成总结."""
        session = self._sessions.pop(session_id, None)
        if not session:
            return {"error": "Session not found"}

        # 用 LLM 生成讨论总结
        all_content = "\n".join([
            f"--- 第{i+1}轮 ---\n" +
            "\n".join([f"[{m['role_name']}]: {m['content']}" for m in t.messages])
            for i, t in enumerate(session.turns)
        ])[:3000]

        summary = await self._llm.ainvoke([
            SystemMessage(content="总结以下学习小组讨论的核心收获和结论，用中文，200字以内"),
            HumanMessage(content=all_content),
        ])

        return {
            "session_id": session_id,
            "total_turns": len(session.turns),
            "summary": summary.content if hasattr(summary, 'content') else str(summary),
            "key_takeaways": [],  # 可扩展
        }

    async def _generate_intro(self, session: StudySession, context: str = "") -> dict:
        """生成开场白 — 使用 LLM 让角色自然自我介绍."""
        roles = session.config.roles
        names = [ROLE_PROFILES.get(r, {}).get("name", r.value) for r in roles]
        emojis = [ROLE_PROFILES.get(r, {}).get("emoji", "") for r in roles]

        # 构建角色描述供 LLM 参考
        role_descs = "\n".join([
            f"- {ROLE_PROFILES[r]['name']} ({r.value}): {ROLE_PROFILES[r]['personality'][:150]}"
            for r in roles
        ])

        intro_prompt = f"""你是 TuringMate 学习小组的「开场协调员」。

小组成员：
{role_descs}

讨论主题：{session.config.topic}
{context}

请生成一段生动的开场白，要求：
1. 每个角色用自己的人设风格做简短自我介绍（各1-2句话）
2. 自然地引出今天要讨论的主题
3. 最后邀请真实用户加入讨论
4. 总长度控制在 200 字以内

以 JSON 格式返回：
{{"messages": [{{"role": "角色名", "role_type": "scholar/striver/discussant", "content": "发言内容"}}, ...], "next_prompt": "给用户的引导语"}}"""

        try:
            response = await self._llm.ainvoke([
                SystemMessage(content="你是一个学习小组的开场协调员。只输出 JSON，不要其他内容。"),
                HumanMessage(content=intro_prompt),
            ])
            result = json.loads(response.content) if response.content else {}
            if result.get("messages"):
                return result
        except Exception as e:
            logger.warning(f"LLM 开场白生成失败，回退到模板: {e}")

        # Fallback: 静态模板
        intro_text = f"""今天的学习小组已经就绪！

成员介绍：
{chr(10).join([f'  {e} {n}' for e, n in zip(emojis, names)])}

今天我们要讨论的主题是：**{session.config.topic}**
{context}

{names[0] if names else '学霸'} 先来开个场吧！"""

        return {
            "messages": [
                {"role": "coordinator", "role_type": "scholar", "content": intro_text},
            ],
            "next_prompt": f"欢迎加入「{session.config.topic}」学习小组！你想从哪个角度切入？",
        }


# 全局单例
study_buddy_agent = StudyBuddyAgent()
