from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator

from app.core.config import DATABASE_URL

# SQLite requires check_same_thread=False for multi-threading in FastAPI dev
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI dependency that yields a transactional SQLAlchemy database session.
    Closes the session automatically when request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
