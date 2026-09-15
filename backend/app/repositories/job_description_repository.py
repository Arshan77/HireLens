from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription


def create_job_description(
    db: Session, user_id: str, raw_text: str, title: Optional[str] = None
) -> JobDescription:
    """Create and persist a user-owned job description record."""
    jd = JobDescription(
        user_id=user_id,
        title=title,
        raw_text=raw_text,
    )
    db.add(jd)
    db.commit()
    db.refresh(jd)
    return jd


def get_job_description_by_id(db: Session, jd_id: str, user_id: str) -> Optional[JobDescription]:
    """Retrieve job description by ID ONLY if owned by user_id."""
    return db.query(JobDescription).filter(
        JobDescription.id == jd_id, JobDescription.user_id == user_id
    ).first()
