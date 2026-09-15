import pytest
from app.services.validator import sanitize_filename, validate_resume_file
from app.core.exceptions import FileValidationError


def test_sanitize_filename():
    assert sanitize_filename("resume.pdf") == "resume.pdf"
    assert sanitize_filename("../../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename("C:\\Users\\compu\\My Resume 2024.docx") == "My Resume 2024.docx"
    
    with pytest.raises(FileValidationError):
        sanitize_filename("")


def test_validate_resume_file_valid_pdf(create_sample_pdf_bytes):
    pdf_bytes = create_sample_pdf_bytes()
    filename, file_type, file_size = validate_resume_file(
        filename="john_doe.pdf",
        content_type="application/pdf",
        file_bytes=pdf_bytes,
    )
    assert filename == "john_doe.pdf"
    assert file_type == "pdf"
    assert file_size == len(pdf_bytes)


def test_validate_resume_file_valid_docx(create_sample_docx_bytes):
    docx_bytes = create_sample_docx_bytes()
    filename, file_type, file_size = validate_resume_file(
        filename="jane_smith.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        file_bytes=docx_bytes,
    )
    assert filename == "jane_smith.docx"
    assert file_type == "docx"
    assert file_size == len(docx_bytes)


def test_validate_resume_file_invalid_extension():
    with pytest.raises(FileValidationError) as excinfo:
        validate_resume_file(
            filename="script.exe",
            content_type="application/x-msdownload",
            file_bytes=b"MZ_FAKE_EXE_BYTES",
        )
    assert "Unsupported file format" in str(excinfo.value)


def test_validate_resume_file_empty_file():
    with pytest.raises(FileValidationError) as excinfo:
        validate_resume_file(
            filename="empty.pdf",
            content_type="application/pdf",
            file_bytes=b"",
        )
    assert "empty" in str(excinfo.value)


def test_validate_resume_file_oversized_file():
    oversized_bytes = b"%PDF-" + b"0" * (6 * 1024 * 1024)  # 6 MB
    with pytest.raises(FileValidationError) as excinfo:
        validate_resume_file(
            filename="large.pdf",
            content_type="application/pdf",
            file_bytes=oversized_bytes,
        )
    assert "exceeds maximum limit" in str(excinfo.value)


def test_validate_resume_file_invalid_magic_signature():
    fake_pdf = b"NOT_A_PDF_MAGIC_BYTES_12345"
    with pytest.raises(FileValidationError) as excinfo:
        validate_resume_file(
            filename="fake.pdf",
            content_type="application/pdf",
            file_bytes=fake_pdf,
        )
    assert "File signature verification failed" in str(excinfo.value)
