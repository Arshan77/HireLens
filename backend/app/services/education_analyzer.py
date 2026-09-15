import re
from typing import Tuple, Optional, Dict
from app.schemas.analysis import EducationAlignment

DEGREE_LEVELS: Dict[str, Tuple[int, str]] = {
    "phd": (3, "Doctorate / PhD"),
    "ph.d": (3, "Doctorate / PhD"),
    "doctorate": (3, "Doctorate / PhD"),
    "m.tech": (2, "Master's Degree"),
    "mtech": (2, "Master's Degree"),
    "m.e": (2, "Master's Degree"),
    "me": (2, "Master's Degree"),
    "m.sc": (2, "Master's Degree"),
    "msc": (2, "Master's Degree"),
    "m.s": (2, "Master's Degree"),
    "ms": (2, "Master's Degree"),
    "mca": (2, "Master's Degree"),
    "master": (2, "Master's Degree"),
    "masters": (2, "Master's Degree"),
    "b.tech": (1, "Bachelor's Degree"),
    "btech": (1, "Bachelor's Degree"),
    "b.e": (1, "Bachelor's Degree"),
    "be": (1, "Bachelor's Degree"),
    "b.sc": (1, "Bachelor's Degree"),
    "bsc": (1, "Bachelor's Degree"),
    "b.s": (1, "Bachelor's Degree"),
    "bs": (1, "Bachelor's Degree"),
    "b.a": (1, "Bachelor's Degree"),
    "ba": (1, "Bachelor's Degree"),
    "bca": (1, "Bachelor's Degree"),
    "bachelor": (1, "Bachelor's Degree"),
    "bachelors": (1, "Bachelor's Degree"),
}

DEGREE_PATTERNS = [
    re.compile(r"\b(Ph\.?D\.?|Doctorate)\b", re.IGNORECASE),
    re.compile(r"\b(M\.?Tech|M\.?E|M\.?Sc|M\.?S|MCA|Master's|Masters|Master)\b", re.IGNORECASE),
    re.compile(r"\b(B\.?Tech|B\.?E|B\.?Sc|B\.?S|B\.?A|BCA|Bachelor's|Bachelors|Bachelor)\b", re.IGNORECASE),
]


def extract_degree_level(text: str) -> Optional[Tuple[int, str]]:
    """
    Extract highest degree level detected in text.
    Returns Tuple[rank: int, canonical_degree_name: str] or None.
    """
    if not text:
        return None

    highest_rank = 0
    highest_degree = None

    for pattern in DEGREE_PATTERNS:
        match = pattern.search(text)
        if match:
            raw_match = match.group(1).lower().replace("'", "").strip()
            level_tuple = DEGREE_LEVELS.get(raw_match)
            if level_tuple:
                rank, name = level_tuple
                if rank > highest_rank:
                    highest_rank = rank
                    highest_degree = name

    if highest_degree:
        return highest_rank, highest_degree

    return None


def evaluate_education_alignment(
    resume_text: str, job_description_text: str
) -> EducationAlignment:
    """
    Evaluate education alignment between candidate resume and job description.
    """
    req_tuple = extract_degree_level(job_description_text)
    cand_tuple = extract_degree_level(resume_text)

    req_degree = req_tuple[1] if req_tuple else None
    cand_degree = cand_tuple[1] if cand_tuple else None

    if req_tuple and cand_tuple:
        req_rank = req_tuple[0]
        cand_rank = cand_tuple[0]

        if cand_rank >= req_rank:
            return EducationAlignment(
                required_degree=req_degree,
                candidate_degree=cand_degree,
                score=100.0,
                status="aligned",
                explanation=f"Candidate degree ({cand_degree}) satisfies requirement ({req_degree}).",
            )
        else:
            return EducationAlignment(
                required_degree=req_degree,
                candidate_degree=cand_degree,
                score=50.0,
                status="below_requirement",
                explanation=f"Candidate degree ({cand_degree}) is below required level ({req_degree}).",
            )

    if req_degree and not cand_degree:
        return EducationAlignment(
            required_degree=req_degree,
            candidate_degree=None,
            score=75.0,
            status="unknown",
            explanation=f"Job requires {req_degree}, but candidate degree was not explicitly detected in resume.",
        )

    if cand_degree and not req_degree:
        return EducationAlignment(
            required_degree=None,
            candidate_degree=cand_degree,
            score=100.0,
            status="aligned",
            explanation=f"Candidate holds {cand_degree}; job description specified no explicit degree requirement.",
        )

    return EducationAlignment(
        required_degree=None,
        candidate_degree=None,
        score=75.0,
        status="unknown",
        explanation="Education requirement and candidate degree not explicitly detected in text.",
    )
