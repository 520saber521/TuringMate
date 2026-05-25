"""Problem Generator Agent — 「举一反三」题目生成器.

核心差异化:
  - 不只讲一道题，而是消灭一类题
  - 基于知识图谱的参数化题目生成
  - 做完变式题后验证掌握程度
  - 通过则在思维漏洞图谱标记「已掌握」

架构:
  1. 输入: 题目 + 知识点 + 错误记录
  2. 匹配题目模板（或 LLM 生成模板）
  3. 参数化替换，生成 3 道变式题
  4. 学生完成后判定掌握状态

MVP 策略:
  - 内置常见题型模板库（链表/树/排序/图/OS/计组/网络）
  - LLM 辅助生成非模板题目的变式
"""

import json
import logging
import uuid
import random

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway
from app.core.tools import question_search, knowledge_graph
from app.api.utils import retry_async
from app.schemas.problem_gen import (
    ProblemTemplate, GeneratedProblem,
    MasteryValidation, DifficultyLevel,
)

logger = logging.getLogger(__name__)


# ── 内置题目模板库 (MVP) ───────────────────────────────────

BUILTIN_TEMPLATES = [
    # === 数据结构 ===
    {
        "template_id": "ds_linkedlist_reverse",
        "subject": "数据结构", "topic": "链表反转",
        "original_question": "编写一个函数，反转一个单链表。",
        "template_text": "给定一个包含 {{n}} 个节点的单链表，头节点为 head，请将该链表{{variant}}。要求：空间复杂度为 O(1)。",
        "parameters": {
            "n": {"type": "int", "range": [5, 20], "description": "节点数"},
            "variant": {"type": "enum", "values": ["反转", "每 k 个一组反转", "从位置 m 到 n 反转"],
                        "description": "变体"},
        },
        "constraints": ["n > k if variant involves k", "1 <= m <= n if variant involves m,n"],
        "solution_template": "使用迭代/递归方式遍历链表，逐个修改指针方向",
        "difficulty": "medium",
    },
    {
        "template_id": "ds_bst_lca",
        "subject": "数据结构", "topic": "二叉搜索树",
        "original_question": "在二叉搜索树中找到两个节点的最近公共祖先。",
        "template_text": "给定一棵包含 {{n}} 个节点的二叉{{tree_type}}树，以及两个节点值 {{val1}} 和 {{val2}}，请找出它们的最近公共祖先(LCA)。假设所有节点值唯一。",
        "parameters": {
            "n": {"type": "int", "range": [7, 30], "description": "节点数"},
            "tree_type": {"type": "enum", "values": ["搜索", "普通"], "description": "树类型"},
            "val1": {"type": "int", "range": [1, 100], "description": "节点值1"},
            "val2": {"type": "int", "range": [1, 100], "description": "节点值2"},
        },
        "constraints": ["val1 != val2", "val1和val2都存在于树中"],
        "solution_template": "BST利用大小关系递归查找；普通树需要后序DFS或存储父路径",
        "difficulty": "medium",
    },
    {
        "template_id": "ds_quicksort_pivot",
        "subject": "数据结构", "topic": "快速排序",
        "original_question": "分析快速排序在最好/最坏情况下的时间复杂度。",
        "template_text": "对数组 arr = [{{array_vals}}] 执行{{pivot_strategy}}快速排序：\n(a) 给出第一趟划分后的结果\n(b) 分析该情况下快速排序的时间复杂度\n(c) 如何优化以避免最坏情况？",
        "parameters": {
            "array_vals": {"type": "list_int", "count_range": [8, 12], "range": [0, 100], "description": "数组元素"},
            "pivot_strategy": {"type": "enum",
                               "values": ["首元素作为基准", "尾元素作为基准", "三数取中法", "随机选取"],
                               "description": "基准选择策略"},
        },
        "constraints": [],
        "solution_template": "根据 pivot 策略执行 partition 操作；分析递归深度",
        "difficulty": "hard",
    },

    # === 操作系统 ===
    {
        "template_id": "os_page_replacement",
        "subject": "操作系统", "topic": "页面置换算法",
        "original_question": "在一个分页系统中，分别用 FIFO、LRU、Optimal 算法计算页面置换次数。",
        "template_text": "一个进程有 {{num_frames}} 个页框，访问串为：{{ref_string}}。\n请分别用以下页面置换算法计算缺页中断次数和缺页率：\n(1) FIFO\n(2) LRU（最近最少使用）\n(3) Clock（改进型CLOCK）",
        "parameters": {
            "num_frames": {"type": "int", "range": [3, 5], "description": "页框数"},
            "ref_string": {"type": "list_int", "count_range": [12, 20],
                           "range": [1, 8], "description": "页面访问串"},
        },
        "constraints": ["ref_string 中元素值不超过 num_frames * 2"],
        "solution_template": "模拟各算法的页面置换过程，统计缺页次数",
        "difficulty": "hard",
    },
    {
        "template_id": "os_process_sync",
        "subject": "操作系统", "topic": "进程同步",
        "original_question": "使用 PV 操作解决生产者-消费者问题。",
        "template_text": "有一个缓冲区，大小为 {{buffer_size}}，有 {{n_producers}} 个生产者和 {{n_consumers}} 个消费者。生产者每次生产一个产品放入缓冲区，消费者每次取走一个产品。请用信号量(PV操作)实现正确的同步互斥机制，并说明：(1) 需要哪些信号量？初值多少？ (2) 完整的伪代码。",
        "parameters": {
            "buffer_size": {"type": "int", "range": [5, 10], "description": "缓冲区大小"},
            "n_producers": {"type": "int", "range": [1, 3], "description": "生产者数量"},
            "n_consumers": {"type": "int", "range": [1, 3], "description": "消费者数量"},
        },
        "constraints": [],
        "solution_template": "mutex=1, empty=N, full=0; P/V 操作正确配对",
        "difficulty": "medium",
    },

    # === 计算机组成原理 ===
    {
        "template_id": "co_float_rep",
        "subject": "计组", "topic": "浮点数表示",
        "original_question": "将十进制浮点数转换为 IEEE 754 单精度格式。",
        "template_text": "将十进制数 {{decimal_num}} 表示为 IEEE 754 单精度浮点数（32位）：\n(1) 写出二进制表示\n(2) 指出符号位、阶码、尾数的值\n(3) 如果该数乘以 {{multiplier}}，结果如何变化？",
        "parameters": {
            "decimal_num": {"type": "float", "range": [-1000, 1000],
                            "description": "十进制数", "step": 0.125},
            "multiplier": {"type": "enum", "values": ["2", "4", "0.5", "-1"],
                           "description": "乘数因子"},
        },
        "constraints": ["decimal_num 不能为 0", "decimal_num 必须能精确表示或近似表示"],
        "solution_template": "转换二进制 → 规格化 → 计算偏置阶码 → 填入 32 位格式",
        "difficulty": "medium",
    },
    {
        "template_id": "co_cache_mapping",
        "subject": "计组", "topic": "Cache 映射",
        "original_question": "某 Cache 采用组相联映射方式，计算命中率和地址映射。",
        "template_text": "一个主存容量为 {{mem_size}}KB 的系统采用 Cache，参数如下：\n- Cache 大小: {{cache_size}}KB\n- 块大小: {{block_size}}B\n- 映射方式: {{mapping_way}} 路组相联\n\n地址流: {{addr_stream}}\n求：(1) Cache 共多少行？多少组？ (2) 初始全空时的命中率？ (3) 标记字段几位？",
        "parameters": {
            "mem_size": {"type": "int", "values": [64, 128, 256, 512], "description": "主存容量KB"},
            "cache_size": {"type": "int", "values": [8, 16, 32, 64], "description": "Cache容量KB"},
            "block_size": {"type": "int", "values": [16, 32, 64, 128], "description": "块大小B"},
            "mapping_way": {"type": "enum", "values": [2, 4, 8], "description": "组相联路数"},
            "addr_stream": {"type": "hex_list", "count_range": [10, 16],
                            "description": "十六进制地址流"},
        },
        "constraints": ["cache_size >= block_size * mapping_way"],
        "solution_template": "计算行数=Cache大小/块大小，组数=行数/路数；模拟地址映射",
        "difficulty": "hard",
    },

    # === 计算机网络 ===
    {
        "template_id": "cn_subnetting",
        "subject": "计算机网络", "topic": "子网划分",
        "original_question": "对一个 IP 地址进行子网划分，计算子网掩码、可用地址范围等。",
        "template_text": "某公司获得一个 {{ip_class}} 类地址块 {{network_addr}}/{{prefix_len}}，需要划分为 {{num_subnets}} 个子网，每个子网至少容纳 {{hosts_per_subnet}} 台主机。\n请给出：(1) 子网掩码 (2) 各子网的网络地址和广播地址 (3) 可用主机IP范围 (4) 地址利用率",
        "parameters": {
            "ip_class": {"type": "enum", "values": ["A", "B", "C"], "description": "地址类别"},
            "network_addr": {"type": "ip", "description": "网络地址"},
            "prefix_len": {"type": "int", "range": [8, 28], "description": "前缀长度"},
            "num_subnets": {"type": "int", "range": [2, 8], "description": "子网数量"},
            "hosts_per_subnet": {"type": "int", "range": [5, 200], "description": "每子网主机数"},
        },
        "constraints": ["prefix_len <= 32 - ceil(log2(hosts_per_subnet+2))"],
        "solution_template": "借位划分子网；计算新掩码、网络地址、广播地址、可用范围",
        "difficulty": "medium",
    },
    {
        "template_id": "cn_tcp_congestion",
        "subject": "计算机网络", "topic": "TCP 拥塞控制",
        "original_question": "分析 TCP 拥塞控制窗口的变化过程。",
        "template_text": "TCP 连接的 MSS={{mss}}, 初始拥塞窗口 cwnd={{init_cwnd}}, 慢开始门限 ssthresh={{ssthresh}}, 接收窗口 rwnd=无限大。\n前 {{n_rounds}} 轮传输中，依次发生了以下事件：{{events}}。\n请画出 cwnd 随时间变化的曲线图，标注出慢开始、拥塞避免、快重传、快恢复等阶段。",
        "parameters": {
            "mss": {"type": "int", "values": [1, 2, 4], "description": "最大报文段"},
            "init_cwnd": {"type": "int", "values": [1, 2, 4], "description": "初始cwnd"},
            "ssthresh": {"type": "int", "range": [8, 64], "description": "慢开始门限"},
            "n_rounds": {"type": "int", "range": [10, 20], "描述": "轮数"},
            "events": {"type": "text_list", "description": "事件列表如 ['第3轮超时', '第7轮收到3个重复ACK']"},
        },
        "constraints": ["init_cwnd <= ssthresh"],
        "solution_template": "按事件逐步更新 cwnd 和 ssthresh；画分段线性图",
        "difficulty": "hard",
    },
]


class ProblemGeneratorInput(BaseModel):
    """题目生成请求."""
    original_question: str = Field(description="原题内容")
    topic: str = Field(description="知识点")
    subject: str = Field(default="", description="科目")
    count: int = Field(default=3, description="生成变式题数量", ge=1, le=5)
    difficulty: str = Field(default="medium", description="目标难度")


class GeneratedProblemsOutput(BaseModel):
    """LLM 结构化输出 — 生成的变式题."""
    problems_json: str = Field(
        description='''JSON 数组，每个题目:
        [{"content": "完整题目文本", "expected_answer": "答案要点",
          "hint": "提示", "difficulty": "easy|medium|hard"}]'''
    )
    mastery_check_plan: str = Field(
        description="""如何判断学生是否掌握：
        说明做完这3道题后如何评估掌握程度"""
    )


GENERATOR_SYSTEM_PROMPT = """你是 TuringMate 的「举一反三」题目生成专家。

你的任务是：基于学生做错的一道题，生成 **同类型但不同参数/场景** 的变式练习题。

## 原则：

### 1. 变式而不变心
- 保持考查的知识点和能力要求一致
- 改变具体数值、场景描述、约束条件
- 可以适度增加难度梯度（第1道简单→第3道较难）

### 2. 保证可解性
- 每道生成的题目必须有确定答案
- 参数要满足基本约束条件（不能出现负数长度、空集合等）
- 如果涉及公式，确保数值代入后有合理解

### 3. 覆盖常见陷阱
- 在变式中自然嵌入该知识点的典型易错点
- 例如：边界条件、特殊情况、概念混淆点

## 输出格式：
返回 JSON 数组，包含 {count} 道变式题，每道题要有：
- content: 完整题目文本（可直接给学生做）
- expected_answer: 答案要点（用于批改参考）
- hint: 提示（学生卡住时显示）
- difficulty: easy / medium / hard"""


class ProblemGeneratorAgent:
    """「举一反三」题目生成器 Agent."""

    def __init__(self):
        self._llm = llm_gateway.get_chat_model()
        self._structured_llm = self._llm.with_structured_output(GeneratedProblemsOutput)
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", GENERATOR_SYSTEM_PROMPT),
            ("human", "{input}"),
        ])

    async def generate_variants(
        self,
        original_question: str,
        topic: str,
        subject: str = "",
        count: int = 3,
        difficulty: str = "medium",
    ) -> dict:
        """基于原题生成变式练习题.

        Args:
            original_question: 原始题目文本
            topic: 知识点名称
            subject: 科目名称
            count: 生成数量 (1-5)
            difficulty: 目标难度

        Returns:
            {"problems": [...], "mastery_check_plan": "..."}
        """
        logger.info(f"ProblemGen: 生成变式题 - topic={topic}, count={count}")

        # 1. 先尝试匹配内置模板
        template = self._find_template(topic, subject)

        if template:
            problems = self._generate_from_template(template, count)
        else:
            # 2. 无匹配模板时用 LLM 生成
            problems = await self._generate_with_llm(
                original_question, topic, subject, count, difficulty
            )

        return {
            "problems": [p.model_dump() for p in problems],
            "mastery_check_plan": (
                f"完成全部{len(problems)}道变式题后："
                f"全部通过 → 「{topic}」已掌握；"
                f"部分错误 → 继续强化薄弱子项"
            ),
            "source_template_id": template.template_id if template else "llm_generated",
        }

    async def validate_mastery(
        self,
        topic: str,
        attempt_results: list[dict],
    ) -> dict:
        """根据做题结果判定掌握程度.

        Args:
            topic: 知识点
            attempt_results: [
                {"problem_id": "...", "passed": true/false, "time_seconds": 120},
                ...
            ]

        Returns:
            MasteryValidation 字典
        """
        total = len(attempt_results)
        passed = sum(1 for r in attempt_results if r.get("passed"))

        is_mastered = total > 0 and (passed / total) >= 0.67  # 2/3 通过率
        confidence = passed / max(total, 1)

        feedback_parts = []
        if is_mastered:
            feedback_parts.append(f"太棒了！你通过了 {passed}/{total} 道变式题，「{topic}」已掌握！")
            feedback_parts.append("思维漏洞图谱已更新：该知识点标记为 ✓ 已掌握")
        elif passed == total - 1:
            feedback_parts.append(f"差一点点！{total-1} 道通过，还有 1 道小问题。")
            feedback_parts.append("建议回顾一下那道题的知识点，再试一次。")
        else:
            weak_items = [r for r in attempt_results if not r.get("passed")]
            feedback_parts.append(f"「{topic}」还需加强，通过了 {passed}/{total} 道。")
            feedback_parts.append(f"重点复习出错的地方：共 {len(weak_items)} 处需要巩固。")

        next_rec = (
            "可以进入下一个知识点学习了！" if is_mastered
            else f"建议针对「{topic}」再做一轮强化练习后再继续"
        )

        return MasteryValidation(
            validation_id=f"mv_{uuid.uuid4().hex[:8]}",
            topic=topic,
            problems_attempted=total,
            problems_passed=passed,
            is_mastered=is_mastered,
            confidence_score=round(confidence, 2),
            feedback="\n".join(feedback_parts),
            next_recommendation=next_rec,
        ).model_dump()

    # ── 内部方法 ───────────────────────────────────────────

    def _find_template(self, topic: str, subject: str) -> ProblemTemplate | None:
        """从内置模板库匹配."""
        best_match = None
        best_score = 0

        for tmpl_data in BUILTIN_TEMPLATES:
            score = 0
            if topic and topic in tmpl_data["topic"]:
                score += 2
            if subject and subject in tmpl_data.get("subject", ""):
                score += 1
            if score > best_score:
                best_score = score
                best_match = tmpl_data

        if best_match:
            return ProblemTemplate(**best_match)
        return None

    def _generate_from_template(
        self, template: ProblemTemplate, count: int
    ) -> list[GeneratedProblem]:
        """从模板实例化生成题目."""
        problems = []
        params_def = template.parameters

        for i in range(count):
            param_values = {}
            for pname, pdef in params_def.items():
                param_values[pname] = self._sample_param(pdef, i)

            # 替换模板中的占位符
            content = template.template_text
            for pname, val in param_values.items():
                content = content.replace(f"{{{{{pname}}}}}", str(val))

            hint = self._build_hint(template.topic, i, count)
            diff = DifficultyLevel.MEDIUM
            if i == 0 and count > 1:
                diff = DifficultyLevel.EASY
            elif i == count - 1 and count > 1:
                diff = DifficultyLevel.HARD

            problems.append(GeneratedProblem(
                problem_id=f"pg_{uuid.uuid4().hex[:8]}",
                source_template_id=template.template_id,
                content=content,
                parameter_values=param_values,
                expected_answer=template.solution_template,
                hint=hint,
                difficulty=diff,
                topic=template.topic,
                subject=template.subject,
            ))

        return problems

    @retry_async(max_attempts=3, delay=0.5)
    async def _generate_with_llm(
        self, question: str, topic: str, subject: str,
        count: int, difficulty: str,
    ) -> list[GeneratedProblem]:
        """LLM 生成变式题（无匹配模板时）."""
        input_text = f"""## 原始题目
{question}

## 知识点
- 科目: {subject or '未指定'}
- 知识点: {topic}

## 要求
- 生成 {count} 道同类型变式练习题
- 目标难度: {difficulty}
- 每道题都要有不同的参数或场景"""

        try:
            chain = self._prompt | self._structured_llm
            output: GeneratedProblemsOutput = await chain.ainvoke({"input": input_text})

            raw_problems = json.loads(output.problems_json)
            problems = []
            for idx, rp in enumerate(raw_problems[:count]):
                diff_map = {"easy": DifficultyLevel.EASY, "medium": DifficultyLevel.MEDIUM,
                            "hard": DifficultyLevel.HARD}
                problems.append(GeneratedProblem(
                    problem_id=f"pg_llm_{idx}_{uuid.uuid4().hex[:6]}",
                    source_template_id="llm_generated",
                    content=rp.get("content", ""),
                    parameter_values={},
                    expected_answer=rp.get("expected_answer", ""),
                    hint=rp.get("hint", ""),
                    difficulty=diff_map.get(rp.get("difficulty", "medium"), DifficultyLevel.MEDIUM),
                    topic=topic,
                    subject=subject,
                ))
            return problems
        except Exception as e:
            logger.error(f"LLM 生成变式题失败: {e}")
            return [GeneratedProblem(
                problem_id=f"pg_fallback_{i}",
                source_template_id="fallback",
                content=f"[{topic}] 变式练习题 {i+1}",
                parameter_values={},
                expected_answer="",
                hint="请尝试运用所学知识解答",
                difficulty=DifficultyLevel.MEDIUM,
                topic=topic,
                subject=subject,
            ) for i in range(count)]

    @staticmethod
    def _sample_param(param_def: dict, variant_idx: int = 0):
        """根据参数定义采样一个值."""
        ptype = param_def.get("type", "int")

        if ptype == "int":
            lo, hi = param_def.get("range", [1, 20])
            return random.randint(lo, hi) + variant_idx

        elif ptype == "float":
            lo, hi = param_def.get("range", [0.0, 100.0])
            step = param_def.get("step", 0.125)
            val = random.uniform(lo, hi)
            return round(val / step) * step

        elif ptype == "enum":
            values = param_def.get("values", [])
            if not values:
                return param_def.get("description", "")
            return values[(variant_idx) % len(values)]

        elif ptype == "list_int":
            cnt_range = param_def.get("count_range", [8, 12])
            val_range = param_def.get("range", [0, 100])
            cnt = random.randint(*cnt_range)
            return [random.randint(*val_range) for _ in range(cnt)]

        elif ptype == "hex_list":
            cnt_range = param_def.get("count_range", [10, 16])
            cnt = random.randint(*cnt_range)
            return [f"{random.randint(0x1000, 0xFFFF):04X}" for _ in range(cnt)]

        elif ptype == "text_list":
            return param_def.get("description", "").split("; ")

        elif ptype == "ip":
            return f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"

        elif ptype == "string":
            return param_def.get("description", "")

        # 未知类型返回描述信息，避免模板中出现 "None" 字符串
        logger.warning(f"未知参数类型: {ptype}, param={param_def.get('description', '')}")
        return param_def.get("description", "") or f"[{ptype}]"

    @staticmethod
    def _build_hint(topic: str, index: int, total: int) -> str:
        hints = [
            f"回忆一下「{topic}」的核心概念再动手",
            f"注意边界条件哦",
            f"提示：画个图可能更清楚",
            f"这是第 {index+1}/{total} 题，加油！",
        ]
        return hints[min(index, len(hints) - 1)]


# 全局单例
problem_generator = ProblemGeneratorAgent()
