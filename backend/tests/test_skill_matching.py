from app.services.skill_matching import evaluate_skill_match


def test_evaluate_skill_match_100_percent():
    resume_text = "Proficient in Python, FastAPI, Docker, and PostgreSQL."
    resume_skills = ["Python", "FastAPI", "Docker", "PostgreSQL"]
    required_jd_skills = ["Python", "FastAPI", "Docker", "PostgreSQL"]
    preferred_jd_skills = []

    score, matching, missing_req, missing_pref, details, warnings = evaluate_skill_match(
        resume_text=resume_text,
        resume_skills=resume_skills,
        required_jd_skills=required_jd_skills,
        preferred_jd_skills=preferred_jd_skills,
    )

    assert score == 100.0
    assert len(matching) == 4
    assert len(missing_req) == 0
    assert len(missing_pref) == 0


def test_evaluate_skill_match_0_percent():
    resume_text = "Experienced in HTML, CSS, and Photoshop."
    resume_skills = ["HTML", "CSS"]
    required_jd_skills = ["Python", "FastAPI", "PostgreSQL"]
    preferred_jd_skills = []

    score, matching, missing_req, missing_pref, details, warnings = evaluate_skill_match(
        resume_text=resume_text,
        resume_skills=resume_skills,
        required_jd_skills=required_jd_skills,
        preferred_jd_skills=preferred_jd_skills,
    )

    assert score == 0.0
    assert len(matching) == 0
    assert len(missing_req) == 3


def test_evaluate_skill_match_partial_and_preferred():
    resume_text = "Skilled in Python, FastAPI, and Postgres."
    resume_skills = ["Python", "FastAPI", "PostgreSQL"]
    required_jd_skills = ["Python", "FastAPI", "Docker"]  # 2 of 3 matched = 66.67%
    preferred_jd_skills = ["PostgreSQL", "Redis"]        # 1 of 2 matched = 50%

    score, matching, missing_req, missing_pref, details, warnings = evaluate_skill_match(
        resume_text=resume_text,
        resume_skills=resume_skills,
        required_jd_skills=required_jd_skills,
        preferred_jd_skills=preferred_jd_skills,
    )

    # 0.8 * 66.67 + 0.2 * 50 = 53.33 + 10 = 63.3
    assert 63.0 <= score <= 64.0
    assert "Python" in matching
    assert "FastAPI" in matching
    assert "PostgreSQL" in matching
    assert "Docker" in missing_req
    assert "Redis" in missing_pref


def test_evaluate_skill_match_no_jd_skills():
    resume_text = "Python, Java"
    resume_skills = ["Python", "Java"]
    required_jd_skills = []
    preferred_jd_skills = []

    score, matching, missing_req, missing_pref, details, warnings = evaluate_skill_match(
        resume_text=resume_text,
        resume_skills=resume_skills,
        required_jd_skills=required_jd_skills,
        preferred_jd_skills=preferred_jd_skills,
    )

    assert score == 100.0
    assert len(warnings) > 0
