from typing import List
from app.schemas.analysis import (
    AnalysisPreviewResponse,
    ScoreBreakdown,
    ScoreWeights,
)
from app.services.skill_extractor import extract_skills
from app.services.jd_analyzer import analyze_job_description_skills
from app.services.skill_matching import evaluate_skill_match
from app.services.text_similarity import compute_text_similarity
from app.services.experience_analyzer import evaluate_experience_alignment
from app.services.education_analyzer import evaluate_education_alignment
from app.services.ats_analyzer import analyze_ats_quality, generate_ats_recommendations
from app.services.cleaner import clean_text
from app.services.scoring import calculate_composite_score
from app.services.recommender import (
    generate_prioritized_skill_gaps,
    evaluate_role_recommendations,
    generate_unified_recommendations,
)


def generate_deterministic_recommendations(
    missing_required: List[str],
    missing_preferred: List[str],
    ats_breakdown,
    exp_alignment,
    edu_alignment,
) -> List[str]:
    """
    Generate deterministic, rule-based improvement suggestions.
    """
    recs: List[str] = []

    # 1. Missing Required Skills (High Priority)
    if missing_required:
        top_missing = missing_required[:3]
        recs.append(f"Add missing core required skills: {', '.join(top_missing)}.")

    # 2. Missing Preferred Skills (Medium Priority)
    if missing_preferred:
        top_pref = missing_preferred[:3]
        recs.append(f"Consider including preferred skills: {', '.join(top_pref)}.")

    # 3. ATS Structural Recommendations
    if ats_breakdown.details.sections_missing:
        missing_sec_str = ", ".join([s.title() for s in ats_breakdown.details.sections_missing[:3]])
        recs.append(f"Add missing standard sections to your resume: {missing_sec_str}.")

    if ats_breakdown.details.action_verb_score < 70.0:
        recs.append("Strengthen bullet points by starting with action verbs like 'developed', 'engineered', or 'scaled'.")

    if ats_breakdown.details.quantifiable_metrics_score < 70.0:
        recs.append("Include quantifiable numbers and metrics (e.g. 'improved performance by 30%', '500+ users') to demonstrate impact.")

    # 4. Experience & Education Recommendations
    if exp_alignment.status == "below_requirement":
        recs.append("Highlight relevant internship or project experience to address the experience gap.")

    if edu_alignment.status == "below_requirement":
        recs.append("Ensure your academic degree and relevant technical coursework are clearly visible.")

    if not recs:
        recs.append("Great job! Your resume aligns very well with the target position.")

    return recs


def run_resume_job_analysis(
    resume_text: str, job_description_text: str
) -> AnalysisPreviewResponse:
    """
    Main analysis engine pipeline orchestrator.
    Executes skill extraction, JD analysis, Cosine Text Similarity, 
    experience/education alignment, ATS health checks, composite scoring,
    and deterministic recommendations.
    """
    all_warnings: List[str] = []
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(job_description_text)

    # 1. Skill Extraction
    resume_skills = extract_skills(clean_resume)
    jd_skills_dict = analyze_job_description_skills(clean_jd)
    
    req_jd_skills = jd_skills_dict["required_skills"]
    pref_jd_skills = jd_skills_dict["preferred_skills"]

    # 2. Skill Matching
    (
        skill_score,
        matching_skills,
        missing_req,
        missing_pref,
        skill_details,
        skill_warnings,
    ) = evaluate_skill_match(
        resume_text=clean_resume,
        resume_skills=resume_skills,
        required_jd_skills=req_jd_skills,
        preferred_jd_skills=pref_jd_skills,
    )
    all_warnings.extend(skill_warnings)

    # 3. Text Similarity (Normalized Term-Frequency Cosine Similarity)
    text_sim_score, text_sim_details, text_warnings = compute_text_similarity(
        resume_text=clean_resume, job_description_text=clean_jd
    )
    all_warnings.extend(text_warnings)

    # 4. Experience Alignment
    exp_alignment = evaluate_experience_alignment(
        resume_text=clean_resume, job_description_text=clean_jd
    )

    # 5. Education Alignment
    edu_alignment = evaluate_education_alignment(
        resume_text=clean_resume, job_description_text=clean_jd
    )

    # 6. ATS Quality Check
    ats_breakdown = analyze_ats_quality(resume_text=clean_resume)

    # 7. Composite Weighted Score
    weights = ScoreWeights()
    overall_score = calculate_composite_score(
        skill_score=skill_score,
        text_similarity_score=text_sim_score,
        experience_score=exp_alignment.score,
        ats_quality_score=ats_breakdown.score,
        weights=weights,
    )

    # 8. Score Breakdown Object
    score_breakdown = ScoreBreakdown(
        skill_score=skill_score,
        text_similarity_score=text_sim_score,
        experience_score=exp_alignment.score,
        ats_quality_score=ats_breakdown.score,
    )

    # 9. Deterministic Recommendations (Legacy string list preserved for compatibility)
    recommendations = generate_deterministic_recommendations(
        missing_required=missing_req,
        missing_preferred=missing_pref,
        ats_breakdown=ats_breakdown,
        exp_alignment=exp_alignment,
        edu_alignment=edu_alignment,
    )

    # 10. Phase 5 Enhanced Engines:
    # 10a. Prioritized Skill Gaps
    prioritized_skill_gaps = generate_prioritized_skill_gaps(
        missing_required_skills=missing_req,
        missing_preferred_skills=missing_pref,
        job_description_text=clean_jd,
    )

    # 10b. Role Recommendations (Independent from JD match score)
    role_recommendations = evaluate_role_recommendations(
        resume_skills=resume_skills
    )

    # 10c. Actionable ATS Recommendations (with conservative heuristics)
    ats_recommendations = generate_ats_recommendations(
        ats_breakdown=ats_breakdown,
        resume_text=clean_resume,
    )

    # 10d. Unified Recommendations
    unified_recommendations = generate_unified_recommendations(
        skill_gaps=prioritized_skill_gaps,
        ats_recommendations=ats_recommendations,
        experience_alignment=exp_alignment,
        education_alignment=edu_alignment,
    )

    # 11. Assemble Final Response
    return AnalysisPreviewResponse(
        overall_score=overall_score,
        score_breakdown=score_breakdown,
        weights=weights,
        resume_skills=resume_skills,
        required_jd_skills=req_jd_skills,
        preferred_jd_skills=pref_jd_skills,
        matching_skills=matching_skills,
        missing_required_skills=missing_req,
        missing_preferred_skills=missing_pref,
        skill_match_details=skill_details,
        text_similarity_details=text_sim_details,
        experience_alignment=exp_alignment,
        education_alignment=edu_alignment,
        ats_breakdown=ats_breakdown,
        recommendations=recommendations,
        warnings=all_warnings,
        prioritized_skill_gaps=prioritized_skill_gaps,
        role_recommendations=role_recommendations,
        ats_recommendations=ats_recommendations,
        unified_recommendations=unified_recommendations,
    )
