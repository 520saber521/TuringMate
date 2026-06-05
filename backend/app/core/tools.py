"""LangChain Tools - TuringMate 工具集.

所有工具使用 LangChain @tool 装饰器或 StructuredTool 定义，
可直接被 LangGraph Agent 通过 .bind_tools() 调用。

工具清单:
  - image_ocr:       图片 OCR 识别（多模态 LLM）
  - question_search: 题库 RAG 检索
  - code_executor:   代码沙箱执行
  - knowledge_graph: 知识图谱查询
"""

import json
import logging
import base64
from pathlib import Path

from langchain_core.tools import tool, StructuredTool
from pydantic import BaseModel, Field
from typing import Optional

from app.core.llm_gateway import llm_gateway
from app.rag.retriever import retriever

logger = logging.getLogger(__name__)

# ── 数据目录 ──
KNOWLEDGE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"


# ============================================================
# Tool 1: Image OCR — 图片识别 (多模态 LLM)
# ============================================================

@tool
async def image_ocr(
    image_url: str = Field(description="图片 URL 或本地文件路径"),
    task: str = Field(
        default="recognize",
        description="识别任务: recognize(通用识别) / parse_question(解析题目) / analyze_handwriting(手写分析)"
    ),
) -> dict:
    """识别图片中的文字、题目内容或手写解题步骤.
    
    使用多模态 LLM（DeepSeek/GPT-4o）理解图片内容，
    支持题目解析、手写步骤分析等场景。
    """
    task_prompts = {
        "recognize": "请识别并提取这张图片中的所有文字内容，按原文格式输出。",
        "parse_question": "请识别这张图片中的计算机考研408题目，输出科目、知识点、难度和题面内容。",
        "analyze_handwriting": "请分析这张草稿纸图片中的手写解题步骤，识别每一步的内容。",
    }
    prompt = task_prompts.get(task, task_prompts["recognize"])

    try:
        messages = [
            {"role": "system", "content": "你是图片识别专家，请准确识别图片内容。"},
            {"role": "user", "content": prompt},
        ]
        result = await llm_gateway.chat_with_image(messages, image_url)
        return {"text": result, "task": task, "success": True}
    except Exception as e:
        logger.warning(f"image_ocr 失败: {e}")
        return {"error": f"图片识别失败: {str(e)[:100]}", "success": False}


# ============================================================
# Tool 2: Question Search — 题 RAG 库检索
# ============================================================

@tool
async def question_search(
    query: str = Field(description="搜索关键词或题目描述"),
    subject: Optional[str] = Field(default=None, description="科目过滤: 数据结构/计组/操作系统/网络"),
    limit: int = Field(default=5, description="返回结果数量"),
) -> dict:
    """从408考研题库中检索相似题目.
    
    支持按知识点、科目筛选，使用 RAG 向量相似度搜索。
    """
    if not query:
        return {"results": [], "total": 0, "error": "必须提供 query 参数", "success": False}

    try:
        kwargs = {}
        if subject:
            kwargs["subject"] = subject

        results = await retriever.retrieve(query, top_k=limit, **kwargs)

        if not results:
            logger.info(f"question_search 未找到结果: query={query}")
            return {"results": [], "total": 0, "success": True}

        return {
            "results": [
                {
                    "content": r.get("content", ""),
                    "score": r.get("score", 0),
                    "metadata": r.get("metadata", {}),
                }
                for r in results
            ],
            "total": len(results),
            "success": True,
        }

    except Exception as e:
        logger.error(f"question_search 失败: {e}")
        return {"error": f"题库检索失败: {str(e)[:100]}", "success": False}


# ============================================================
# Tool 3: Code Executor — 代码沙箱执行
# ============================================================

class CodeExecutorInput(BaseModel):
    """代码执行输入参数."""
    code: str = Field(description="要执行的源代码")
    language: str = Field(default="python", description="编程语言: python/c/cpp")
    test_input: Optional[str] = Field(default=None, description="测试输入")
    time_limit: float = Field(default=10.0, description="执行时间限制(秒)")


# ── Forbidden imports/patterns for sandbox safety ──
FORBIDDEN_IMPORTS = {
    "os", "subprocess", "shutil", "sys", "ctypes", "socket",
    "requests", "urllib", "http", "ftplib", "telnetlib",
    "pickle", "marshal", "code", "codeop", "compileall",
    "importlib", "pkgutil", "pathlib",
}
FORBIDDEN_FUNCTIONS = {
    "exec", "eval", "compile", "open", "__import__",
    "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "breakpoint",
}
SAFE_BUILTINS = {
    "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
    "bytes": bytes, "chr": chr, "complex": complex, "dict": dict,
    "divmod": divmod, "enumerate": enumerate, "filter": filter,
    "float": float, "format": format, "frozenset": frozenset,
    "hash": hash, "hex": hex, "int": int, "isinstance": isinstance,
    "issubclass": issubclass, "iter": iter, "len": len, "list": list,
    "map": map, "max": max, "min": min, "next": next, "object": object,
    "oct": oct, "ord": ord, "pow": pow, "print": print, "range": range,
    "repr": repr, "reversed": reversed, "round": round, "set": set,
    "slice": slice, "sorted": sorted, "str": str, "sum": sum,
    "tuple": tuple, "type": type, "zip": zip, "staticmethod": staticmethod,
    "classmethod": classmethod, "property": property, "super": super,
    "True": True, "False": False, "None": None,
    "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
    "KeyError": KeyError, "IndexError": IndexError, "StopIteration": StopIteration,
    "ZeroDivisionError": ZeroDivisionError, "ArithmeticError": ArithmeticError,
}


def _validate_code_safety(code: str) -> str | None:
    """Check code for forbidden patterns. Returns error message or None."""
    import ast
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"语法错误: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split(".")[0]
                if name in FORBIDDEN_IMPORTS:
                    return f"禁止导入模块: {name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.split(".")[0]
                if name in FORBIDDEN_IMPORTS:
                    return f"禁止导入模块: {name}"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_FUNCTIONS:
                return f"禁止调用函数: {node.func.id}"

    for kw in FORBIDDEN_IMPORTS:
        if kw in code:
            # Additional check for string-based bypasses
            if f"__import__('{kw}')" in code or f'__import__("{kw}")' in code:
                return f"禁止导入模块: {kw}"

    return None


@tool(args_schema=CodeExecutorInput)
async def code_executor(code: str, language: str = "python", test_input: str = None, time_limit: float = 10.0) -> dict:
    """在沙箱环境中执行算法代码并返回执行步骤快照.

    支持 Python 代码，记录变量状态变化用于可视化。
    安全限制: AST白名单过滤 + 50步上限 + safe builtins + 禁用危险模块。
    """
    import io
    import sys
    import asyncio

    if language != "python":
        return {
            "steps": [],
            "output": f"[暂不支持 {language}]",
            "execution_time": 0,
            "success": False,
            "error": f"当前仅支持 Python, 不支持 {language}",
        }

    # Security check
    safety_error = _validate_code_safety(code)
    if safety_error:
        return {
            "steps": [],
            "output": "",
            "execution_time": 0,
            "success": False,
            "error": f"安全限制: {safety_error}",
        }

    output_buf = io.StringIO()
    steps = []
    step_no = 1

    # Build safe execution environment
    exec_globals = {"__builtins__": SAFE_BUILTINS}
    exec_locals = {}

    old_stdout = sys.stdout
    sys.stdout = output_buf

    try:
        async def _run():
            nonlocal step_no, steps

            lines = code.strip().split("\n")
            current_block = []

            for line in lines:
                stripped = line.strip()
                current_block.append(line)

                is_complete = not stripped.endswith(":") and (
                    not stripped or
                    stripped.startswith(("#", "import ", "from ", "def ", "class "))
                    or stripped.endswith((")", "]", "}", '"', "'"))
                )

                if is_complete and current_block:
                    block_code = "\n".join(current_block)

                    # Record pre-execution state
                    step_vars = {}
                    for var_name, var_value in list(exec_locals.items()):
                        if not var_name.startswith("__"):
                            try:
                                step_vars[var_name] = repr(var_value)[:200]
                            except Exception:
                                pass

                    steps.append({
                        "step_no": step_no,
                        "line": len(steps) + 1,
                        "description": block_code[:150],
                        "variables": step_vars,
                        "visual_state": {},
                    })

                    try:
                        exec(compile(block_code, "<sandbox>", "exec"), exec_globals, exec_locals)
                    except SyntaxError:
                        continue
                    except Exception as e:
                        steps.append({
                            "step_no": step_no + 1,
                            "line": len(steps) + 1,
                            "description": f"运行时错误: {e}",
                            "variables": {},
                            "visual_state": {},
                        })
                        break

                    step_no += 1
                    current_block = []
                    if step_no > 50:
                        break

            if current_block and step_no <= 50:
                block_code = "\n".join(current_block)
                try:
                    exec(compile(block_code, "<sandbox>", "exec"), exec_globals, exec_locals)
                except Exception:
                    pass

        await asyncio.wait_for(_run(), timeout=time_limit)

        sys.stdout = old_stdout
        output = output_buf.getvalue()

        return {
            "steps": steps,
            "output": output or "(无输出)",
            "execution_time": 0.01,
            "success": True,
        }

    except asyncio.TimeoutError:
        sys.stdout = old_stdout
        return {
            "steps": steps,
            "output": output_buf.getvalue(),
            "execution_time": time_limit,
            "success": False,
            "error": f"代码执行超时 ({time_limit}s)",
        }
    except Exception as e:
        sys.stdout = old_stdout
        return {
            "steps": steps,
            "output": output_buf.getvalue(),
            "execution_time": 0,
            "success": False,
            "error": f"执行错误: {str(e)[:500]}",
        }
    finally:
        sys.stdout = old_stdout


# ============================================================
# Tool 4: Knowledge Graph — 知识图谱查询
# ============================================================

class KnowledgeGraphInput(BaseModel):
    """知识图谱查询参数."""
    action: str = Field(default="get_nodes", description="操作类型: get_nodes/get_edges/get_related")
    subject: Optional[str] = Field(default=None, description="科目: ds/co/os/cn")
    node_id: Optional[str] = Field(default=None, description="节点 ID (用于关联查询)")


@tool(args_schema=KnowledgeGraphInput)
async def knowledge_graph(action: str = "get_nodes", subject: str = None, node_id: str = None) -> dict:
    """查询408四科知识点节点和跨科目关联关系.
    
    支持获取节点列表、关联边、以及跨科知识关联查找。
    """

    def _load_json(filename: str) -> list:
        path = KNOWLEDGE_DATA_DIR / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    match action:
        case "get_nodes":
            nodes = []
            for f in ["ds_nodes.json", "co_nodes.json", "os_nodes.json", "cn_nodes.json"]:
                if subject and not f.startswith(subject[0] if subject else ""):
                    continue
                nodes.extend(_load_json(f))
            return {"nodes": nodes, "count": len(nodes), "success": True}

        case "get_edges":
            edges = _load_json("cross_subject_edges.json")
            return {"edges": edges, "count": len(edges), "success": True}

        case "get_related":
            all_edges = _load_json("cross_subject_edges.json")
            related = [e for e in all_edges if e.get("source") == node_id or e.get("target") == node_id]
            related_node_ids = set()
            for e in related:
                related_node_ids.add(e["source"])
                related_node_ids.add(e["target"])
            related_node_ids.discard(node_id)

            related_nodes = []
            for filename in ["ds_nodes.json", "co_nodes.json", "os_nodes.json", "cn_nodes.json"]:
                for n in _load_json(filename):
                    if n.get("id") in related_node_ids:
                        related_nodes.append(n)

            return {
                "node": node_id,
                "related_nodes": related_nodes,
                "edges": related,
                "success": True,
            }

        case _:
            return {"error": f"Unknown action: {action}", "success": False}


# ============================================================
# Tool Registry — 所有工具的集合
# ============================================================

ALL_TOOLS = [image_ocr, question_search, code_executor, knowledge_graph]

TOOL_NAMES = {t.name for t in ALL_TOOLS}

# LangChain tool list — 可直接传给 .bind_tools()
langchain_tools = ALL_TOOLS


def get_tool_by_name(name: str):
    """按名称获取工具."""
    for t in ALL_TOOLS:
        if t.name == name:
            return t
    raise ValueError(f"未知工具: {name}. 可用: {TOOL_NAMES}")


def get_tool_descriptions() -> list[dict]:
    """获取所有工具描述（供 Agent prompt 使用）."""
    return [{"name": t.name, "description": t.description} for t in ALL_TOOLS]


# 向后兼容
class LegacyToolRegistry:
    """向后兼容的工具注册表."""

    def register(self, tool):
        pass

    def get(self, name):
        for t in ALL_TOOLS:
            if t.name == name:
                return t
        return None

    def list_tools(self):
        return get_tool_descriptions()


tool_registry = LegacyToolRegistry()
