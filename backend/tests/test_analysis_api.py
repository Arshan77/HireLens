def test_preview_analysis_endpoint_success(client):
    payload = {
        "resume_text": "Experienced Python Developer with FastAPI and PostgreSQL skills. 2 years experience.",
        "job_description_text": "Seeking a Python Developer with FastAPI skills. 2+ years experience required.",
    }
    response = client.post("/api/v1/analysis/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "score_breakdown" in data
    assert "matching_skills" in data
    assert "Python" in data["matching_skills"]
    assert "FastAPI" in data["matching_skills"]


def test_preview_analysis_endpoint_empty_resume(client):
    payload = {
        "resume_text": "",
        "job_description_text": "Python developer required.",
    }
    response = client.post("/api/v1/analysis/preview", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "FILE_VALIDATION_ERROR"
    assert "Resume text" in data["detail"]


def test_preview_analysis_endpoint_empty_jd(client):
    payload = {
        "resume_text": "Python developer",
        "job_description_text": "   ",
    }
    response = client.post("/api/v1/analysis/preview", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "FILE_VALIDATION_ERROR"
    assert "Job description" in data["detail"]
