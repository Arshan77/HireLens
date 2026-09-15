import io
import pytest
from app.services.pdf_generator import generate_analysis_pdf_report
from app.core import config


def test_generate_pdf_report_direct():
    """Verify in-memory PDF generation produces valid PDF bytes."""
    mock_data = {
        "id": "analysis-12345",
        "job_title": "Senior Backend Developer",
        "overall_score": 84.5,
        "score_breakdown": {
            "skill_score": 90.0,
            "text_similarity_score": 75.0,
            "experience_score": 85.0,
            "ats_quality_score": 88.0,
        },
        "weights": {
            "skill": 0.40,
            "text_similarity": 0.30,
            "experience": 0.15,
            "ats": 0.15,
        },
        "matching_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        "missing_required_skills": ["Redis"],
        "missing_preferred_skills": ["Kubernetes"],
        "prioritized_skill_gaps": [
            {
                "skill": "Redis",
                "category": "database",
                "priority": "high",
                "required_or_preferred": "required",
                "reason": "Redis is listed as a required database skill in the job description.",
                "action": "Add a relevant Redis caching project before applying.",
            }
        ],
        "role_recommendations": [
            {
                "role": "Backend Developer",
                "score": 82.5,
                "fit_level": "Strong fit",
                "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
                "missing_core_skills": ["Spring Boot"],
                "reason": "Strong alignment with backend development requirements.",
            }
        ],
        "ats_breakdown": {
            "score": 88.0,
            "details": {
                "section_completeness_score": 100.0,
                "action_verb_score": 80.0,
                "quantifiable_metrics_score": 80.0,
                "sections_found": ["experience", "education", "skills", "projects"],
                "sections_missing": [],
                "action_verbs_found": ["developed", "engineered", "optimized"],
                "metrics_count": 4,
            },
        },
        "ats_recommendations": [
            {
                "category": "metrics",
                "priority": "medium",
                "title": "Add Measurable Achievements",
                "issue": "Detected 4 quantifiable metrics.",
                "action": "Continue adding metrics to new bullet points.",
            }
        ],
        "unified_recommendations": [
            {
                "type": "skill_gap",
                "priority": "high",
                "title": "Acquire / Highlight Redis",
                "reason": "Redis is listed as required in JD.",
                "action": "Build a caching service with Redis.",
            }
        ],
    }

    pdf_bytes = generate_analysis_pdf_report(
        analysis_data=mock_data,
        candidate_name="Jane Developer",
        resume_filename="Jane_Resume.pdf",
        job_title="Senior Backend Developer",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-")


def test_generate_pdf_report_empty_fallback():
    """Verify PDF generator handles missing or empty fields without crashing."""
    pdf_bytes = generate_analysis_pdf_report(
        analysis_data={},
        candidate_name=None,
        resume_filename=None,
        job_title=None,
    )
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")


def test_download_pdf_report_authenticated_success(client, create_test_user, create_sample_pdf_bytes):
    """Verify an authenticated user can download their analysis report as a PDF."""
    user_data = create_test_user(email="reportowner@example.com")
    pdf_bytes = create_sample_pdf_bytes()

    # 1. Upload resume
    upload_res = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
        headers=user_data["headers"],
    )
    assert upload_res.status_code == 200
    resume_id = upload_res.json()["id"]

    # 2. Run analysis
    jd_text = (
        "Seeking a Python Developer with 3+ years experience in FastAPI, PostgreSQL, "
        "Docker, and Git. Must have a Bachelor's degree."
    )
    analysis_res = client.post(
        "/api/v1/analysis/run",
        json={
            "resume_id": resume_id,
            "job_title": "Python Developer",
            "job_description_text": jd_text,
        },
        headers=user_data["headers"],
    )
    assert analysis_res.status_code == 201
    analysis_id = analysis_res.json()["id"]

    # 3. Request PDF Report
    report_res = client.get(
        f"/api/v1/analysis/{analysis_id}/report",
        headers=user_data["headers"],
    )
    assert report_res.status_code == 200
    assert "application/pdf" in report_res.headers["content-type"]
    assert "attachment; filename=" in report_res.headers["content-disposition"]
    assert report_res.content.startswith(b"%PDF-")
    assert len(report_res.content) > 1000


def test_download_pdf_report_user_isolation(client, create_test_user, create_sample_pdf_bytes):
    """Verify User B cannot download User A's PDF analysis report (strict user isolation)."""
    user_a = create_test_user(email="usera_report@example.com")
    user_b = create_test_user(email="userb_report@example.com")

    # User A uploads and analyzes
    upload_res = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume_a.pdf", create_sample_pdf_bytes(), "application/pdf")},
        headers=user_a["headers"],
    )
    resume_id = upload_res.json()["id"]

    analysis_res = client.post(
        "/api/v1/analysis/run",
        json={
            "resume_id": resume_id,
            "job_title": "Software Engineer",
            "job_description_text": "Python and PostgreSQL engineer needed.",
        },
        headers=user_a["headers"],
    )
    analysis_id = analysis_res.json()["id"]

    # User B attempts to download User A's report
    unauth_res = client.get(
        f"/api/v1/analysis/{analysis_id}/report",
        headers=user_b["headers"],
    )
    assert unauth_res.status_code == 404
    assert "not found or unauthorized" in unauth_res.json()["detail"].lower()


def test_download_pdf_report_unauthenticated(client):
    """Verify unauthenticated request is rejected with 401."""
    res = client.get("/api/v1/analysis/some-random-id/report")
    assert res.status_code == 401


def test_download_pdf_report_not_found(client, create_test_user):
    """Verify 404 for nonexistent analysis ID."""
    user = create_test_user(email="notfound_test@example.com")
    res = client.get("/api/v1/analysis/nonexistent-uuid/report", headers=user["headers"])
    assert res.status_code == 404


def test_production_security_validation(monkeypatch):
    """Verify production environment rejects insecure JWT keys and wildcard CORS."""
    # 1. Insecure key in production
    monkeypatch.setattr(config, "ENVIRONMENT", "production")
    monkeypatch.setattr(config, "JWT_SECRET_KEY", "hirelens-dev-secret-key-do-not-use-in-production-123456789")
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        config.validate_production_config()

    # 2. Wildcard CORS in production
    monkeypatch.setattr(config, "JWT_SECRET_KEY", "a-very-secure-random-secret-key-32-chars-minimum")
    monkeypatch.setattr(config, "CORS_ORIGINS", ["https://hirelens.com", "*"])
    with pytest.raises(RuntimeError, match="Wildcard CORS"):
        config.validate_production_config()

    # 3. Valid production configuration passes
    monkeypatch.setattr(config, "CORS_ORIGINS", ["https://hirelens.com", "https://app.hirelens.com"])
    config.validate_production_config()  # Should not raise

    # 4. Development mode passes with default dev key
    monkeypatch.setattr(config, "ENVIRONMENT", "development")
    monkeypatch.setattr(config, "JWT_SECRET_KEY", "hirelens-dev-secret-key-do-not-use-in-production-123456789")
    monkeypatch.setattr(config, "CORS_ORIGINS", ["*"])
    config.validate_production_config()  # Should not raise in development
