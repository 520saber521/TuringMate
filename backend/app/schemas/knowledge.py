"""Knowledge schemas."""
from pydantic import BaseModel


class KnowledgeNodeItem(BaseModel):
    id: str
    name: str
    difficulty: int = 1
    prerequisites: list[str] = []

    class Config:
        from_attributes = True


class KnowledgeCategory(BaseModel):
    category: str
    nodes: list[KnowledgeNodeItem]


class KnowledgeTreeResponse(BaseModel):
    subject: str
    tree: list[KnowledgeCategory]


class CrossLinkItem(BaseModel):
    node_id: str
    node_name: str
    subject: str
    relation: str


class KnowledgeNodeDetail(BaseModel):
    id: str
    name: str
    subject: str
    category: str = ""
    difficulty: int = 1
    prerequisites: list[str] = []
    concept_explanation: str | None = None
    common_pitfalls: list[str] = []
    related_question_ids: list[str] = []

    class Config:
        from_attributes = True
