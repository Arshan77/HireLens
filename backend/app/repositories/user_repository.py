from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve user record by normalized email address."""
    normalized = email.strip().lower()
    return db.query(User).filter(User.email == normalized).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Retrieve user record by primary key UUID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password_hash: str) -> User:
    """Create and persist a new user record."""
    normalized_email = email.strip().lower()
    user = User(
        email=normalized_email,
        password_hash=password_hash,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
