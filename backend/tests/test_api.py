def test_upload_valid_pdf_resume(client, create_sample_pdf_bytes):
    pdf_bytes = create_sample_pdf_bytes()
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("alex_mercer.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "alex_mercer.pdf"
    assert data["file_type"] == "pdf"
    assert data["file_size"] == len(pdf_bytes)
    assert "Alex Mercer" in data["text"]
    assert "sections" in data
    assert "skills" in data["sections"]
    assert "experience" in data["sections"]
    assert "education" in data["sections"]


def test_upload_valid_docx_resume(client, create_sample_docx_bytes):
    docx_bytes = create_sample_docx_bytes()
    response = client.post(
        "/api/v1/resumes/upload",
        files={
            "file": (
                "taylor_reed.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "taylor_reed.docx"
    assert data["file_type"] == "docx"
    assert data["file_size"] == len(docx_bytes)
    assert "Taylor Reed" in data["text"]
    assert "sections" in data


def test_upload_invalid_extension(client):
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("script.py", b"print('hello')", "text/plain")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "FILE_VALIDATION_ERROR"
    assert "Unsupported file format" in data["detail"]


def test_upload_empty_file(client):
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "FILE_VALIDATION_ERROR"
    assert "empty" in data["detail"]


def test_upload_oversized_file(client):
    large_bytes = b"%PDF-" + b"0" * (6 * 1024 * 1024)
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("large.pdf", large_bytes, "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "FILE_VALIDATION_ERROR"
    assert "exceeds maximum limit" in data["detail"]


def test_upload_invalid_signature(client):
    fake_pdf = b"INVALID_HEADER_BYTES_FOR_PDF"
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("fake.pdf", fake_pdf, "application/pdf")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_type"] == "FILE_VALIDATION_ERROR"
    assert "File signature verification failed" in data["detail"]


def test_upload_corrupted_pdf(client):
    corrupted_pdf = b"%PDF-1.4\nCorrupted payload..."
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("corrupted.pdf", corrupted_pdf, "application/pdf")},
    )
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "FILE_EXTRACTION_ERROR"
