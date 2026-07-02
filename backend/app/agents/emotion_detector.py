"""Emotion Detector — 情绪感知与学习状态调节引擎.

在苏格拉底对话中实时检测学生情绪状态，
自动切换教学模式：
  - 沮丧 → 信心构建模式（推简单题+鼓励）
  - 疲劳 → 轻松复习模式（建议休息/知识卡片）
  - 走神 → 吸引注意力模式（趣味故事/轻松提醒）
  - 自信 → 挑战模式（加深难度）

实现策略（MVP）:
  1. 关键词检测（快速、可靠）
  2. 回答质量分析（长度/准确度变化趋势）
  3. 后续接入情感分析模型（精细版）
"""

import logging
import re
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from app.schemas.emotion import (
    EmotionState, TeachingMode,
    EmotionEvent, EmotionDetectionResult,
)

logger = logging.getLogger(__name__)

# ============================================================
# 情绪关键词规则库
# ============================================================

EMOTION_KEYWORDS: dict[EmotionState, list[tuple[float, list[str]]]] = {
    # (权重, 关键词正则列表) — 高权重关键词优先匹配
    EmotionState.FRUSTRATED: [
        (1.0, [r"烦死了", r"不想学了", r"太难受了", r"心态崩了"]),
        (0.9, [r"完全不会", r"根本不", r"一点都不会", r"太难了吧"]),
        (0.8, [r"不行了", r"放弃了", r"学不下去了", r"太菜了"]),
        (0.7, [r"好难", r"做不出来", r"想不出", r"卡住了.*很久"]),
        (0.5, [r"又错了", r"还是不对", r"总是错", r"又忘了"]),
    ],
    EmotionState.ANXIOUS: [
        (1.0, [r"来不及", r"来不及了", r"来不及复习", r"时间不够"]),
        (0.9, [r"考不上", r"考不上了", r"肯定挂", r"完蛋"]),
        (0.8, [r"紧张", r"焦虑", r"压力很大", r"担心"]),
        (0.6, [r"别人都", r"别人已经", r"差距太大"]),
    ],
    EmotionState.FATIGUED: [
        (1.0, [r"困了", r"好困", r"眼睛睁不开", r"想睡觉"]),
        (0.9, [r"累了", r"好累", r"坚持不住了", r"脑壳疼"]),
        (0.8, [r"看不进", r"看不进去", r"注意力集中不了"]),
        (0.6, [r"头昏", r"头痛", r"效率低"]),
    ],
    EmotionState.BORED: [
        (1.0, [r"无聊", r"没意思", r"枯燥", r"烦死了"]),
        (0.8, [r"走神了", r"在想别的事", r"不感兴趣"]),
        (0.6, [r"换个话题", r"讲个故事", r"有意思的吗"]),
    ],
    EmotionState.CONFIDENT: [
        (1.0, [r"懂了", r"明白了", r"很简单", r"轻松"]),
        (0.9, [r"我会", r"我知道", r"这个简单", r"没问题"]),
        (0.8, [r"原来如此", r"恍然大悟", r"一下子就"]),
        (0.6, [r"哈哈", r"nice", r"太好了", r"终于"]),
    ],
    EmotionState.EXCITED: [
        (1.0, [r"太酷了", r"好厉害", r"牛逼", r"绝了"]),
        (0.8, [r"有意思", r"好玩", r"喜欢这个", r"还想学"]),
        (0.6, [r"再来一题", r"继续", r"还有吗"]),
    ],
}

# ============================================================
# 教学模式映射
# ============================================================

EMOTION_TO_MODE: dict[EmotionState, TeachingMode] = {
    EmotionState.FRUSTRATED: TeachingMode.CONFIDENCE_BUILDING,
    EmotionState.ANXIOUS: TeachingMode.CONFIDENCE_BUILDING,
    EmotionState.FATIGUED: TeachingMode.RELAXED_REVIEW,
    EmotionState.BORED: TeachingMode.ENGAGEMENT,
    EmotionState.CONFIDENT: TeachingMode.CHALLENGE,
    EmotionState.EXCITED: TeachingMode.DEEP_DIVE,
    EmotionState.NEUTRAL: TeachingMode.NORMAL,
}

MODE_SYSTEM_PROMPT_OVERRIDES: dict[TeachingMode, str] = {
    TeachingMode.NORMAL: "",  # 使用默认 Prompt

    TeachingMode.CONFIDENCE_BUILDING: """
## 【当前模式：信心构建】⚠️
学生似乎遇到了挫折。请立即切换策略：
1. 先给予真诚的鼓励和认可
2. 把问题拆解成更小的、更容易的子问题
3. 推送一道他能轻松完成的同类基础题
4. 强调他已有的进步和能力
5. 避免使用挑战性语言
语气要温暖、耐心、充满支持。""",

    TeachingMode.RELAXED_REVIEW: """
## 【当前模式：轻松复习】😴
学生可能疲劳了。请切换到轻松模式：
1. 建议休息 3-5 分钟（喝口水、站起来走走）
2. 切换到「知识卡片」模式——用简短的问答代替长推理
3. 可以讲一个相关的趣味计算机小知识/历史故事来拉回注意力
4. 降低题目难度，减少单次互动的认知负荷
语气要轻松、幽默、不施压。""",

    TeachingMode.CHALLENGE: """
## 【当前模式：挑战模式】🔥
学生状态很好，自信满满！趁热打铁：
1. 提出更有深度的问题
2. 引导他尝试不同的解题思路
3. 给一道略高于当前水平的变式题
4. 讨论边界条件和优化可能性
5. 适度表扬但不要过度——保持进取心
语气要积极、有活力、带点挑战性。""",

    TeachingMode.ENGAGEMENT: """
## 【当前模式：吸引注意】👀
学生可能在走神。用以下方式重新吸引：
1. 用一个有趣的类比或现实场景引入
2. 讲一个与知识点相关的计算机历史趣事（如 Dijkstra 为什么发明该算法）
3. 提一个反直觉的问题引发好奇
4. 使用更生动活泼的语言
语气要轻松有趣、富有感染力。""",

    TeachingMode.DEEP_DIVE: """
## 【当前模式：深入探讨】🧠
学生对这个话题很兴奋，抓住机会深挖！
1. 探讨底层原理和设计动机
2. 比较不同方案的优劣
3. 引入扩展知识和前沿应用
4. 鼓励提出自己的见解和创新想法
5. 可以讨论面试/科研中的高级应用
语气要专业、热情、鼓励探索精神""",
}


@dataclass
class SessionEmotionState:
    """单个会话的情绪状态追踪."""
    session_id: str
    current_emotion: EmotionState = EmotionState.NEUTRAL
    current_mode: TeachingMode = TeachingMode.NORMAL
    history: deque = field(default_factory=lambda: deque(maxlen=50))
    consecutive_frustrated: int = 0   # 连续沮丧次数
    consecutive_fatigued: int = 0     # 连续疲劳次数
    mode_switches: int = 0            # 模式切换次数
    last_mode_switch_at: float = 0.0


class EmotionDetector:
    """情绪检测与教学策略调节器.

    使用方式:
      detector = EmotionDetector()
      result = detector.detect(user_message, session_id)
      prompt_override = detector.get_mode_prompt_override(session_id)
    """

    # 最大缓存会话数，防止长时间运行后内存泄漏
    MAX_SESSIONS = 200

    def __init__(self):
        # 会话状态缓存 {session_id: SessionEmotionState}
        self._sessions: dict[str, SessionEmotionState] = {}

    def detect(
        self,
        message_content: str,
        session_id: str,
    ) -> EmotionDetectionResult:
        """检测消息中的情绪状态.

        Args:
            message_content: 用户输入文本
            session_id: 会话 ID

        Returns:
            EmotionDetectionResult 包含检测结果和建议
        """
        content = message_content.strip() if message_content else ""
        if not content:
            return EmotionDetectionResult()

        best_match: tuple[EmotionState, float, list[str]] = (
            EmotionState.NEUTRAL, 0.0, []
        )

        # 遍历所有情绪类别，找到最佳匹配
        for emotion, rules in EMOTION_KEYWORDS.items():
            for weight, patterns in rules:
                matched_keywords = []
                for pat in patterns:
                    match = re.search(pat, content, re.IGNORECASE)
                    if match:
                        matched_keywords.append(match.group())

                if matched_keywords:
                    confidence = min(weight, 0.5 + weight * 0.1 * len(matched_keywords))
                    if confidence > best_match[1]:
                        best_match = (emotion, confidence, matched_keywords)

        emotion, confidence, triggers = best_match
        suggested_mode = EMOTION_TO_MODE.get(emotion, TeachingMode.NORMAL)

        # 更新会话状态
        state = self._ensure_session(session_id)
        prev_emotion = state.current_emotion
        state.current_emotion = emotion
        state.history.append((emotion, confidence, triggers))
        
        # 连续计数
        if emotion == EmotionState.FRUSTRATED:
            state.consecutive_frustrated += 1
        else:
            state.consecutive_frustrated = 0
        
        if emotion == EmotionState.FATIGUED:
            state.consecutive_fatigued += 1
        else:
            state.consecutive_fatigued = 0

        # 检测是否需要切换模式
        should_switch = self._should_switch_mode(state, emotion, prev_emotion)
        if should_switch:
            state.current_mode = suggested_mode
            state.mode_switches += 1
            state.last_mode_switch_at = time.time()

        result = EmotionDetectionResult(
            emotion=emotion,
            confidence=confidence,
            detected_by="keyword" if triggers else "neutral",
            triggers=triggers,
            suggested_mode=suggested_mode,
            adaptation_hints=self._get_hints(emotion),
        )

        return result

    def get_mode_prompt_override(self, session_id: str) -> str:
        """获取当前模式的 System Prompt 覆盖内容.

        返回追加到默认 system prompt 后面的模式指令。
        如果是 NORMAL 模式则返回空字符串。
        """
        state = self._sessions.get(session_id)
        if not state:
            return ""
        return MODE_SYSTEM_PROMPT_OVERRIDES.get(state.current_mode, "")

    def get_current_state(self, session_id: str) -> dict:
        """获取会话当前情绪状态的快照."""
        state = self._sessions.get(session_id)
        if not state:
            return {
                "emotion": "neutral", "mode": "normal",
                "consecutive_frustrated": 0, "consecutive_fatigued": 0,
                "mode_switches": 0,
            }
        return {
            "emotion": state.current_emotion.value,
            "mode": state.current_mode.value,
            "consecutive_frustrated": state.consecutive_frustrated,
            "consecutive_fatigued": state.consecutive_fatigued,
            "mode_switches": state.mode_switches,
            "history_length": len(state.history),
        }

    def get_session_events(self, session_id: str) -> list[dict]:
        """获取会话的情绪事件日志."""
        state = self._sessions.get(session_id)
        if not state:
            return []

        events = []
        for idx, (emotion, conf, triggers) in enumerate(state.history):
            events.append({
                "index": idx,
                "emotion": emotion.value if isinstance(emotion, EmotionState) else str(emotion),
                "confidence": round(conf, 2),
                "triggers": triggers,
            })
        return events

    def reset_session(self, session_id: str) -> None:
        """重置会话状态（会话结束时调用）."""
        self._sessions.pop(session_id, None)

    # ── 内部方法 ───────────────────────────────────────────

    def _ensure_session(self, session_id: str) -> SessionEmotionState:
        if session_id not in self._sessions:
            # 防止无限增长：超出上限时淘汰最旧的会话
            if len(self._sessions) >= self.MAX_SESSIONS:
                oldest_key = next(iter(self._sessions))
                del self._sessions[oldest_key]
            self._sessions[session_id] = SessionEmotionState(session_id=session_id)
        return self._sessions[session_id]

    def _should_switch_mode(
        self,
        state: SessionEmotionState,
        new_emotion: EmotionState,
        prev_emotion: EmotionState,
    ) -> bool:
        """判断是否需要切换教学模式."""
        # 同一情绪不需要重复切换
        if new_emotion == prev_emotion:
            return False

        # 冷却时间：避免频繁切换（至少间隔 3 条消息）
        elapsed = time.time() - state.last_mode_switch_at
        if elapsed < 30 and state.mode_switches > 0:  # 30秒冷却
            return False

        # 中度及以上非中性情绪才触发切换
        strong_emotions = {
            EmotionState.FRUSTRATED, EmotionState.ANXIOUS,
            EmotionState.FATIGUED, EmotionState.BORED,
            EmotionState.CONFIDENT, EmotionState.EXCITED,
        }
        return new_emotion in strong_emotions

    @staticmethod
    def _get_hints(emotion: EmotionState) -> list[str]:
        hints_map = {
            EmotionState.FRUSTRATED: [
                "降低题目难度，推送一道基础巩固题",
                "先给予鼓励，再拆解问题",
                "回顾之前做对的类似题目建立信心",
            ],
            EmotionState.ANXIOUS: [
                "帮助学生分解目标，制定短期可达成的计划",
                "强调已取得的进展",
                "避免讨论竞争/排名等压力源话题",
            ],
            EmotionState.FATIGUED: [
                "建议休息 3-5 分钟",
                "切换到知识卡片模式（轻量问答）",
                "讲一个趣味计算机故事放松一下",
            ],
            EmotionState.BORED: [
                "引入趣味类比或真实案例",
                "讲述相关的计算机历史故事",
                "提出反直觉的问题激发好奇心",
            ],
            EmotionState.CONFIDENT: [
                "增加题目难度",
                "引导学生尝试多种解法",
                "讨论边界条件和优化方案",
            ],
            EmotionState.EXCITED: [
                "深入探讨原理和设计思想",
                "介绍扩展知识和前沿应用",
                "鼓励探索性思考和自主创新",
            ],
        }
        return hints_map.get(emotion, [])


# 全局单例
emotion_detector = EmotionDetector()
