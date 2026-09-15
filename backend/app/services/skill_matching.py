from typing import Dict, List, Set, Tuple, Any
from app.schemas.analysis import SkillMatchDetails, SkillAliasMatch
from app.services.skill_extractor import extract_skills_with_metadata


def evaluate_skill_match(
    resume_text: str,
    resume_skills: List[str],
    required_jd_skills: List[str],
    preferred_jd_skills: List[str],
) -> Tuple[float, List[str], List[str], List[str], SkillMatchDetails, List[str]]:
    """
    Perform deterministic skill matching using set intersection and skill coverage scoring.
    
    Formula:
        Required Skill Coverage = |R ∩ J_required| / |J_required| * 100
        Preferred Skill Coverage = |R ∩ J_preferred| / |J_preferred| * 100
        Skill Score = (0.80 * Required Coverage) + (0.20 * Preferred Coverage)
    
    Returns:
        Tuple[
            skill_score: float (0-100),
            matching_skills: List[str],
            missing_required_skills: List[str],
            missing_preferred_skills: List[str],
            skill_match_details: SkillMatchDetails,
            warnings: List[str]
        ]
    """
    warnings: List[str] = []
    
    set_r = set(resume_skills)
    set_req = set(required_jd_skills)
    set_pref = set(preferred_jd_skills)

    all_jd_skills = set_req | set_pref

    matching_skills = sorted(list(set_r & all_jd_skills))
    missing_required = sorted(list(set_req - set_r))
    missing_preferred = sorted(list(set_pref - set_r))

    # Required skill coverage percentage
    if len(set_req) > 0:
        req_match_pct = (len(set_r & set_req) / len(set_req)) * 100.0
    else:
        req_match_pct = 100.0
        warnings.append("No required skills detected in job description.")

    # Preferred skill coverage percentage
    if len(set_pref) > 0:
        pref_match_pct = (len(set_r & set_pref) / len(set_pref)) * 100.0
    else:
        pref_match_pct = 100.0

    # Composite skill coverage score calculation
    if len(set_req) > 0 and len(set_pref) > 0:
        skill_score = (0.80 * req_match_pct) + (0.20 * pref_match_pct)
    elif len(set_req) > 0:
        skill_score = req_match_pct
    elif len(set_pref) > 0:
        skill_score = pref_match_pct
    else:
        skill_score = 100.0 if len(set_r) > 0 else 0.0
        warnings.append("No skills detected in job description text.")

    # Build alias match details
    _, raw_alias_map = extract_skills_with_metadata(resume_text)
    exact_matches: List[str] = []
    alias_matches: List[SkillAliasMatch] = []

    for skill in matching_skills:
        raw_alias = raw_alias_map.get(skill)
        if raw_alias and raw_alias.lower() != skill.lower():
            alias_matches.append(
                SkillAliasMatch(resume_alias=raw_alias, canonical_name=skill)
            )
        else:
            exact_matches.append(skill)

    details = SkillMatchDetails(
        required_match_percentage=round(req_match_pct, 1),
        preferred_match_percentage=round(pref_match_pct, 1),
        exact_matches=exact_matches,
        alias_matches=alias_matches,
    )

    return (
        round(skill_score, 1),
        matching_skills,
        missing_required,
        missing_preferred,
        details,
        warnings,
    )
