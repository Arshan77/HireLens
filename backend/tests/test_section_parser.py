from app.services.section_parser import parse_resume_sections


def test_parse_resume_sections_full():
    sample_text = (
        "John Doe\n"
        "Email: john@example.com | Phone: 123-456-7890\n"
        "SUMMARY\n"
        "Experienced Developer\n"
        "TECHNICAL SKILLS\n"
        "Python, React, FastAPI\n"
        "WORK EXPERIENCE\n"
        "Software Engineer at ACME Corp\n"
        "ACADEMIC BACKGROUND\n"
        "BS Computer Science\n"
        "KEY PROJECTS\n"
        "HireLens Web Application\n"
        "CERTIFICATIONS\n"
        "AWS Cloud Practitioner\n"
    )

    sections = parse_resume_sections(sample_text)

    assert "john@example.com" in sections.contact
    assert "Experienced Developer" in sections.summary
    assert "Python, React, FastAPI" in sections.skills
    assert "ACME Corp" in sections.experience
    assert "BS Computer Science" in sections.education
    assert "HireLens Web Application" in sections.projects
    assert "AWS Cloud Practitioner" in sections.certifications


def test_parse_resume_sections_missing_sections():
    sample_text = (
        "Jane Smith\n"
        "SKILLS\n"
        "Java, Python\n"
        "EDUCATION\n"
        "B.Tech Computer Science\n"
    )

    sections = parse_resume_sections(sample_text)

    assert "Jane Smith" in sections.contact
    assert sections.summary == ""
    assert "Java, Python" in sections.skills
    assert sections.experience == ""
    assert "B.Tech Computer Science" in sections.education
    assert sections.projects == ""
    assert sections.certifications == ""


def test_parse_resume_sections_empty_text():
    sections = parse_resume_sections("")
    assert sections.contact == ""
    assert sections.skills == ""
    assert sections.experience == ""
