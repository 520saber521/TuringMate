"""Knowledge Wiki API."""
import json
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.crud.knowledge import knowledge_crud
from app.schemas.knowledge import (
    KnowledgeTreeResponse, KnowledgeNodeDetail, CrossLinkItem,
)

router = APIRouter()

SUBJECT_MAP = {
    "ds": "数据结构", "co": "计组", "os": "操作系统", "cn": "计算机网络",
    "数据结构": "ds", "计组": "co", "操作系统": "os", "计算机网络": "cn",
}
SUBJECT_FULL = {"ds": "数据结构", "co": "计组", "os": "操作系统", "cn": "计算机网络"}

# Path to knowledge data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "knowledge")


def _normalize_subject(subject: str) -> str:
    """将中文科目名转为短键，短键保持不变。"""
    # SUBJECT_MAP 中，中文→短键方向
    for full_name, short_key in [("数据结构", "ds"), ("计组", "co"), ("操作系统", "os"), ("计算机网络", "cn")]:
        if subject == full_name:
            return short_key
    return subject if subject in SUBJECT_FULL else "ds"


@router.get("/tree", response_model=KnowledgeTreeResponse)
def get_tree(subject: str = "ds", db: Session = Depends(get_db)):
    subj_key = _normalize_subject(subject)
    nodes = knowledge_crud.list_by_subject(db, subj_key)
    if not nodes:
        _auto_seed(db, subj_key)

    tree = knowledge_crud.get_tree(db, subj_key)
    return KnowledgeTreeResponse(subject=SUBJECT_FULL.get(subj_key, subj_key), tree=tree)


@router.get("/nodes/{node_id}", response_model=KnowledgeNodeDetail)
def get_node(node_id: str, db: Session = Depends(get_db)):
    node = knowledge_crud.get_node(db, node_id)
    if not node:
        # try auto-seed
        for subj in ["ds", "co", "os", "cn"]:
            _auto_seed(db, subj)
        node = knowledge_crud.get_node(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return KnowledgeNodeDetail.model_validate(node)


class QuestionRef(BaseModel):
    id: str
    content: str
    difficulty: int

    class Config:
        from_attributes = True


@router.get("/nodes/{node_id}/questions")
def get_node_questions(node_id: str, db: Session = Depends(get_db)):
    node = knowledge_crud.get_node(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="知识点不存在")

    question_ids = node.related_question_ids or []
    questions = []
    if question_ids:
        from app.crud.question import question_crud
        for qid in question_ids:
            q = question_crud.get_by_id(db, qid)
            if q:
                questions.append({"id": q.id, "content": q.content[:100], "difficulty": q.difficulty})
    return {"node_id": node_id, "questions": questions}


@router.get("/nodes/{node_id}/cross-links", response_model=list[CrossLinkItem])
def get_cross_links(node_id: str, db: Session = Depends(get_db)):
    node = knowledge_crud.get_node(db, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="知识点不存在")
    return knowledge_crud.get_cross_links(db, node_id)


@router.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = knowledge_crud.all_subjects(db)
    if not subjects:
        for subj in ["ds", "co", "os", "cn"]:
            _auto_seed(db, subj)
        subjects = knowledge_crud.all_subjects(db)
    return {
        "subjects": [
            {"id": s, "name": SUBJECT_FULL.get(s, s)}
            for s in subjects
        ]
    }


def _auto_seed(db: Session, subject: str):
    """Auto-load knowledge nodes from JSON files."""
    json_file = os.path.join(DATA_DIR, f"{subject}_nodes.json")
    if not os.path.exists(json_file):
        return

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            nodes = json.load(f)
        knowledge_crud.seed_from_json(db, subject, nodes)
    except Exception:
        pass

    # Also seed cross-subject edges
    edges_file = os.path.join(DATA_DIR, "cross_subject_edges.json")
    if os.path.exists(edges_file):
        try:
            with open(edges_file, "r", encoding="utf-8") as f:
                edges = json.load(f)
            knowledge_crud.seed_edges(db, edges)
        except Exception:
            pass
