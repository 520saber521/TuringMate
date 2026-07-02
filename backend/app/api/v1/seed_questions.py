"""Seed 408 exam questions into the database.

Run: python -m app.api.v1.seed_questions
"""
import sys
from app.models.database import SessionLocal
from app.crud.question import question_crud

SEED_DATA = [
    # === 数据结构 - 线性表 ===
    {"subject": "数据结构", "knowledge_tags": ["线性表", "链表操作"], "difficulty": 3,
     "year": 2010, "exam_paper": "2010年408真题", "chapter_order": 1, "source_type": "exam",
     "content": "设将 n (n>1) 个整数存放到一维数组 R 中。试设计一个在时间和空间两方面都尽可能高效的算法。将 R 中保存的序列循环左移 p (0<p<n) 个位置，即将 R 中的数据由 (X0, X1, ..., Xn-1) 变换为 (Xp, Xp+1, ..., Xn-1, X0, X1, ..., Xp-1)。",
     "solution_steps": [
         {"step_no": 1, "content": "将 R[0..p-1] 逆置", "hint": "reverse 函数的时间复杂度为 O(p/2)"},
         {"step_no": 2, "content": "将 R[p..n-1] 逆置", "hint": "reverse 函数的时间复杂度为 O((n-p)/2)"},
         {"step_no": 3, "content": "将整个 R[0..n-1] 逆置", "hint": "三次逆置后即可得到循环左移结果"},
     ]},
    {"subject": "数据结构", "knowledge_tags": ["线性表", "链表操作"], "difficulty": 3,
     "year": 2010, "exam_paper": "2010年408真题", "chapter_order": 2, "source_type": "exam",
     "content": "已知一个带有表头结点的单链表，结点结构为 (data, link)。假设该链表只给出了头指针 list。在不改变链表的前提下，请设计一个尽可能高效的算法，查找链表中倒数第 k 个位置上的结点（k 为正整数）。若查找成功，算法输出该结点的 data 域的值，并返回 1；否则，只返回 0。",
     "solution_steps": [
         {"step_no": 1, "content": "设置两个指针 p 和 q，初始都指向头结点", "hint": "双指针技巧"},
         {"step_no": 2, "content": "p 先向前走 k 步，若不足 k 步则返回 0", "hint": "检查链表长度"},
         {"step_no": 3, "content": "p 和 q 同步向前走，直到 p 到达表尾，此时 q 指向倒数第 k 个结点", "hint": "双指针保持 k 的距离差"},
     ]},

    # === 数据结构 - 树 ===
    {"subject": "数据结构", "knowledge_tags": ["二叉树性质与遍历", "哈夫曼树与编码"], "difficulty": 3,
     "year": 2011, "exam_paper": "2011年408真题", "chapter_order": 3, "source_type": "exam",
     "content": "已知一棵二叉树的前序遍历序列为 ABDCEGF，中序遍历序列为 BDAEGCF。请画出这棵二叉树，并给出其后序遍历序列。",
     "solution_steps": [
         {"step_no": 1, "content": "由前序第一个 A 确定根节点", "hint": "前序遍历：根→左→右"},
         {"step_no": 2, "content": "在中序序列中找到 A，左侧 BD 为左子树，右侧 EGCF 为右子树", "hint": "中序遍历：左→根→右"},
         {"step_no": 3, "content": "递归构建左右子树，得到完整的二叉树结构", "hint": "重复步骤1-2直到所有节点就位"},
     ]},

    # === 数据结构 - 图 ===
    {"subject": "数据结构", "knowledge_tags": ["最短路径"], "difficulty": 4,
     "year": 2012, "exam_paper": "2012年408真题", "chapter_order": 4, "source_type": "exam",
     "content": "已知带权有向图 G=(V,E)，其中 V={v1,v2,v3,v4,v5,v6}，请用 Dijkstra 算法求从 v1 到其余各顶点的最短路径，写出每一步 dist 数组的变化过程。",
     "solution_steps": [
         {"step_no": 1, "content": "初始化 dist=[0,∞,∞,∞,∞,∞]，S={v1}", "hint": "dist[v1]=0，其余为无穷大"},
         {"step_no": 2, "content": "每次从 V-S 中选择 dist 最小的顶点加入 S", "hint": "贪心策略"},
         {"step_no": 3, "content": "更新新加入顶点的邻接点的 dist 值", "hint": "松弛操作: dist[v] = min(dist[v], dist[u]+w(u,v))"},
     ]},

    # === 计组 - 数制 ===
    {"subject": "计组", "knowledge_tags": ["数制与编码", "定点数运算"], "difficulty": 3,
     "year": 2011, "exam_paper": "2011年408真题", "chapter_order": 1, "source_type": "exam",
     "content": "设机器字长为 8 位（含 1 位符号位），用补码运算规则计算下列各式，并判断是否溢出：\n(1) [x]补 + [y]补，其中 x = -85, y = 39\n(2) [x]补 - [y]补，其中 x = 52, y = -76",
     "solution_steps": [
         {"step_no": 1, "content": "将十进制转换为 8 位补码表示", "hint": "正数补码=原码，负数补码=反码+1"},
         {"step_no": 2, "content": "执行补码加法运算", "hint": "按位相加，符号位参与运算"},
         {"step_no": 3, "content": "根据进位和符号位判断是否溢出", "hint": "双高位判别法：Cs⊕Cp=1 则溢出"},
     ]},

    # === 计组 - 存储器 ===
    {"subject": "计组", "knowledge_tags": ["Cache映射与替换"], "difficulty": 4,
     "year": 2013, "exam_paper": "2013年408真题", "chapter_order": 2, "source_type": "exam",
     "content": "某计算机的 Cache 采用 4 路组相联映射方式，共有 64 行（块），每块大小为 128B。主存容量为 256MB。请回答：\n(1) Cache 共有多少组？\n(2) 主存地址中 tag、index、块内地址各占多少位？\n(3) 若访问地址为 0x12345，它映射到 Cache 的哪一组？",
     "solution_steps": [
         {"step_no": 1, "content": "计算组数 = Cache行数/路数 = 64/4 = 16组", "hint": "4路组相联"},
         {"step_no": 2, "content": "块内地址 = log2(128) = 7位；index = log2(16) = 4位；tag = 28-4-7 = 17位", "hint": "主存256MB需要28位地址"},
         {"step_no": 3, "content": "将0x12345转为二进制，提取index字段确定组号", "hint": "27位主存地址格式为 [tag:17][index:4][offset:7]"},
     ]},

    # === 操作系统 - 进程 ===
    {"subject": "操作系统", "knowledge_tags": ["进程同步"], "difficulty": 4,
     "year": 2014, "exam_paper": "2014年408真题", "chapter_order": 1, "source_type": "exam",
     "content": "有3个并发进程 P1、P2、P3，它们共享一个缓冲区 B。P1 负责将数据写入 B，P2 负责从 B 读取数据并加工，P3 负责将 P2 加工后的数据输出。请用 P/V 操作（信号量）实现这三个进程的同步。",
     "solution_steps": [
         {"step_no": 1, "content": "定义三个信号量: empty=1(缓冲区空), full1=0(数据已写入), full2=0(数据已加工)", "hint": "PV操作的经典生产者-消费者变体"},
         {"step_no": 2, "content": "P1: P(empty) → 写入B → V(full1)", "hint": "P操作申请资源，V操作释放资源"},
         {"step_no": 3, "content": "P2: P(full1) → 读取加工 → V(full2)", "hint": "P2既是消费者又是生产者"},
         {"step_no": 4, "content": "P3: P(full2) → 输出 → V(empty)", "hint": "P3消费处理后释放empty"},
     ]},

    # === 计算机网络 - TCP ===
    {"subject": "计算机网络", "knowledge_tags": ["TCP协议"], "difficulty": 4,
     "year": 2015, "exam_paper": "2015年408真题", "chapter_order": 1, "source_type": "exam",
     "content": "主机 A 向主机 B 发送一个长度为 100KB 的文件。假设 MSS=1KB，采用 TCP 拥塞控制的慢启动和拥塞避免算法。初始阈值为 16KB。请回答：\n(1) 在传输过程中，拥塞窗口的变化过程。\n(2) 若在第 8 个 RTT 时发生超时，新的阈值和拥塞窗口是多少？",
     "solution_steps": [
         {"step_no": 1, "content": "慢启动阶段: cwnd从1开始，每RTT翻倍，直到达到阈值16", "hint": "cwnd变化: 1→2→4→8→16"},
         {"step_no": 2, "content": "拥塞避免阶段: cwnd每次只增加1，线形增长", "hint": "cwnd变化: 16→17→18→19→..."},
         {"step_no": 3, "content": "超时后: 新阈值=当前cwnd/2, cwnd重置为1", "hint": "TCP Reno的处理方式"},
     ]},

    # 额外题目覆盖更多知识点
    {"subject": "数据结构", "knowledge_tags": ["交换排序（冒泡/快速）"], "difficulty": 2,
     "year": 2016, "exam_paper": "2016年408真题", "chapter_order": 5, "source_type": "exam",
     "content": "对序列 {49, 38, 65, 97, 76, 13, 27, 50} 进行快速排序，以第一个元素为基准，写出第一趟排序后的结果。",
     "solution_steps": [
         {"step_no": 1, "content": "选取 49 为基准 pivot", "hint": "通常选第一个元素为基准"},
         {"step_no": 2, "content": "从右往左找比49小的，从左往右找比49大的，然后交换", "hint": "双指针扫描"},
         {"step_no": 3, "content": "一趟结束后基准49归位，左小右大", "hint": "最终序列: {27,38,13,49,76,97,65,50}"},
     ]},
    {"subject": "计组", "knowledge_tags": ["指令流水线"], "difficulty": 4,
     "year": 2014, "exam_paper": "2014年408真题", "chapter_order": 3, "source_type": "exam",
     "content": "某 CPU 采用 5 级流水线（IF, ID, EX, MEM, WB），每级耗时分别为 10ns, 8ns, 10ns, 10ns, 8ns。流水线锁存器延迟为 1ns。求：(1) 流水线的时钟周期；(2) 执行 100 条指令的加速比。",
     "solution_steps": [
         {"step_no": 1, "content": "时钟周期 = max(各级耗时) + 锁存器延迟 = 10+1 = 11ns", "hint": "流水线时钟周期由最慢的一级决定"},
         {"step_no": 2, "content": "非流水线执行时间 = 100×(10+8+10+10+8) = 4600ns", "hint": "每条指令串行执行"},
         {"step_no": 3, "content": "流水线执行时间 = (5+99)×11 = 1144ns；加速比 = 4600/1144 ≈ 4.02", "hint": "5个周期填满流水线+99条指令各需1周期"},
     ]},
]

SUBJECT_NAMES = {
    "ds": "数据结构", "co": "计组", "os": "操作系统", "cn": "计算机网络",
}


def seed():
    db = SessionLocal()
    try:
        count = 0
        for item in SEED_DATA:
            q = question_crud.create(
                db,
                subject=item["subject"],
                content=item["content"],
                knowledge_tags=item.get("knowledge_tags", []),
                difficulty=item.get("difficulty", 3),
                solution_steps=item.get("solution_steps", []),
                year=item.get("year"),
                exam_paper=item.get("exam_paper", ""),
                chapter_order=item.get("chapter_order"),
                source_type=item.get("source_type", "manual"),
            )
            count += 1
            print(f"  [+] [{q.subject}] {q.content[:40]}... (year={q.year})")
        db.commit()
        print(f"\nSeed complete: {count} questions inserted.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
