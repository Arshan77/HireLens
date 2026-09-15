from app.services.scoring import calculate_composite_score


def test_calculate_composite_score_exact_weights():
    # Skill = 80, Text = 70, Experience = 90, ATS = 60
    # Expected: 0.40(80) + 0.30(70) + 0.15(90) + 0.15(60) = 32 + 21 + 13.5 + 9 = 75.5
    score = calculate_composite_score(
        skill_score=80.0,
        text_similarity_score=70.0,
        experience_score=90.0,
        ats_quality_score=60.0,
    )
    assert score == 75.5


def test_calculate_composite_score_issue1_regression():
    # Skill = 100.0, Text = 45.2, Experience = 100.0, ATS = 83.3
    # Expected: 0.40(100.0) + 0.30(45.2) + 0.15(100.0) + 0.15(83.3)
    #         = 40.0 + 13.56 + 15.0 + 12.495 = 81.055 -> 81.1
    score = calculate_composite_score(
        skill_score=100.0,
        text_similarity_score=45.2,
        experience_score=100.0,
        ats_quality_score=83.3,
    )
    assert score == 81.1


def test_calculate_composite_score_perfect():
    score = calculate_composite_score(
        skill_score=100.0,
        text_similarity_score=100.0,
        experience_score=100.0,
        ats_quality_score=100.0,
    )
    assert score == 100.0


def test_calculate_composite_score_zero():
    score = calculate_composite_score(
        skill_score=0.0,
        text_similarity_score=0.0,
        experience_score=0.0,
        ats_quality_score=0.0,
    )
    assert score == 0.0
