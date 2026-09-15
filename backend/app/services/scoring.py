from app.schemas.analysis import ScoreBreakdown, ScoreWeights


def calculate_composite_score(
    skill_score: float,
    text_similarity_score: float,
    experience_score: float,
    ats_quality_score: float,
    weights: ScoreWeights = ScoreWeights(),
) -> float:
    """
    Calculate the overall weighted composite match score.
    
    Formula:
        Overall = (w_skill * skill_score) + (w_text * text_sim_score) + 
                  (w_exp * exp_score) + (w_ats * ats_score)
    """
    raw_composite = (
        (weights.skill * skill_score)
        + (weights.text_similarity * text_similarity_score)
        + (weights.experience * experience_score)
        + (weights.ats * ats_quality_score)
    )

    clamped_score = max(0.0, min(100.0, raw_composite))
    return round(clamped_score, 1)
