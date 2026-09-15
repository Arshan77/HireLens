from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class SectionData(BaseModel):
    contact: str = Field(default="", description="Contact information found in the resume")
    summary: str = Field(default="", description="Professional summary, objective, or profile statement")
    skills: str = Field(default="", description="Technical skills, soft skills, and technologies")
    experience: str = Field(default="", description="Work experience and employment history")
    education: str = Field(default="", description="Education background and academic qualifications")
    projects: str = Field(default="", description="Academic and personal projects")
    certifications: str = Field(default="", description="Certifications and professional credentials")

class ResumeParseResponse(BaseModel):
    id: Optional[str] = Field(None, description="Persisted resume ID if authenticated")
    filename: str = Field(..., description="Sanitized original filename")
    file_type: str = Field(..., description="Detected file extension ('pdf' or 'docx')")
    file_size: int = Field(..., description="File size in bytes")
    text: str = Field(..., description="Cleaned full text extracted from resume")
    sections: SectionData = Field(..., description="Structured sections extracted from resume text")
    created_at: Optional[datetime] = Field(None, description="Timestamp created")
    uploaded_at: Optional[datetime] = Field(None, description="Timestamp uploaded (alias)")

class ResumeListItem(BaseModel):
    id: str = Field(..., description="Resume ID")
    filename: str = Field(..., description="Sanitized original filename")
    file_type: str = Field(..., description="File type extension")
    file_size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Timestamp created")
    uploaded_at: datetime = Field(..., description="Timestamp uploaded (alias)")

class HealthCheckResponse(BaseModel):
    status: str = Field(default="ok", description="Service health status")
    version: str = Field(..., description="API version")
    app_name: str = Field(..., description="Application name")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human readable error message")
    error_type: str = Field(..., description="Error classification string")
