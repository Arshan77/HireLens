import pytest


def test_cross_user_data_isolation(client, create_test_user, create_sample_pdf_bytes):
    # 1. Setup User A and User B
    user_a = create_test_user(email="usera@example.com")
    user_b = create_test_user(email="userb@example.com")

    # 2. User A uploads a resume
    pdf_bytes = create_sample_pdf_bytes()
    upload_res = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("usera_resume.pdf", pdf_bytes, "application/pdf")},
        headers=user_a["headers"],
    )
    assert upload_res.status_code == 200

    # Retrieve User A's resume ID from DB list
    list_res_a = client.get("/api/v1/resumes", headers=user_a["headers"])
    assert len(list_res_a.json()) == 1
    resume_a_id = list_res_a.json()[0]["id"]

    # 3. User A runs persistent analysis
    run_res_a = client.post(
        "/api/v1/analysis/run",
        json={
            "resume_id": resume_a_id,
            "job_title": "Python Developer",
            "job_description_text": "Seeking Python developer with FastAPI and PostgreSQL skills.",
        },
        headers=user_a["headers"],
    )
    assert run_res_a.status_code == 201
    analysis_a_id = run_res_a.json()["analysis_id"]

    # --- CROSS-USER ISOLATION VERIFICATION (User B attempts to access User A's resources) ---

    # 4. User B CANNOT view User A's resume detail (expects 404)
    res = client.get(f"/api/v1/resumes/{resume_a_id}", headers=user_b["headers"])
    assert res.status_code == 404

    # 5. User B's resume list does NOT contain User A's resume
    list_res_b = client.get("/api/v1/resumes", headers=user_b["headers"])
    assert len(list_res_b.json()) == 0

    # 6. User B CANNOT run analysis using User A's resume_id (expects 404)
    run_b_res = client.post(
        "/api/v1/analysis/run",
        json={
            "resume_id": resume_a_id,
            "job_description_text": "Python developer required.",
        },
        headers=user_b["headers"],
    )
    assert run_b_res.status_code == 404

    # 7. User B CANNOT view User A's analysis detail (expects 404)
    res = client.get(f"/api/v1/analysis/{analysis_a_id}", headers=user_b["headers"])
    assert res.status_code == 404

    # 8. User B's history list does NOT contain User A's analysis
    hist_b_res = client.get("/api/v1/analysis/history", headers=user_b["headers"])
    assert len(hist_b_res.json()) == 0

    # 9. User B CANNOT delete User A's analysis (expects 404)
    del_b_res = client.delete(f"/api/v1/analysis/{analysis_a_id}", headers=user_b["headers"])
    assert del_b_res.status_code == 404

    # --- VERIFY USER A CAN STILL ACCESS & DELETE OWN DATA ---

    # User A views single analysis (200 OK)
    res_a_view = client.get(f"/api/v1/analysis/{analysis_a_id}", headers=user_a["headers"])
    assert res_a_view.status_code == 200
    assert res_a_view.json()["overall_score"] > 0

    # User A deletes own analysis (200 OK)
    del_a_res = client.delete(f"/api/v1/analysis/{analysis_a_id}", headers=user_a["headers"])
    assert del_a_res.status_code == 200
