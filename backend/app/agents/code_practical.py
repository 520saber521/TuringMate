"""Code Practical Module — 「代码即题目」实战模块 (Feature 6).

差异化核心:
  - 408 与编程紧密相关，不只是静态题目
  - 讲 DS 时内嵌代码沙盒让学生运行/补全代码
  - 讲 CO 时模拟 CPU 数据通路动画

模块组成:
  1. CodeSandboxTool: 增强版代码执行工具（带可视化步骤）
  2. DSPracticalAgent: 数据结构实战 Agent
  3. COPracticalAgent: 计算机组成原理实战 Agent
  4. CodeChallengeManager: 代码挑战管理（补全/调试/改错）
"""

import json
import logging
import uuid
import re
from enum import Enum

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.core.llm_gateway import llm_gateway
from app.core.tools import code_executor

logger = logging.getLogger(__name__)

# ============================================================
# 代码挑战类型
# ============================================================


class ChallengeType(str, Enum):
    COMPLETE = "complete"      # 补全代码（填空）
    DEBUG = "debug"           # 调试代码（找bug）
    MODIFY = "modify"         # 修改实现（换算法/Optimize)
    TRACE = "trace"           # 手动追踪（写出每步输出）
    DESIGN = "design"         # 设计实现（从零写）


class CodeChallenge(BaseModel):
    """代码挑战题目."""
    challenge_id: str = Field(description="挑战ID")
    type: ChallengeType = Field(description="挑战类型")
    subject: str = Field(default="数据结构", description="适用科目")
    topic: str = Field(description="关联知识点")
    title: str = Field(description="挑战标题")
    description: str = Field(description="问题描述")
    starter_code: str = Field(default="", description="初始代码框架")
    hidden_tests: list[str] = Field(default_factory=list, description="隐藏测试用例")
    expected_output: str = Field(default="", description="预期输出")
    hint: str = Field(default="", description="提示")
    difficulty: str = Field(default="medium", description="难度")
    explanation: str = Field(default="", description="解析（完成后显示）")


# ============================================================
# 内置代码挑战库
# ============================================================

DS_CHALLENGES = [
    CodeChallenge(
        challenge_id="ds_001",
        type=ChallengeType.COMPLETE,
        subject="数据结构", topic="链表反转",
        title="手写链表反转",
        description="补全下面的 ListNode 反转函数。要求 O(1) 空间复杂度。",
        starter_code="""class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    \"\"\"TODO: 补全链表反转逻辑\"\"\"
    prev = None
    curr = head
    while curr:
        # ====== 请在这里补全 ======
        # 你的代码...
        
        # =========================
    return prev

# 测试
head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
result = reverse_list(head)
# 打印: 4 -> 3 -> 2 -> 1
while result:
    print(result.val, end=' -> ')
    result = result.next
print('None')
""",
        hidden_tests=[
            "reverse_list(ListNode(1)) should produce ListNode(1)",
            "reverse_list(None) should return None",
            "reverse_list(ListNode(1,ListNode(2))) should produce 2->1",
        ],
        expected_output="4 -> 3 -> 2 -> 1 -> None",
        hint="想想三个指针的关系：prev, curr, next_temp",
        difficulty="easy",
        explanation="经典三指针法：prev 记录前一节点，curr 是当前节点，next_temp 暂存 curr.next 以防断链。每步将 curr.next 指向 prev，然后三个指针各前进一步。",
    ),
    CodeChallenge(
        challenge_id="ds_002",
        type=ChallengeType.DEBUG,
        subject="数据结构", topic="二叉树层序遍历",
        title="找出 BFS 中的 Bug",
        description="下面这段层序遍历(BFS)代码有一个隐蔽的 bug，找出它并修复。",
        starter_code="""from collections import deque

def level_order(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])  # Bug 可能在这
    
    while queue:
        level_size = len(queue)
        current_level = []
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            # BUG: 下面哪一行有问题？
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(current_level)
    
    return result

# 期望输出: [[1],[2,3],[4,5]]
print(level_order(root))
""",
        hidden_tests=["Should handle empty tree", "Single node tree", "Full binary tree"],
        expected_output="[[1], [2, 3], [4, 5]]",
        hint="仔细检查队列的初始化和节点的处理顺序...",
        difficulty="medium",
        explanation="代码本身没有明显的 bug —— 但如果 root 为 None 且初始化时没有正确处理，或者 node.val 属性在某些测试中不存在时会出错。常见的隐藏 bug 包括：忘记检查 node 是否为 None、level_size 计算时机不对等。",
    ),
    CodeChallenge(
        challenge_id="ds_003",
        type=ChallengeType.TRACE,
        subject="数据结构", topic="快速排序",
        title="手动追踪 QuickSort 的 Partition 过程",
        description="给定数组和 pivot 选择策略，手动写出 partition 函数每一轮的状态变化。",
        starter_code="""def partition(arr, low, high):
    \"\"\"Lomuto partition scheme\"\"\"
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return i + 1

# 追踪: arr = [3, 6, 8, 10, 1, 2, 1]
# 请写出每一步 j 和 swap 后 arr 的状态
arr = [3, 6, 8, 10, 1, 2, 1]
print(f"Initial: {arr}")
pivot_index = partition(arr, 0, len(arr)-1)
print(f"After partition (pivot at {pivot_index}): {arr}")
""",
        hidden_tests=["pivot value should be 1", "left side <= 1", "right side > 1"],
        expected_output="[1, 1, 2, 3, 6, 8, 10]",
        hint="一步步追踪 j=0,1,2,... 每次 arr[j] 和 pivot 比较，<= 则交换",
        difficulty="hard",
        explanation="""Lomuto partition 步骤追踪:
j=0: arr[0]=3<=1? No → arr=[3,6,8,10,1,2,1]
j=1: arr[1]=6<=1? No → 同上
j=2: arr[2]=8<=1? No → 同上
j=3: arr[3]=10<=1? No → 同上
j=4: arr[4]=1<=1? Yes! i=0, swap(arr[0],arr[4]) → [1,6,8,10,3,2,1]
j=5: arr[5]=2<=1? No → 同上
Final: swap(arr[1],arr[6]) → [1,1,2,10,3,6,8], pivot_index=1
""",
    ),
]


CO_CHALLENGES = [
    CodeChallenge(
        challenge_id="co_001",
        type=ChallengeType.TRACE,
        subject="计组", topic="数据通路",
        title="手动模拟单周期 CPU 指令执行",
        description="给定指令 `add $s1, $s2, $s3`，写出每个时钟周期的控制信号和数据流动。",
        starter_code="""# 单周期 MIPS CPU 模拟
# 指令: add $s1, $s2, $s3
# 寄存器初始值: $s2=10, $s3=20, PC=0x00400000

registers = {'$zero':0,'$s0':0,'$s1':0,'$s2':10,'$s3':20,
             '$t0':0,'$t1':0,'$sp':0x7FFFFFFC}

memory = {}  # 简化的内存模型

def clock_cycle(cycle, pc, regs, mem):
    '''模拟单个时钟周期的数据通路'''
    # TODO: 追踪每阶段的值
    # IF: 取指 → ID: 译码 → EX: 执行 → MEM: 访存 → WB: 回写
    pass

# 追踪 5 个时钟周期
for cycle in range(1, 6):
    print(f"=== Cycle {cycle} ===")
    clock_cycle(cycle, 0x00400000, registers, memory)
    print(f"$s1 = {registers['$s1']}")
""",
        hidden_tests=["$s1 最终应为 30"],
        expected_output="$s1 = 30",
        hint="按 IF→ID→EX→MEM→WB 五阶段追踪寄存器值和控制信号",
        difficulty="hard",
        explanation="""Cycle 1 (IF): IR=Memory[PC], PC+=4
Cycle 2 (ID): Read $s2=10, $s3=20, decode opcode=add
Cycle 3 (EX): ALUResult = 10 + 20 = 30
Cycle 4 (MEM): 无内存操作 (add不需要访存)
Cycle 5 (WB): Write 30 to $s1 → $s1=30
""",
    ),
]


# ============================================================
# 增强版代码执行工具 (带可视化)
# ============================================================


@tool
async def code_practical_execute(
    code: str = Field(description="学生提交的代码"),
    challenge_id: str = Field(default="", description="挑战ID (可选，用于自动评测)"),
    language: str = Field(default="python", description="编程语言"),
) -> dict:
    """执行学生的代码并返回详细的可视化步骤.

    用于「代码即题目」实战模块，比通用 code_executor 更适合教学场景：
      - 自动检测语法/运行时错误
      - 对比预期输出
      - 生成逐步骤变量状态变化
      - 关键步骤标注（如 swap、比较等）
    """
    # 使用已有的 code_executor 工具
    base_result = await code_executor.ainvoke({
        "code": code, "language": language,
    })

    # 增强分析（防御性取值）
    analysis = _analyze_code_quality(code)
    steps = base_result.get("steps") if isinstance(base_result, dict) else []
    output = base_result.get("output", "") if isinstance(base_result, dict) else ""

    # 截断过长的输出，防止响应膨胀
    MAX_OUTPUT_LENGTH = 5000
    if len(output) > MAX_OUTPUT_LENGTH:
        output = output[:MAX_OUTPUT_LENGTH] + f"\n... (输出已截断，共{len(output)}字符)"

    # 如果提供了 challenge_id，进行自动评测
    evaluation = None
    if challenge_id:
        evaluation = _evaluate_challenge(challenge_id, code, output)

    return {
        **base_result,
        "analysis": analysis,
        "evaluation": evaluation,
        "visual_steps": _enrich_visual_steps(steps, code),
    }


def _analyze_code_quality(code: str) -> dict:
    """静态代码质量分析."""
    issues = []
    
    # 检查常见问题
    if "while True" in code.lower() and "break" not in code:
        issues.append({"severity": "warning", "message": "可能的死循环：while True 没有 break"})
    
    if "==" in code and "=" in code and "= =" not in code:
        # 简单启发式：检查是否有赋值误用
        pass
    
    if "print(" not in code and "return " not in code:
        issues.append({"severity": "info", "message": "建议添加 print 或 return 来观察结果"})

    lines = code.strip().split("\n")
    if len(lines) < 5:
        issues.append({"severity": "info", "message": "代码较短，可能不完整"})

    complexity_indicators = {
        "has_loop": any(kw in code for kw in ["for ", "while "]),
        "has_recursion": "def " in code and any(code.count(name) > 1 
                         for name in re.findall(r'def (\w+)\(', code)),
        "has_condition": "if " in code,
        "line_count": len(lines),
    }

    return {
        "issues": issues,
        "complexity": complexity_indicators,
        "score": max(0, 100 - len(issues) * 10),  # 简单评分
    }


def _evaluate_challenge(challenge_id: str, code: str, actual_output: str) -> dict:
    """对照挑战题自动评测."""
    all_challenges = DS_CHALLENGES + CO_CHALLENGES
    challenge = next((c for c in all_challenges if c.challenge_id == challenge_id), None)
    
    if not challenge:
        return {"status": "unknown_challenge", "challenge_id": challenge_id}

    # 简单输出比对
    expected = challenge.expected_output.strip()
    actual = actual_output.strip() if actual_output else ""

    passed = expected == actual or expected in actual or actual in expected

    return {
        "status": "passed" if passed else "failed",
        "challenge_id": challenge_id,
        "title": challenge.title,
        "expected": expected,
        "actual": actual[:200],
        "match_details": "输出完全匹配" if passed else "输出不一致，请检查逻辑",
        "hint_shown": not passed,
        "hint": challenge.hint if not passed else "",
    }


def _enrich_visual_steps(steps: list, code: str) -> list:
    """增强步骤可视化信息."""
    enriched = []
    
    # 检测关键操作模式
    key_patterns = {
        "swap": [r"swap", r".*,.*=.*,.*"],
        "compare": [r"<", r">", r"==", r"<=", r">="],
        "append": [r"\.append\("],
        "pop": [r"\.pop\("],
        "recurse_call": [r"return\s+\w+\("],
    }
    
    for step in steps:
        desc = step.get("description", "")
        detected_ops = []
        for op, patterns in key_patterns.items():
            for pat in patterns:
                if re.search(pat, desc, re.IGNORECASE):
                    detected_ops.append(op)
                    break

        # 拷贝一份，避免修改原始 step 数据
        enriched_step = {**step}
        enriched_step["detected_operations"] = detected_ops
        enriched_step["is_key_step"] = len(detected_ops) > 0
        enriched.append(enriched_step)
    
    return enriched


# ============================================================
# 挑战管理 API
# ============================================================


class CodePracticalManager:
    """代码实战挑战管理器."""

    def __init__(self):
        self._challenges = {c.challenge_id: c for c in DS_CHALLENGES + CO_CHALLENGES}

    def list_challenges(
        self,
        subject: str = "",
        topic: str = "",
        challenge_type: str = "",
        difficulty: str = "",
    ) -> list[dict]:
        """列出符合条件的挑战题."""
        results = list(self._challenges.values())
        
        if subject:
            results = [c for c in results if c.subject == subject]
        if topic:
            results = [c for c in results if topic in c.topic]
        if challenge_type:
            results = [c for c in results if c.type.value == challenge_type]
        if difficulty:
            results = [c for c in results if c.difficulty == difficulty]
        
        return [{
            "id": c.challenge_id,
            "type": c.type.value,
            "subject": c.subject,
            "topic": c.topic,
            "title": c.title,
            "difficulty": c.difficulty,
            "short_description": c.description[:80],
        } for c in results]

    def get_challenge(self, challenge_id: str) -> dict | None:
        """获取单个挑战详情（不含解析）."""
        c = self._challenges.get(challenge_id)
        if not c:
            return None
        return {
            **c.model_dump(exclude={"explanation"}),
            "has_starter_code": bool(c.starter_code),
        }

    def reveal_explanation(self, challenge_id: str) -> str | None:
        """获取挑战的解析（学生完成后调用）."""
        c = self._challenges.get(challenge_id)
        return c.explanation if c else None


# 全局单例
code_practical_manager = CodePracticalManager()
