from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.resume import ResumeParseResponse, ResumeListItem
from app.services.validator import validate_resume_file
from app.services.extractor import extract_text_from_file
from app.services.cleaner import clean_text
from app.services.section_parser import parse_resume_sections
from app.core.exceptions import FileValidationError
from app.core.auth_dependency import get_current_user, get_optional_current_user
from app.models.user import User
from app.repositories import resume_repository

router = APIRouter(prefix="/api/v1/resumes", tags=["Resumes"])


@router.post(
    "/upload",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and parse a PDF or DOCX resume",
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if not file or not file.filename:
        raise FileValidationError("No file uploaded or filename missing.")

    file_bytes = await file.read()

    # 1. Validate file
    safe_filename, file_type, file_size = validate_resume_file(
        filename=file.filename,
        content_type=file.content_type or "",
        file_bytes=file_bytes,
    )

    # 2. Extract raw text
    raw_text = extract_text_from_file(file_type=file_type, file_bytes=file_bytes)

    # 3. Clean text
    cleaned_text = clean_text(raw_text)

    # 4. Parse sections
    sections = parse_resume_sections(cleaned_text)

    # 5. Persist to DB if user is authenticated
    persisted_id = None
    persisted_created_at = None
    if current_user:
        new_resume = resume_repository.create_resume(
            db=db,
            user_id=current_user.id,
            original_filename=safe_filename,
            file_type=file_type,
            file_size=file_size,
            raw_text=cleaned_text,
            parsed_data=sections.model_dump(),
        )
        persisted_id = new_resume.id
        persisted_created_at = new_resume.created_at

    # 6. Return structured JSON response
    return ResumeParseResponse(
        id=persisted_id,
        filename=safe_filename,
        file_type=file_type,
        file_size=file_size,
        text=cleaned_text,
        sections=sections,
        created_at=persisted_created_at,
        uploaded_at=persisted_created_at,
    )


@router.get(
    "",
    response_model=List[ResumeListItem],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user's uploaded resumes",
)
async def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = resume_repository.get_user_resumes(db, user_id=current_user.id)
    return [
        ResumeListItem(
            id=r.id,
            filename=r.original_filename,
            file_type=r.file_type,
            file_size=r.file_size,
            created_at=r.created_at,
            uploaded_at=r.created_at,
        )
        for r in resumes
    ]


@router.get(
    "/{resume_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get single resume record if owned by current user",
)
async def get_resume_detail(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = resume_repository.get_resume_by_id(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or unauthorized.",
        )

    return {
        "id": resume.id,
        "filename": resume.original_filename,
        "file_type": resume.file_type,
        "file_size": resume.file_size,
        "raw_text": resume.raw_text,
        "parsed_data": resume.parsed_data,
        "created_at": resume.created_at,
        "uploaded_at": resume.created_at,
    }
