"""Knowledge Graph Tool - 知识图谱查询工具.

四科（数据结构/计组/OS/网络）知识点节点和跨科关联边。
MVP 阶段使用预定义的结构化 JSON 数据。
"""

import json
from pathlib import Path
from app.core.tools import BaseTool, ToolResult


class KnowledgeGraphTool(BaseTool):
    """知识图谱查询工具."""

    name = "knowledge_graph"
    description = "查询408四科知识点节点和跨科目关联关系"

    def __init__(self, data_dir: str = "./data/knowledge"):
        self._data_dir = Path(data_dir)
        self._cache: dict[str, list] = {}

    def _load_json(self, filename: str) -> list:
        """加载并缓存 JSON 文件."""
        if filename not in self._cache:
            path = self._data_dir / filename
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self._cache[filename] = json.load(f)
            else:
                self._cache[filename] = []
        return self._cache[filename]

    async def execute(
        self,
        action: str = "get_nodes",
        subject: str | None = None,
        node_id: str | None = None,
    ) -> ToolResult:
        """执行知识图谱查询.

        Args:
            action: 查询类型 ("get_nodes" | "get_edges" | "get_related")
            subject: 科目过滤 (ds/co/os/cn)
            node_id: 节点 ID（用于关联查询）
        """
        match action:
            case "get_nodes":
                nodes = []
                for f in ["ds_nodes.json", "co_nodes.json", "os_nodes.json", "cn_nodes.json"]:
                    if subject and not f.startswith(subject[0]):
                        continue
                    nodes.extend(self._load_json(f))
                return ToolResult(success=True, data=nodes)

            case "get_edges":
                edges = self._load_json("cross_subject_edges.json")
                return ToolResult(success=True, data=edges)

            case "get_related":
                # TODO: 实现关联节点查找
                return ToolResult(
                    success=True,
                    data={"node": node_id, "related_nodes": []},
                )

            case _:
                return ToolResult(success=False, error=f"Unknown action: {action}")


from app.core.tools import tool_registry
tool_registry.register(KnowledgeGraphTool())
