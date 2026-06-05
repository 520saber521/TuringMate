"""Chat session CRUD operations."""
import uuid
from sqlalchemy.orm import Session
from app.models.chat import ChatSession


class ChatCRUD:
    def get_by_id(self, db: Session, session_id: str) -> ChatSession | None:
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def list_by_user(self, db: Session, user_id: str, limit: int = 20) -> list[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, db: Session, user_id: str, question_id: str = None) -> ChatSession:
        session = ChatSession(
            id=str(uuid.uuid4())[:32],
            user_id=user_id,
            question_id=question_id,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def append_message(self, db: Session, session: ChatSession, role: str, content: str, stage: str = None) -> ChatSession:
        import datetime
        messages = list(session.messages or [])
        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
            "stage": stage or session.current_stage,
        })
        session.messages = messages
        if stage:
            session.current_stage = stage
        db.commit()
        db.refresh(session)
        return session

    def update_status(self, db: Session, session: ChatSession, status: str) -> ChatSession:
        session.status = status
        db.commit()
        db.refresh(session)
        return session


chat_crud = ChatCRUD()
