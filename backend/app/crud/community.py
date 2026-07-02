"""Community CRUD operations."""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.community import Discussion, Reply, DiscussionLike, HotTopic


class CommunityCRUD:
    # ── Discussion ──

    def list_discussions(
        self, db: Session, subject: str = "", tag: str = "", sort: str = "latest",
        page: int = 1, page_size: int = 20,
    ) -> tuple[list[Discussion], int]:
        q = db.query(Discussion)
        if subject:
            q = q.filter(Discussion.subject == subject)
        if tag:
            q = q.filter(Discussion.tags.contains(tag))

        if sort == "hot":
            q = q.order_by(desc(Discussion.like_count), desc(Discussion.reply_count))
        elif sort == "unresolved":
            q = q.filter(Discussion.is_resolved == False)
            q = q.order_by(desc(Discussion.created_at))
        else:
            q = q.order_by(desc(Discussion.created_at))

        total = q.count()
        items = q.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_discussion(self, db: Session, discussion_id: str) -> Discussion | None:
        return db.query(Discussion).filter(Discussion.id == discussion_id).first()

    def create_discussion(self, db: Session, user_id: str, title: str, content: str,
                          subject: str = "", tags: list[str] | None = None) -> Discussion:
        disc = Discussion(
            id=uuid.uuid4().hex[:16],
            title=title,
            content=content,
            user_id=user_id,
            subject=subject,
            tags=tags or [],
        )
        db.add(disc)
        db.commit()
        db.refresh(disc)
        return disc

    # ── Reply ──

    def list_replies(self, db: Session, discussion_id: str) -> list[Reply]:
        return (
            db.query(Reply)
            .filter(Reply.discussion_id == discussion_id)
            .order_by(Reply.created_at)
            .all()
        )

    def create_reply(self, db: Session, user_id: str, discussion_id: str,
                     content: str, parent_reply_id: str | None = None) -> Reply:
        reply = Reply(
            id=uuid.uuid4().hex[:16],
            content=content,
            discussion_id=discussion_id,
            user_id=user_id,
            parent_reply_id=parent_reply_id,
        )
        db.add(reply)
        # bump reply count
        disc = self.get_discussion(db, discussion_id)
        if disc:
            disc.reply_count = (disc.reply_count or 0) + 1
        db.commit()
        db.refresh(reply)
        return reply

    def accept_reply(self, db: Session, reply_id: str) -> Reply | None:
        reply = db.query(Reply).filter(Reply.id == reply_id).first()
        if not reply:
            return None
        reply.is_accepted = True
        disc = self.get_discussion(db, reply.discussion_id)
        if disc:
            disc.is_resolved = True
            disc.resolved_reply_id = reply_id
        db.commit()
        db.refresh(reply)
        return reply

    # ── Like ──

    def toggle_like(self, db: Session, discussion_id: str, user_id: str) -> dict:
        existing = (
            db.query(DiscussionLike)
            .filter(
                DiscussionLike.discussion_id == discussion_id,
                DiscussionLike.user_id == user_id,
            )
            .first()
        )
        disc = self.get_discussion(db, discussion_id)
        if existing:
            db.delete(existing)
            if disc:
                disc.like_count = max(0, (disc.like_count or 0) - 1)
            db.commit()
            return {"liked": False, "like_count": disc.like_count if disc else 0}
        else:
            like = DiscussionLike(discussion_id=discussion_id, user_id=user_id)
            db.add(like)
            if disc:
                disc.like_count = (disc.like_count or 0) + 1
            db.commit()
            return {"liked": True, "like_count": disc.like_count if disc else 0}

    # ── Hot Topics ──

    def get_hot_topics(self, db: Session, limit: int = 5) -> list[HotTopic]:
        return (
            db.query(HotTopic)
            .order_by(desc(HotTopic.created_at))
            .limit(limit)
            .all()
        )

    def create_hot_topic(self, db: Session, title: str, summary: str,
                         discussion_ids: list[str]) -> HotTopic:
        topic = HotTopic(
            title=title,
            summary=summary,
            discussion_ids=discussion_ids,
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return topic


community_crud = CommunityCRUD()
