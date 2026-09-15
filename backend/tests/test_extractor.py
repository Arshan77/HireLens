import pytest
from app.services.extractor import (
    extract_pdf_text,
    extract_docx_text,
    extract_text_from_file,
)
from app.core.exceptions import FileExtractionError


def test_extract_pdf_text_single_page(create_sample_pdf_bytes):
    pdf_bytes = create_sample_pdf_bytes()
    text = extract_pdf_text(pdf_bytes)
    assert "Alex Mercer" in text
    assert "TECHNICAL SKILLS" in text
    assert "WORK EXPERIENCE" in text


def test_extract_pdf_text_multi_page(create_sample_pdf_bytes):
    pdf_bytes = create_sample_pdf_bytes(page_count=3)
    text = extract_pdf_text(pdf_bytes)
    assert "Alex Mercer" in text
    assert text.count("Alex Mercer") >= 3


def test_extract_docx_text(create_sample_docx_bytes):
    docx_bytes = create_sample_docx_bytes()
    text = extract_docx_text(docx_bytes)
    assert "Taylor Reed" in text
    assert "SKILLS & TECHNOLOGIES" in text
    assert "Python Professional Cert" in text  # From table cell


def test_extract_pdf_corrupted():
    corrupted_bytes = b"%PDF-1.4\nCorrupted binary rubbish here..."
    with pytest.raises(FileExtractionError):
        extract_pdf_text(corrupted_bytes)


def test_extract_docx_corrupted():
    corrupted_bytes = b"PK\x03\x04Corrupted zip payload..."
    with pytest.raises(FileExtractionError):
        extract_docx_text(corrupted_bytes)


def test_extract_text_from_file_dispatcher(create_sample_pdf_bytes, create_sample_docx_bytes):
    pdf_text = extract_text_from_file("pdf", create_sample_pdf_bytes())
    assert "Alex Mercer" in pdf_text

    docx_text = extract_text_from_file("docx", create_sample_docx_bytes())
    assert "Taylor Reed" in docx_text

    with pytest.raises(FileExtractionError):
        extract_text_from_file("txt", b"Hello world")
