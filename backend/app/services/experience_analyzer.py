import re
from typing import Tuple, Optional
from app.schemas.analysis import ExperienceAlignment

FRESHER_PATTERNS = re.compile(
    r"(?:freshers?\s+welcome|entry\s+level|0\s*-\s*1\s*years?|no\s+experience\s+required)",
    re.IGNORECASE,
)

JD_EXP_PATTERNS = [
    re.compile(r"(\d+)\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs?)(?:\s+of)?\s+experience", re.IGNORECASE),
    re.compile(r"minimum\s+(\d+)\s*(?:years?|yrs?)", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s+required", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s+in", re.IGNORECASE),
]

RESUME_EXP_PATTERNS = [
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s+in\s+software", re.IGNORECASE),
    re.compile(r"(\d+)\+?\s*yrs?\s+exp", re.IGNORECASE),
]


def extract_required_years(jd_text: str) -> Optional[float]:
    """Extract required years of experience from job description."""
    if not jd_text:
        return None

    if FRESHER_PATTERNS.search(jd_text):
        return 0.0

    for pattern in JD_EXP_PATTERNS:
        match = pattern.search(jd_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    return None


def extract_candidate_years(resume_text: str) -> Optional[float]:
    """Extract estimated years of experience from candidate resume."""
    if not resume_text:
        return None

    # Check explicit statement first
    for pattern in RESUME_EXP_PATTERNS:
        match = pattern.search(resume_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    # Check date range heuristics e.g., "2021 - 2024" or "2022 - Present"
    date_ranges = re.findall(r"\b(20\d\d)\s*-\s*(20\d\d|Present|Current)\b", resume_text, re.IGNORECASE)
    total_years = 0.0
    current_year = 2026

    for start_str, end_str in date_ranges:
        try:
            start_yr = float(start_str)
            end_yr = current_year if end_str.lower() in ("present", "current") else float(end_str)
            diff = max(0.0, end_yr - start_yr)
            if 0 < diff <= 15:  # Avoid erroneous large numbers
                total_years += diff
        except ValueError:
            pass

    if total_years > 0:
        return round(total_years, 1)

    return None


def evaluate_experience_alignment(
    resume_text: str, job_description_text: str
) -> ExperienceAlignment:
    """
    Deterministically evaluate candidate experience alignment against job description requirements.
    """
    req_years = extract_required_years(job_description_text)
    cand_years = extract_candidate_years(resume_text)

    # 1. Fresher / Entry Level
    if req_years == 0.0:
        cand_val = cand_years if cand_years is not None else 0.0
        return ExperienceAlignment(
            required_years=0.0,
            candidate_years=cand_val,
            score=100.0,
            status="aligned",
            explanation="Position is suitable for entry-level candidates/freshers.",
        )

    # 2. Required years extracted
    if req_years is not None:
        if cand_years is not None:
            if cand_years >= req_years:
                status_str = "aligned" if cand_years == req_years else "exceeds_requirement"
                return ExperienceAlignment(
                    required_years=req_years,
                    candidate_years=cand_years,
                    score=100.0,
                    status=status_str,
                    explanation=f"Candidate experience ({cand_years} yrs) meets or exceeds requirement ({req_years} yrs).",
                )
            else:
                pct = round((cand_years / req_years) * 100.0, 1)
                return ExperienceAlignment(
                    required_years=req_years,
                    candidate_years=cand_years,
                    score=pct,
                    status="below_requirement",
                    explanation=f"Candidate experience ({cand_years} yrs) is below requirement ({req_years} yrs).",
                )
        else:
            return ExperienceAlignment(
                required_years=req_years,
                candidate_years=None,
                score=75.0,
                status="unknown",
                explanation=f"Job requires {req_years} yrs experience, but candidate experience could not be confidently calculated from resume text.",
            )

    # 3. Required years not extracted
    cand_val = cand_years if cand_years is not None else None
    return ExperienceAlignment(
        required_years=None,
        candidate_years=cand_val,
        score=75.0,
        status="unknown",
        explanation="Experience requirement could not be confidently extracted from job description text.",
    )
