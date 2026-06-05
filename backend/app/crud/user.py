"""User CRUD operations."""
import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password


class UserCRUD:
    def get_by_id(self, db: Session, user_id: str) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, username: str, password: str, name: str, email: str = "") -> User:
        user = User(
            id=str(uuid.uuid4())[:32],
            username=username,
            email=email,
            name=name,
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = self.get_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def update(self, db: Session, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user


user_crud = UserCRUD()
