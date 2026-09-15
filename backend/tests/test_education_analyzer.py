from app.services.education_analyzer import evaluate_education_alignment


def test_education_matching():
    resume = "Education: B.Tech in Computer Engineering (2020-2024)"
    jd = "Requirements: Bachelor's degree in Computer Science or related field."
    result = evaluate_education_alignment(resume, jd)
    assert result.score == 100.0
    assert result.status == "aligned"


def test_education_exceeds_or_aligned_higher():
    resume = "Education: Master's degree (M.Tech) in Computer Science"
    jd = "Requires a Bachelor's degree."
    result = evaluate_education_alignment(resume, jd)
    assert result.score == 100.0
    assert result.status == "aligned"


def test_education_below_requirement():
    resume = "Education: B.Tech in Computer Engineering"
    jd = "Requires a Master's degree (M.Tech/MCA) in Computer Science."
    result = evaluate_education_alignment(resume, jd)
    assert result.score == 50.0
    assert result.status == "below_requirement"


def test_education_unknown():
    resume = "Self-taught developer with strong project portfolio."
    jd = "Join our software engineering team."
    result = evaluate_education_alignment(resume, jd)
    assert result.score == 75.0
    assert result.status == "unknown"
