from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.resume import Resume


def create_resume(
    db: Session,
    user_id: str,
    original_filename: str,
    file_type: str,
    file_size: int,
    raw_text: str,
    parsed_data: Optional[Dict[str, Any]] = None,
) -> Resume:
    """Create and persist a user-owned resume record."""
    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        file_type=file_type,
        file_size=file_size,
        raw_text=raw_text,
        parsed_data=parsed_data or {},
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_user_resumes(db: Session, user_id: str) -> List[Resume]:
    """Retrieve all resumes owned by the specified user (user data isolation)."""
    return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).all()


def get_resume_by_id(db: Session, resume_id: str, user_id: str) -> Optional[Resume]:
    """
    Retrieve single resume by ID ONLY if owned by user_id.
    Prevents cross-user data access.
    """
    return db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
