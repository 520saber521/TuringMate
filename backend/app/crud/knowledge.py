"""Knowledge CRUD operations."""
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeNode, CrossSubjectEdge


class KnowledgeCRUD:
    def get_node(self, db: Session, node_id: str) -> KnowledgeNode | None:
        return db.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()

    def list_by_subject(self, db: Session, subject: str) -> list[KnowledgeNode]:
        return (
            db.query(KnowledgeNode)
            .filter(KnowledgeNode.subject == subject)
            .order_by(KnowledgeNode.category, KnowledgeNode.id)
            .all()
        )

    def get_tree(self, db: Session, subject: str) -> list[dict]:
        nodes = self.list_by_subject(db, subject)
        categories: dict[str, list[dict]] = {}
        for n in nodes:
            cat = n.category or "其他"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "id": n.id,
                "name": n.name,
                "difficulty": n.difficulty,
                "prerequisites": n.prerequisites or [],
            })
        return [{"category": cat, "nodes": children} for cat, children in categories.items()]

    def get_cross_links(self, db: Session, node_id: str) -> list[dict]:
        edges = (
            db.query(CrossSubjectEdge)
            .filter(
                (CrossSubjectEdge.source == node_id) | (CrossSubjectEdge.target == node_id)
            )
            .all()
        )
        result = []
        for e in edges:
            other_id = e.target if e.source == node_id else e.source
            other_node = self.get_node(db, other_id)
            result.append({
                "node_id": other_id,
                "node_name": other_node.name if other_node else other_id,
                "subject": other_node.subject if other_node else "",
                "relation": e.relation,
            })
        return result

    def seed_from_json(self, db: Session, subject: str, nodes: list[dict]):
        for n in nodes:
            existing = self.get_node(db, n["id"])
            if existing:
                existing.name = n.get("name", existing.name)
                existing.category = n.get("category", existing.category)
                existing.difficulty = n.get("difficulty", existing.difficulty)
                existing.prerequisites = n.get("prerequisites", existing.prerequisites)
            else:
                node = KnowledgeNode(
                    id=n["id"],
                    name=n.get("name", ""),
                    subject=subject,
                    category=n.get("category", ""),
                    difficulty=n.get("difficulty", 1),
                    prerequisites=n.get("prerequisites", []),
                )
                db.add(node)
        db.commit()

    def seed_edges(self, db: Session, edges: list[dict]):
        for e in edges:
            exists = (
                db.query(CrossSubjectEdge)
                .filter(
                    CrossSubjectEdge.source == e["source"],
                    CrossSubjectEdge.target == e["target"],
                )
                .first()
            )
            if not exists:
                edge = CrossSubjectEdge(
                    source=e["source"],
                    target=e["target"],
                    relation=e.get("relation", ""),
                )
                db.add(edge)
        db.commit()

    def all_subjects(self, db: Session) -> list[str]:
        rows = db.query(KnowledgeNode.subject).distinct().all()
        return sorted([r[0] for r in rows])


knowledge_crud = KnowledgeCRUD()
