from app.services.cleaner import clean_text


def test_clean_text_whitespace_normalization():
    raw = "John   Doe  \t  -   Software Engineer\r\nEmail:\xa0john@example.com"
    cleaned = clean_text(raw)
    assert "John Doe - Software Engineer" in cleaned
    assert "Email: john@example.com" in cleaned


def test_clean_text_multiple_newlines():
    raw = "Header\n\n\n\n\nSubheader\n\n\nContent"
    cleaned = clean_text(raw)
    assert cleaned == "Header\n\nSubheader\n\nContent"


def test_clean_text_empty_input():
    assert clean_text("") == ""
    assert clean_text("   \n\n  ") == ""


def test_clean_text_preserves_bullets_punctuation():
    raw = (
        "SKILLS\n"
        "• Python, FastAPI & React\n"
        "- PostgreSQL / Docker / Git\n"
        "Contact: +1 (555) 019-2834 | john.doe@example.com"
    )
    cleaned = clean_text(raw)
    assert "• Python, FastAPI & React" in cleaned
    assert "- PostgreSQL / Docker / Git" in cleaned
    assert "john.doe@example.com" in cleaned
