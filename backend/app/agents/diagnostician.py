"""Diagnostician Agent - 薄弱点诊断 Agent.

分析用户的错题记录模式，
结合 LLM 生成四科能力评估和薄弱点报告。
MVP 阶段使用预设数据分析 + LLM 生成报告。
"""

import logging
import json
import re

from app.core.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)

DIAGNOSIS_SYSTEM_PROMPT = """你是 TuringMate 的408计算机考研诊断专家，根据学生的练习数据分析薄弱环节。

基于以下学生数据生成诊断报告：

错题记录摘要：
{mistake_summary}

请输出 JSON 格式（不要输出其他文字）：
{
  "scores": {
    "数据结构": 分数(0-100),
    "计组": 分数(0-100),
    "操作系统": 分数(0-100),
    "网络": 分数(0-100)
  },
  "weak_points": [
    {
      "subject": "科目名",
      "topic": "薄弱知识点",
      "score": 掌握度(0-100),
      "description": "具体问题描述"
    }
  ],
  "recommendations": [
    {
      "type": "专项练习/知识点回顾/真题演练",
      "title": "推荐标题",
      "count": 数量
    }
  ]
}

要求：
1. scores 反映四科整体掌握程度
2. weak_points 列出2-4个最需要加强的知识点
3. recommendations 给出3-5条针对性建议
4. 分数要合理，不要全部偏高或偏低
"""


class DiagnosticianAgent:
    """诊断 Agent - 分析错题模式，生成薄弱点报告."""

    def __init__(self):
        self.llm = llm_gateway

    async def generate_report(self, user_id: str) -> dict:
        """生成诊断报告.

        Args:
            user_id: 用户 ID

        Returns:
            四科分数 + 薄弱知识点列表 + 练习推荐
        """
        # TODO: 从数据库获取真实错题记录
        # MVP 阶段使用模拟数据
        mistake_summary = self._get_mock_mistake_summary(user_id)

        messages = [
            {"role": "system", "content": DIAGNOSIS_SYSTEM_PROMPT.format(mistake_summary=mistake_summary)},
            {"role": "user", "content": "请根据我的练习数据生成薄弱点诊断报告。"},
        ]

        try:
            logger.info(f"Diagnostician: 开始生成报告 - user={user_id}")
            raw_response = await self.llm.chat(messages, temperature=0.5)
            logger.info(f"Diagnostician: LLM 响应长度: {len(raw_response)}")

            parsed = self._extract_json(raw_response)

            # 确保必要字段存在
            parsed.setdefault("user_id", user_id)
            parsed.setdefault("scores", {"数据结构": 70, "计组": 65, "操作系统": 75, "网络": 60})
            parsed.setdefault("weak_points", [])
            parsed.setdefault("recommendations", [])

            # 校验 scores 包含四科
            for subject in ["数据结构", "计组", "操作系统", "网络"]:
                parsed["scores"].setdefault(subject, 70)

            # 校验 weak_points 结构
            for wp in parsed.get("weak_points", []):
                wp.setdefault("subject", "数据结构")
                wp.setdefault("topic", "未知知识点")
                wp.setdefault("score", 50)
                wp.setdefault("description", "需要加强练习")

            # 校验 recommendations 结构
            for rec in parsed.get("recommendations", []):
                rec.setdefault("type", "专项练习")
                rec.setdefault("title", "推荐练习")
                rec.setdefault("count", 5)

            return parsed

        except Exception as e:
            logger.warning(f"Diagnostician: LLM 调用失败 ({e})，使用 fallback")
            return self._generate_fallback_report(user_id)

    def _get_mock_mistake_summary(self, user_id: str) -> str:
        """获取模拟错题摘要（MVP 阶段）."""
        return """该学生近期练习情况：
- 数据结构：链表操作错误3次，树遍历错误2次，排序算法错误1次
- 计组：流水线冒险判断错误4次，Cache映射错误2次
- 操作系统：进程调度算法选择错误1次，死锁判断错误1次
- 网络：TCP拥塞控制错误5次，IP子网划分错误3次

总计错题22题，正确率约68%"""

    def _extract_json(self, text: str) -> dict:
        """从 LLM 响应中提取 JSON."""
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        logger.warning(f"Diagnostician: 无法解析JSON，原文前200字: {text[:200]}")
        return {}

    def _generate_fallback_report(self, user_id: str) -> dict:
        """Fallback 报告."""
        return {
            "user_id": user_id,
            "scores": {"数据结构": 72, "计组": 65, "操作系统": 78, "网络": 58},
            "weak_points": [
                {
                    "subject": "计算机网络",
                    "topic": "TCP拥塞控制",
                    "score": 45,
                    "description": "慢开始、拥塞避免、快重传的阈值变化规律掌握不牢",
                },
                {
                    "subject": "计算机组成原理",
                    "topic": "流水线冒险",
                    "score": 52,
                    "description": "数据冒险、控制冒险的解决策略混淆",
                },
            ],
            "recommendations": [
                {"type": "专项练习", "title": "TCP 拥塞控制专项训练", "count": 10},
                {"type": "知识点回顾", "title": "流水线冒险机制详解", "count": 1},
            ],
        }


diagnostician = DiagnosticianAgent()
