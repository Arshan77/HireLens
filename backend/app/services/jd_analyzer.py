import re
from typing import Dict, List, Tuple, Set
from app.services.skill_extractor import extract_skills


PREFERRED_KEYWORDS_PATTERN = re.compile(
    r"(?:preferred|nice\s+to\s+have|bonus|plus|desirable|advantage|good\s+to\s+have|optional)",
    re.IGNORECASE,
)

REQUIRED_KEYWORDS_PATTERN = re.compile(
    r"(?:required|must\s+have|mandatory|should\s+have|strong\s+knowledge|proficiency|qualifications|requirements|essential)",
    re.IGNORECASE,
)


def analyze_job_description_skills(jd_text: str) -> Dict[str, List[str]]:
    """
    Parse Job Description text and categorize extracted skills into:
    - required_skills: Skills required for the role
    - preferred_skills: Skills preferred/nice-to-have for the role
    
    Fallback Behavior:
    If no contextual preference indicators are detected, all extracted skills default to required_skills.
    """
    if not jd_text or not jd_text.strip():
        return {"required_skills": [], "preferred_skills": []}

    lines = jd_text.split("\n")
    
    required_blocks: List[str] = []
    preferred_blocks: List[str] = []
    
    current_mode = "required"  # Default mode

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check line for section mode switches
        if PREFERRED_KEYWORDS_PATTERN.search(stripped) and len(stripped) <= 60:
            current_mode = "preferred"
            preferred_blocks.append(stripped)
            continue
        elif REQUIRED_KEYWORDS_PATTERN.search(stripped) and len(stripped) <= 60:
            current_mode = "required"
            required_blocks.append(stripped)
            continue

        if current_mode == "preferred":
            preferred_blocks.append(stripped)
        else:
            required_blocks.append(stripped)

    # Extract skills from respective text blocks
    required_text = "\n".join(required_blocks)
    preferred_text = "\n".join(preferred_blocks)

    req_skills = set(extract_skills(required_text))
    pref_skills = set(extract_skills(preferred_text))

    # If any skill was extracted in preferred_text that was also in required_text,
    # keep required priority
    pref_skills = pref_skills - req_skills

    # Fallback check: If preferred_text was empty or no split occurred, run extract_skills on full text
    if not req_skills and not pref_skills:
        all_skills = extract_skills(jd_text)
        return {"required_skills": all_skills, "preferred_skills": []}

    return {
        "required_skills": sorted(list(req_skills)),
        "preferred_skills": sorted(list(pref_skills)),
    }
