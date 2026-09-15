from app.services.analysis_engine import run_resume_job_analysis


def test_run_resume_job_analysis_pipeline():
    resume_text = (
        "Alex Mercer\n"
        "Email: alex@example.com | Phone: 123-456-7890\n"
        "SUMMARY\n"
        "Software developer with 2 years of experience building Python APIs and web apps.\n"
        "TECHNICAL SKILLS\n"
        "Python, FastAPI, React, PostgreSQL, Docker, Git\n"
        "WORK EXPERIENCE\n"
        "Software Developer - TechCorp (2022-2024)\n"
        "- Engineered RESTful microservices using FastAPI reducing response times by 35%.\n"
        "- Deployed applications serving 1000 users.\n"
        "EDUCATION\n"
        "B.S. in Computer Science - State University\n"
        "PROJECTS\n"
        "- Built HireLens web application.\n"
    )

    jd_text = (
        "Job Title: Python Backend Developer\n"
        "Required Skills:\n"
        "Must be proficient in Python, FastAPI, PostgreSQL, and Kubernetes.\n"
        "Preferred Skills:\n"
        "Nice to have Redis and Docker.\n"
        "Requirements:\n"
        "2+ years of experience in backend development.\n"
        "Bachelor's degree in Computer Science.\n"
    )

    response = run_resume_job_analysis(
        resume_text=resume_text, job_description_text=jd_text
    )

    assert response.overall_score > 50.0
    assert "Python" in response.resume_skills
    assert "FastAPI" in response.resume_skills
    assert "Kubernetes" in response.missing_required_skills
    assert "Docker" in response.matching_skills
    assert response.score_breakdown.skill_score > 50.0
    assert response.score_breakdown.text_similarity_score > 10.0
    assert response.experience_alignment.status == "aligned"
    assert response.education_alignment.status == "aligned"
    assert len(response.recommendations) > 0
