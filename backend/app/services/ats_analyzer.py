import re
from typing import Dict, List, Set, Tuple
from app.schemas.analysis import AtsQualityBreakdown, AtsDetailBreakdown, AtsRecommendation
from app.services.section_parser import parse_resume_sections

ACTION_VERBS_LIST: List[str] = [
    "developed", "engineered", "implemented", "designed", "optimized",
    "built", "automated", "analyzed", "deployed", "improved",
    "integrated", "created", "scaled", "led", "architected",
    "configured", "orchestrated", "managed", "reduced", "increased",
    "refactored", "spearheaded", "accelerated", "enhanced", "launched",
]

METRICS_PATTERNS = [
    re.compile(r"\b\d+%"),
    re.compile(r"\b\d+\s+(?:users|customers|clients|requests|records|hours|days|weeks|months|percent|x)\b", re.IGNORECASE),
    re.compile(r"[\$₹€£]\s*\d+"),
    re.compile(r"\b\d+\s*(?:ms|sec|seconds|x|fold)\b", re.IGNORECASE),
]


def analyze_ats_quality(resume_text: str) -> AtsQualityBreakdown:
    """
    Deterministically evaluate ATS Quality Health Score based on:
    1. Section Completeness (50%)
    2. Action Verb Usage (25%)
    3. Quantifiable Metrics (25%)
    """
    if not resume_text or not resume_text.strip():
        details = AtsDetailBreakdown(
            section_completeness_score=0.0,
            action_verb_score=0.0,
            quantifiable_metrics_score=0.0,
            sections_found=[],
            sections_missing=["contact", "summary", "skills", "experience", "education", "projects"],
            action_verbs_found=[],
            metrics_count=0,
        )
        return AtsQualityBreakdown(score=0.0, details=details)

    # 1. Section Completeness Check
    parsed_sections = parse_resume_sections(resume_text)
    standard_sections = ["contact", "summary", "skills", "experience", "education", "projects"]
    
    sections_found: List[str] = []
    sections_missing: List[str] = []

    for sec in standard_sections:
        content = getattr(parsed_sections, sec, "")
        if content and len(content.strip()) > 5:
            sections_found.append(sec)
        else:
            sections_missing.append(sec)

    section_score = (len(sections_found) / float(len(standard_sections))) * 100.0

    # 2. Action Verb Usage Check
    text_lower = resume_text.lower()
    verbs_found: Set[str] = set()

    for verb in ACTION_VERBS_LIST:
        pattern = r"\b" + verb + r"\b"
        if re.search(pattern, text_lower):
            verbs_found.add(verb)

    # 5+ distinct action verbs = 100% score
    verb_ratio = min(1.0, len(verbs_found) / 5.0)
    verb_score = verb_ratio * 100.0

    # 3. Quantifiable Metrics Check
    metrics_count = 0
    for pattern in METRICS_PATTERNS:
        matches = pattern.findall(resume_text)
        metrics_count += len(matches)

    # 3+ quantifiable metrics = 100% score
    metric_ratio = min(1.0, metrics_count / 3.0)
    metric_score = metric_ratio * 100.0

    # 4. Composite ATS Score Calculation
    overall_ats_score = (0.50 * section_score) + (0.25 * verb_score) + (0.25 * metric_score)

    details = AtsDetailBreakdown(
        section_completeness_score=round(section_score, 1),
        action_verb_score=round(verb_score, 1),
        quantifiable_metrics_score=round(metric_score, 1),
        sections_found=sections_found,
        sections_missing=sections_missing,
        action_verbs_found=sorted(list(verbs_found)),
        metrics_count=metrics_count,
    )

    return AtsQualityBreakdown(
        score=round(overall_ats_score, 1),
        details=details,
    )


def generate_ats_recommendations(
    ats_breakdown: AtsQualityBreakdown, resume_text: str
) -> List[AtsRecommendation]:
    """
    Generate actionable, conservative ATS recommendations based on detected
    structure, action verbs, quantifiable metrics, and HireLens length heuristics.
    
    Adheres strictly to factual, non-subjective phrasing without claiming
    definitive automated ATS rejection.
    """
    recommendations: List[AtsRecommendation] = []
    
    if not resume_text or not resume_text.strip():
        recommendations.append(
            AtsRecommendation(
                category="sections",
                priority="high",
                title="Resume Content Required",
                issue="The provided resume text is empty or unreadable.",
                action="Upload a readable PDF or DOCX file with standard resume sections.",
            )
        )
        return recommendations

    details = ats_breakdown.details
    missing = details.sections_missing

    # 1. Section Recommendations
    section_advice = {
        "contact": (
            "high",
            "Add Contact Information",
            "No standard contact section was identified by the parser.",
            "Include your full name, email, phone number, and location at the top of your resume.",
        ),
        "skills": (
            "high",
            "Include a Dedicated Skills Section",
            "No standard technical skills section was detected.",
            "Add a clear skills section categorized by languages, frameworks, databases, and tools.",
        ),
        "experience": (
            "high",
            "Add Work or Internship Experience",
            "No work experience or internship section was detected.",
            "Include a professional experience section with role titles, organization names, dates, and bulleted achievements.",
        ),
        "education": (
            "high",
            "Add Education Credentials",
            "No standard education section was detected.",
            "List your degree, major/specialization, university/college, and graduation year.",
        ),
        "projects": (
            "medium",
            "Add Technical Projects",
            "No dedicated projects section was detected.",
            "Include technical projects demonstrating practical implementation of your core skills.",
        ),
        "summary": (
            "low",
            "Consider Adding a Professional Summary",
            "No professional summary or objective was detected.",
            "Consider adding a brief 2-3 line summary highlighting your technical focus and top qualifications.",
        ),
    }

    for sec in missing:
        if sec in section_advice:
            prio, title, issue, action = section_advice[sec]
            recommendations.append(
                AtsRecommendation(
                    category="sections",
                    priority=prio,
                    title=title,
                    issue=issue,
                    action=action,
                )
            )

    # 2. Action Verb Recommendations
    if details.action_verb_score < 70.0:
        recommendations.append(
            AtsRecommendation(
                category="action_verbs",
                priority="medium",
                title="Strengthen Action Verb Usage",
                issue=f"Detected {len(details.action_verbs_found)} strong action verb(s) in bullet points.",
                action="Consider starting bullet points with strong action verbs like 'developed', 'engineered', 'optimized', or 'deployed' to highlight personal contributions.",
            )
        )

    # 3. Quantifiable Metrics Recommendations
    if details.quantifiable_metrics_score < 70.0:
        recommendations.append(
            AtsRecommendation(
                category="metrics",
                priority="medium",
                title="Add Measurable Achievements",
                issue=f"Detected {details.metrics_count} quantifiable metric(s) in your resume.",
                action="Where truthful, incorporate measurable outcomes (e.g. latency improvement, user count, automated tasks, percentage gains) to demonstrate tangible impact.",
            )
        )

    # 4. Length Heuristics (Explicitly labeled as HireLens heuristic)
    word_count = len(resume_text.split())
    if word_count < 150:
        recommendations.append(
            AtsRecommendation(
                category="length",
                priority="medium",
                title="Resume Appears Very Short",
                issue=f"Your resume appears very short based on HireLens's length heuristic ({word_count} words detected).",
                action="Consider expanding on your technical responsibilities, project details, and specific achievements to provide sufficient context for reviewers.",
            )
        )
    elif word_count > 1200:
        recommendations.append(
            AtsRecommendation(
                category="length",
                priority="low",
                title="Resume Appears Lengthy",
                issue=f"Your resume appears lengthy based on HireLens's length heuristic ({word_count} words detected).",
                action="For early-career roles, consider condensing older bullet points to keep your resume focused and scannable.",
            )
        )

    return recommendations
