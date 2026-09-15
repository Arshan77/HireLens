from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analysis import (
    AnalysisPreviewRequest,
    AnalysisPreviewResponse,
    RunAnalysisRequest,
    AnalysisHistorySummary,
)
from app.services.analysis_engine import run_resume_job_analysis
from app.services.pdf_generator import generate_analysis_pdf_report
from app.core.exceptions import FileValidationError
from app.core.auth_dependency import get_current_user
from app.models.user import User
from app.repositories import (
    resume_repository,
    job_description_repository,
    analysis_repository,
)

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis Engine"])


@router.post(
    "/preview",
    response_model=AnalysisPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Stateless preview analysis endpoint for Phase 2 engine testing",
    description="Accepts raw cleaned resume text and job description text to execute the complete explainable matching pipeline.",
)
async def preview_analysis(payload: AnalysisPreviewRequest):
    if not payload.resume_text or not payload.resume_text.strip():
        raise FileValidationError("Resume text payload cannot be empty.")

    if not payload.job_description_text or not payload.job_description_text.strip():
        raise FileValidationError("Job description text payload cannot be empty.")

    return run_resume_job_analysis(
        resume_text=payload.resume_text,
        job_description_text=payload.job_description_text,
    )


@router.post(
    "/run",
    response_model=AnalysisPreviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute analysis engine and save result to database",
    description="Runs Phase 2 analysis engine on an authenticated user's uploaded resume and job description, persisting the analysis result.",
)
async def run_and_save_analysis(
    payload: RunAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Verify user owns the resume
    resume = resume_repository.get_resume_by_id(
        db, resume_id=payload.resume_id, user_id=current_user.id
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or unauthorized.",
        )

    if not payload.job_description_text or not payload.job_description_text.strip():
        raise FileValidationError("Job description text cannot be empty.")

    # 2. Persist Job Description
    jd = job_description_repository.create_job_description(
        db=db,
        user_id=current_user.id,
        raw_text=payload.job_description_text,
        title=payload.job_title,
    )

    # 3. Run Analysis Engine
    analysis_result = run_resume_job_analysis(
        resume_text=resume.raw_text,
        job_description_text=payload.job_description_text,
    )

    # 4. Save Analysis Record
    result_dict = analysis_result.model_dump()
    analysis_record = analysis_repository.create_analysis(
        db=db,
        user_id=current_user.id,
        resume_id=resume.id,
        job_description_id=jd.id,
        overall_score=analysis_result.overall_score,
        result_json=result_dict,
    )

    # Add DB IDs and metadata to response
    result_dict["id"] = analysis_record.id
    result_dict["analysis_id"] = analysis_record.id
    result_dict["resume_id"] = resume.id
    result_dict["job_description_id"] = jd.id
    result_dict["job_title"] = jd.title
    result_dict["created_at"] = analysis_record.created_at.isoformat() if analysis_record.created_at else None

    # Persist updated IDs to stored result_json
    analysis_record.result_json = result_dict
    db.commit()

    return AnalysisPreviewResponse(**result_dict)


@router.get(
    "/history",
    response_model=List[AnalysisHistorySummary],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user's analysis history",
)
async def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = analysis_repository.get_user_analyses(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

    history = []
    for rec in records:
        history.append(
            AnalysisHistorySummary(
                id=rec.id,
                overall_score=rec.overall_score,
                resume_id=rec.resume_id,
                resume_filename=rec.resume.original_filename if rec.resume else None,
                job_description_id=rec.job_description_id,
                job_title=rec.job_description.title if rec.job_description else None,
                created_at=rec.created_at,
            )
        )
    return history


@router.get(
    "/{analysis_id}",
    response_model=AnalysisPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single analysis details by ID (user isolated)",
)
async def get_single_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = analysis_repository.get_analysis_by_id(
        db, analysis_id=analysis_id, user_id=current_user.id
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or unauthorized.",
        )

    res_json = record.result_json.copy() if isinstance(record.result_json, dict) else {}
    res_json["id"] = record.id
    res_json["analysis_id"] = record.id
    res_json["resume_id"] = record.resume_id
    res_json["job_description_id"] = record.job_description_id
    res_json["job_title"] = record.job_description.title if record.job_description else None
    res_json["created_at"] = record.created_at.isoformat() if record.created_at else None

    return AnalysisPreviewResponse(**res_json)


@router.get(
    "/{analysis_id}/report",
    status_code=status.HTTP_200_OK,
    summary="Download PDF analysis report (authenticated & user isolated)",
    description="Generates an in-memory PDF report from the stored analysis record. Strict user isolation enforced.",
)
async def download_analysis_report(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = analysis_repository.get_analysis_by_id(
        db, analysis_id=analysis_id, user_id=current_user.id
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis report not found or unauthorized.",
        )

    analysis_data = record.result_json if isinstance(record.result_json, dict) else {}
    resume_filename = record.resume.original_filename if record.resume else None
    job_title = record.job_description.title if record.job_description else None

    pdf_bytes = generate_analysis_pdf_report(
        analysis_data=analysis_data,
        candidate_name=getattr(current_user, "full_name", None) or current_user.email,
        resume_filename=resume_filename,
        job_title=job_title,
    )

    safe_id = analysis_id.replace("-", "")[:8]
    filename = f"HireLens_Report_{safe_id}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        },
    )


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an analysis record owned by current user",
)
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = analysis_repository.delete_analysis_by_id(
        db, analysis_id=analysis_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found or unauthorized.",
        )

    return {"message": "Analysis deleted successfully.", "analysis_id": analysis_id}
