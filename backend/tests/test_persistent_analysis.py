def test_persistent_analysis_full_lifecycle(client, create_test_user, create_sample_pdf_bytes):
    # 1. Setup authenticated user
    user_data = create_test_user(email="analyst@example.com")
    headers = user_data["headers"]

    # 2. Upload resume
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("analyst_resume.pdf", pdf_bytes, "application/pdf")},
        headers=headers,
    )
    assert upload_res.status_code == 200

    resumes_list = client.get("/api/v1/resumes", headers=headers)
    assert len(resumes_list.json()) == 1
    resume_id = resumes_list.json()[0]["id"]

    # 3. Run persistent analysis
    jd_text = (
        "Seeking a Python Backend Developer.\n"
        "Required Skills: Python, FastAPI, PostgreSQL, Docker.\n"
        "Experience: 2+ years required."
    )
    run_res = client.post(
        "/api/v1/analysis/run",
        json={
            "resume_id": resume_id,
            "job_title": "Python Developer",
            "job_description_text": jd_text,
        },
        headers=headers,
    )
    assert run_res.status_code == 201
    analysis_data = run_res.json()
    assert "analysis_id" in analysis_data
    analysis_id = analysis_data["analysis_id"]
    original_score = analysis_data["overall_score"]

    # 4. Check history listing
    history_res = client.get("/api/v1/analysis/history", headers=headers)
    assert history_res.status_code == 200
    history_list = history_res.json()
    assert len(history_list) == 1
    assert history_list[0]["id"] == analysis_id
    assert history_list[0]["overall_score"] == original_score
    assert history_list[0]["job_title"] == "Python Developer"

    # 5. Get single analysis detail
    detail_res = client.get(f"/api/v1/analysis/{analysis_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["overall_score"] == original_score
    assert "Python" in detail_data["matching_skills"]

    # 6. Delete analysis
    del_res = client.delete(f"/api/v1/analysis/{analysis_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Analysis deleted successfully."

    # 7. Verify deletion
    get_deleted = client.get(f"/api/v1/analysis/{analysis_id}", headers=headers)
    assert get_deleted.status_code == 404

    history_after_del = client.get("/api/v1/analysis/history", headers=headers)
    assert len(history_after_del.json()) == 0
