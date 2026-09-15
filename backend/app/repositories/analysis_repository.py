from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.analysis import Analysis


def create_analysis(
    db: Session,
    user_id: str,
    resume_id: str,
    job_description_id: str,
    overall_score: float,
    result_json: Dict[str, Any],
) -> Analysis:
    """Create and persist a user-owned analysis record."""
    analysis = Analysis(
        user_id=user_id,
        resume_id=resume_id,
        job_description_id=job_description_id,
        overall_score=overall_score,
        result_json=result_json,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_user_analyses(
    db: Session, user_id: str, skip: int = 0, limit: int = 20
) -> List[Analysis]:
    """Retrieve paginated list of analyses owned by user_id sorted newest first."""
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_analysis_by_id(db: Session, analysis_id: str, user_id: str) -> Optional[Analysis]:
    """
    Retrieve single analysis record by ID ONLY if owned by user_id.
    Strict user isolation.
    """
    return db.query(Analysis).filter(
        Analysis.id == analysis_id, Analysis.user_id == user_id
    ).first()


def delete_analysis_by_id(db: Session, analysis_id: str, user_id: str) -> bool:
    """
    Delete single analysis record by ID ONLY if owned by user_id.
    Returns True if deleted, False if not found or unauthorized.
    """
    record = get_analysis_by_id(db=db, analysis_id=analysis_id, user_id=user_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
