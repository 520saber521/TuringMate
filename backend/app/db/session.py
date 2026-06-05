"""Database session dependency injection."""
from app.models.database import SessionLocal


def get_db():
    """FastAPI dependency: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
