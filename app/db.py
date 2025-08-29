# app/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:root@localhost:5432/gym_saas_db"
)

# Engine and SessionLocal
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency - yields a SQLAlchemy Session and ensures it is closed
    after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create DB tables based on SQLAlchemy models.Base metadata.
    Safe to call on startup (idempotent).
    """
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        # Provide a clearer error if DB not reachable
        msg = (
            "Could not create tables - check DATABASE_URL and that PostgreSQL is running.\n"
            f"Error: {exc}"
        )
        raise RuntimeError(msg)