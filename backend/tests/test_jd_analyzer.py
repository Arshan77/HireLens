from app.services.jd_analyzer import analyze_job_description_skills


def test_analyze_jd_required_and_preferred():
    jd_text = (
        "Required Qualifications:\n"
        "Must have experience with Python, FastAPI, and PostgreSQL.\n"
        "Preferred Qualifications:\n"
        "Nice to have experience with Kubernetes and Redis.\n"
    )
    result = analyze_job_description_skills(jd_text)
    assert "Python" in result["required_skills"]
    assert "FastAPI" in result["required_skills"]
    assert "PostgreSQL" in result["required_skills"]
    assert "Kubernetes" in result["preferred_skills"]
    assert "Redis" in result["preferred_skills"]


def test_analyze_jd_fallback_all_required():
    jd_text = "Looking for a Software Engineer proficient in React, Node.js, and MongoDB."
    result = analyze_job_description_skills(jd_text)
    assert "React" in result["required_skills"]
    assert "Node.js" in result["required_skills"]
    assert "MongoDB" in result["required_skills"]
    assert len(result["preferred_skills"]) == 0


def test_analyze_jd_empty_text():
    result = analyze_job_description_skills("")
    assert result["required_skills"] == []
    assert result["preferred_skills"] == []
