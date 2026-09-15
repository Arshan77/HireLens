import re
from typing import Dict, List, Set, Optional, Tuple, Any
from app.schemas.analysis import (
    SkillGapRecommendation,
    RoleRecommendation,
    AtsRecommendation,
    UnifiedRecommendation,
    ExperienceAlignment,
    EducationAlignment,
)
from app.services.skill_taxonomy import normalize_skill_name, get_skill_category


# =====================================================================
# 1. ROLE TAXONOMY DEFINITION
# =====================================================================

ROLE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Backend Developer": {
        "core_skills": [
            "Python", "Java", "Node.js", "Go", "FastAPI", "Django",
            "Spring Boot", "Express.js", "SQL", "PostgreSQL", "MySQL", "REST API"
        ],
        "supporting_skills": ["Docker", "Redis", "Linux", "CI/CD", "Git"],
        "description": "Server-side logic, API engineering, database design, and backend infrastructure.",
    },
    "Frontend Developer": {
        "core_skills": [
            "JavaScript", "TypeScript", "React", "HTML", "CSS",
            "Next.js", "Angular", "Vue", "Tailwind CSS"
        ],
        "supporting_skills": ["Git", "REST API", "GraphQL", "Postman"],
        "description": "User interface engineering, responsive web applications, and modern component architecture.",
    },
    "Full Stack Developer": {
        "core_skills": [
            "React", "JavaScript", "TypeScript", "Node.js", "Python",
            "HTML", "CSS", "SQL", "REST API"
        ],
        "supporting_skills": ["Docker", "Git", "PostgreSQL", "MongoDB", "Redis"],
        "description": "End-to-end web application development encompassing both client-side UI and backend APIs.",
    },
    "Python Developer": {
        "core_skills": [
            "Python", "FastAPI", "Django", "Flask", "SQL", "PostgreSQL"
        ],
        "supporting_skills": ["Docker", "Git", "Linux", "Redis", "NumPy", "Pandas"],
        "description": "Specialized Python application development, web backends, automation scripting, and data pipelines.",
    },
    "Java Developer": {
        "core_skills": [
            "Java", "Spring Boot", "SQL", "MySQL", "PostgreSQL", "REST API"
        ],
        "supporting_skills": ["Docker", "Git", "Linux", "CI/CD"],
        "description": "Enterprise Java application development, microservices architecture, and scalable server systems.",
    },
    "Data Analyst": {
        "core_skills": [
            "SQL", "Python", "Pandas", "NumPy", "Matplotlib", "MySQL", "PostgreSQL"
        ],
        "supporting_skills": ["Git", "scikit-learn"],
        "description": "Data querying, statistical analysis, trend exploration, and business metric visualization.",
    },
    "Machine Learning Engineer": {
        "core_skills": [
            "Python", "scikit-learn", "TensorFlow", "PyTorch",
            "Machine Learning", "Deep Learning", "NumPy", "Pandas"
        ],
        "supporting_skills": ["Docker", "SQL", "Git", "Linux"],
        "description": "Predictive modeling, neural network architectures, machine learning pipelines, and AI engineering.",
    },
    "Software Engineer": {
        "core_skills": [
            "Python", "Java", "C++", "JavaScript", "SQL", "Git", "REST API"
        ],
        "supporting_skills": ["Docker", "Linux", "CI/CD", "Agile"],
        "description": "Core software development, system design patterns, algorithm optimization, and software lifecycle.",
    },
}


# =====================================================================
# 2. DETERMINISTIC ROLE RECOMMENDATION ENGINE
# =====================================================================

def compute_role_score(
    resume_skills: List[str], role_name: str
) -> Tuple[float, str, List[str], List[str], str]:
    """
    Calculate deterministic role fit score for a specific role.
    
    Formula:
        Role Score = 0.70 * core_coverage + 0.30 * supporting_coverage
        scaled to 0 - 100.
        
        core_coverage = matched_core_skills / total_core_skills
        supporting_coverage = matched_supporting_skills / total_supporting_skills
        
    Handles empty skill sets safely: if total_skills == 0, coverage = 0.0.
    """
    role_def = ROLE_TAXONOMY.get(role_name)
    if not role_def:
        return 0.0, "Skills to strengthen", [], [], "Role definition not found."

    norm_resume_skills = {normalize_skill_name(s) for s in resume_skills if s and s.strip()}
    core_skills = [normalize_skill_name(s) for s in role_def["core_skills"]]
    supp_skills = [normalize_skill_name(s) for s in role_def["supporting_skills"]]

    set_core = set(core_skills)
    set_supp = set(supp_skills)

    matched_core = sorted(list(norm_resume_skills & set_core))
    matched_supp = sorted(list(norm_resume_skills & set_supp))
    missing_core = sorted(list(set_core - norm_resume_skills))

    core_coverage = len(matched_core) / float(len(set_core)) if len(set_core) > 0 else 0.0
    supp_coverage = len(matched_supp) / float(len(set_supp)) if len(set_supp) > 0 else 0.0

    raw_score = (0.70 * core_coverage + 0.30 * supp_coverage) * 100.0
    score = round(raw_score, 1)

    # Standardized fit classification
    if score >= 65.0:
        fit_level = "Strong fit"
    elif score >= 40.0:
        fit_level = "Good fit"
    elif score >= 20.0:
        fit_level = "Moderate fit"
    else:
        fit_level = "Skills to strengthen"

    matched_all = sorted(list(set(matched_core) | set(matched_supp)))

    if matched_all:
        reason = (
            f"Detected {len(matched_core)} core skill(s) and {len(matched_supp)} supporting skill(s) "
            f"aligning with {role_name} requirements."
        )
    else:
        reason = f"No direct skill alignment detected for {role_name} in candidate resume."

    return score, fit_level, matched_all, missing_core, reason


def evaluate_role_recommendations(
    resume_skills: List[str]
) -> List[RoleRecommendation]:
    """
    Evaluate candidate's extracted skills against all supported roles in the taxonomy.
    Returns ranked list of RoleRecommendation sorted descending by score.
    Deterministic tie-breaker uses alphabetical role name.
    """
    recommendations: List[RoleRecommendation] = []

    for role_name in sorted(ROLE_TAXONOMY.keys()):
        score, fit_level, matched, missing_core, reason = compute_role_score(
            resume_skills=resume_skills, role_name=role_name
        )
        recommendations.append(
            RoleRecommendation(
                role=role_name,
                score=score,
                fit_level=fit_level,
                matched_skills=matched,
                missing_core_skills=missing_core,
                reason=reason,
            )
        )

    # Sort descending by score, secondary tie-breaker alphabetical role
    recommendations.sort(key=lambda r: (-r.score, r.role))
    return recommendations


# =====================================================================
# 3. PRIORITIZED SKILL GAP ENGINE
# =====================================================================

def count_skill_occurrences_in_text(skill: str, text: str) -> int:
    """Count case-insensitive occurrences of skill name in text."""
    pattern = r"\b" + re.escape(skill.lower()) + r"\b"
    return len(re.findall(pattern, text.lower()))


def generate_prioritized_skill_gaps(
    missing_required_skills: List[str],
    missing_preferred_skills: List[str],
    job_description_text: str = "",
) -> List[SkillGapRecommendation]:
    """
    Generate deterministic, prioritized skill gap recommendations.
    
    Rules:
    - Only recommend skills present in the job description.
    - Avoid duplicates caused by aliases by canonicalizing all skills.
    - Priority Assignment:
        HIGH:
            - Required skill in core category (language, backend, frontend, database, data_ai)
            - Or required skill appearing >= 2 times in the JD
        MEDIUM:
            - Required skill in secondary category (tools, devops)
            - Preferred skill in core category or appearing >= 2 times in the JD
        LOW:
            - Preferred skill in secondary category
    """
    gaps: List[SkillGapRecommendation] = []
    seen_skills: Set[str] = set()

    core_categories = {"language", "backend", "frontend", "database", "data_ai"}

    # 1. Process Required Missing Skills
    for raw_skill in missing_required_skills:
        canonical = normalize_skill_name(raw_skill)
        if canonical in seen_skills:
            continue
        seen_skills.add(canonical)

        category = get_skill_category(canonical)
        freq = count_skill_occurrences_in_text(canonical, job_description_text)

        if category in core_categories or freq >= 2:
            priority = "high"
        else:
            priority = "medium"

        reason = (
            f"{canonical} is listed as a required {category} skill in the job description."
        )
        action = (
            f"Add a relevant {canonical} project or demonstrate hands-on {canonical} experience before applying."
        )

        gaps.append(
            SkillGapRecommendation(
                skill=canonical,
                category=category,
                priority=priority,
                required_or_preferred="required",
                reason=reason,
                action=action,
            )
        )

    # 2. Process Preferred Missing Skills
    for raw_skill in missing_preferred_skills:
        canonical = normalize_skill_name(raw_skill)
        if canonical in seen_skills:
            continue
        seen_skills.add(canonical)

        category = get_skill_category(canonical)
        freq = count_skill_occurrences_in_text(canonical, job_description_text)

        if category in core_categories or freq >= 2:
            priority = "medium"
        else:
            priority = "low"

        reason = (
            f"{canonical} is specified as a preferred/nice-to-have {category} skill in the job posting."
        )
        action = (
            f"Consider completing a tutorial or adding a portfolio sample highlighting {canonical} to strengthen your profile."
        )

        gaps.append(
            SkillGapRecommendation(
                skill=canonical,
                category=category,
                priority=priority,
                required_or_preferred="preferred",
                reason=reason,
                action=action,
            )
        )

    # Deterministic sort: high priority first, then medium, then low, then alphabetical skill
    prio_map = {"high": 0, "medium": 1, "low": 2}
    gaps.sort(key=lambda g: (prio_map.get(g.priority, 3), g.skill))

    return gaps


# =====================================================================
# 4. UNIFIED RECOMMENDATIONS ENGINE
# =====================================================================

def generate_unified_recommendations(
    skill_gaps: List[SkillGapRecommendation],
    ats_recommendations: List[AtsRecommendation],
    experience_alignment: Optional[ExperienceAlignment] = None,
    education_alignment: Optional[EducationAlignment] = None,
) -> List[UnifiedRecommendation]:
    """
    Synthesize all feedback dimensions into a single unified recommendation list:
    - skill_gap (from prioritized skill gaps)
    - ats / structure (from ATS analysis)
    - content (from experience and education alignment)
    
    Deterministic ordering: High priority first, then Medium, then Low.
    """
    unified: List[UnifiedRecommendation] = []

    # 1. Skill Gap Recommendations
    for gap in skill_gaps:
        unified.append(
            UnifiedRecommendation(
                type="skill_gap",
                priority=gap.priority,
                title=f"Acquire / Highlight {gap.skill}",
                reason=gap.reason,
                action=gap.action,
                evidence={
                    "skill": gap.skill,
                    "category": gap.category,
                    "requirement": gap.required_or_preferred,
                },
            )
        )

    # 2. ATS Recommendations
    for ats_rec in ats_recommendations:
        rec_type = "structure" if ats_rec.category == "sections" else "ats"
        unified.append(
            UnifiedRecommendation(
                type=rec_type,
                priority=ats_rec.priority,
                title=ats_rec.title,
                reason=ats_rec.issue,
                action=ats_rec.action,
                evidence={"ats_category": ats_rec.category},
            )
        )

    # 3. Experience Alignment Recommendations
    if experience_alignment and experience_alignment.status == "below_requirement":
        unified.append(
            UnifiedRecommendation(
                type="content",
                priority="high",
                title="Address Experience Gap",
                reason=experience_alignment.explanation,
                action="Emphasize relevant project work, internships, or open-source contributions to showcase equivalent practical competency.",
                evidence={
                    "required_years": experience_alignment.required_years,
                    "candidate_years": experience_alignment.candidate_years,
                },
            )
        )

    # 4. Education Alignment Recommendations
    if education_alignment and education_alignment.status == "below_requirement":
        unified.append(
            UnifiedRecommendation(
                type="content",
                priority="medium",
                title="Clarify Educational Credentials",
                reason=education_alignment.explanation,
                action="Ensure your degree title, major, coursework, and relevant certifications are explicitly stated.",
                evidence={
                    "required_degree": education_alignment.required_degree,
                    "candidate_degree": education_alignment.candidate_degree,
                },
            )
        )

    # Deterministic Sort: High -> Medium -> Low, then by type, then by title
    prio_order = {"high": 0, "medium": 1, "low": 2}
    unified.sort(key=lambda u: (prio_order.get(u.priority, 3), u.type, u.title))

    return unified
