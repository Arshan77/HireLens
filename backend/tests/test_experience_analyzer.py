from app.services.experience_analyzer import evaluate_experience_alignment


def test_experience_aligned():
    resume = "Software Engineer with 2 years of experience building Python backend services."
    jd = "Requirements: 2+ years of experience in software development."
    result = evaluate_experience_alignment(resume, jd)
    assert result.score == 100.0
    assert result.status == "aligned"
    assert result.required_years == 2.0
    assert result.candidate_years == 2.0


def test_experience_below_requirement():
    resume = "Developer with 1 year of experience in web development."
    jd = "Minimum 3 years of experience required."
    result = evaluate_experience_alignment(resume, jd)
    assert 33.0 <= result.score <= 34.0
    assert result.status == "below_requirement"
    assert result.required_years == 3.0
    assert result.candidate_years == 1.0


def test_experience_exceeds_requirement():
    resume = "Senior Engineer with 5 years of experience."
    jd = "2 years of experience required."
    result = evaluate_experience_alignment(resume, jd)
    assert result.score == 100.0
    assert result.status == "exceeds_requirement"


def test_experience_fresher_entry_level():
    resume = "Recent graduate seeking entry-level developer role."
    jd = "Freshers welcome! Entry level Software Engineer."
    result = evaluate_experience_alignment(resume, jd)
    assert result.score == 100.0
    assert result.status == "aligned"
    assert result.required_years == 0.0


def test_experience_unknown():
    resume = "Passionate developer who loves coding."
    jd = "Looking for a proactive developer."
    result = evaluate_experience_alignment(resume, jd)
    assert result.score == 75.0
    assert result.status == "unknown"
