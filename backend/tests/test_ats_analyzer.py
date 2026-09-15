from app.services.ats_analyzer import analyze_ats_quality


def test_ats_quality_high_score():
    resume = (
        "John Doe\n"
        "Email: john@example.com | Phone: +1-555-0199\n"
        "SUMMARY\n"
        "Passionate engineer.\n"
        "SKILLS\n"
        "Python, React, FastAPI, PostgreSQL\n"
        "WORK EXPERIENCE\n"
        "- Developed REST APIs reducing response latency by 40%.\n"
        "- Engineered scalable services serving 500 users daily.\n"
        "- Optimized queries saving 20 hours of compute time.\n"
        "EDUCATION\n"
        "B.S. in Computer Science\n"
        "PROJECTS\n"
        "- Built full-stack web application.\n"
    )
    result = analyze_ats_quality(resume)
    assert result.score >= 80.0
    assert result.details.section_completeness_score == 100.0
    assert len(result.details.action_verbs_found) >= 3
    assert result.details.metrics_count >= 3


def test_ats_quality_low_score():
    resume = "Just a short note with skills: Python."
    result = analyze_ats_quality(resume)
    assert result.score < 50.0
    assert len(result.details.sections_missing) > 0


def test_ats_quality_empty_text():
    result = analyze_ats_quality("")
    assert result.score == 0.0
    assert result.details.metrics_count == 0
