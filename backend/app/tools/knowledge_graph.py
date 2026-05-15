"""Knowledge Graph Tool - 知识图谱查询.

使用 LangChain @tool 定义，查询408四科知识节点和跨科关联。
完整实现见 app.core.tools.knowledge_graph
"""

from app.core.tools import knowledge_graph

__all__ = ["knowledge_graph"]
