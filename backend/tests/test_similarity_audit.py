import pytest
from app.services.text_similarity import compute_text_similarity, preprocess_for_similarity, TECH_STOP_WORDS
from app.services.analysis_engine import run_resume_job_analysis
from sklearn.feature_extraction.text import TfidfVectorizer


# Controlled Test Data
STRONG_BACKEND_RESUME = """Rahul Mehta
rahul.mehta@example.com | Ahmedabad, India | github.com/rahulmehta
SUMMARY
Backend Software Engineer with 1 year of experience building REST APIs and web services. Strong in Python,
FastAPI, Node.js, PostgreSQL and Docker.
SKILLS
Python, FastAPI, Node.js, JavaScript, PostgreSQL, SQL, REST API, Docker, Git, GitHub, React
EXPERIENCE
Backend Developer Intern | Jun 2025 - Jun 2026
- Built 12 REST API endpoints using Python and FastAPI, reducing response time by 30%.
- Designed PostgreSQL schemas and SQL queries for 50,000+ records.
- Containerized services with Docker and maintained GitHub CI workflows.
- Integrated Node.js and JavaScript services with backend APIs.
EDUCATION
Bachelor of Engineering in Computer Engineering | GTU | 2022 - 2026
PROJECTS
Job Match API - FastAPI + PostgreSQL application with Docker, Git, GitHub and REST API integration.
Recruitment Dashboard - React and JavaScript frontend connected to Node.js and Python services."""

CONTROLLED_BACKEND_JD = """Backend Software Engineer - Entry Level

Required qualifications:
- Bachelor's degree in Computer Science, Computer Engineering, or a related field.
- 0-2 years of relevant software development experience.
- Python and FastAPI.
- Node.js and JavaScript.
- PostgreSQL and SQL.
- REST API development.
- Docker.
- Git and GitHub.
- React familiarity.

Responsibilities:
- Build and maintain REST APIs using Python and FastAPI.
- Develop backend services using Node.js and JavaScript.
- Design PostgreSQL databases and write SQL queries.
- Containerize applications with Docker.
- Collaborate through Git and GitHub.
- Work with React-based frontend applications when needed.
- Write maintainable, testable software and improve application performance.

Preferred:
- Experience deploying containerized applications.
- Familiarity with CI workflows."""

PARTIAL_BACKEND_RESUME = """Vikram Sharma
vikram@example.com | Mumbai, India
SUMMARY
Software developer with experience in Python scripting and SQL queries.
SKILLS
Python, SQL, Git
EXPERIENCE
Junior Programmer | 2025 - 2026
- Wrote Python scripts to automate data workflows.
- Maintained SQL queries for internal reporting.
- Used Git for version control.
EDUCATION
Bachelor of Science in Information Technology | 2022 - 2026
PROJECTS
Python Data Parser - Script to extract and transform CSV data into SQL tables using Git."""

POOR_MATCH_RESUME = """Amit Patel
amit.patel@example.com | Ahmedabad, India
SUMMARY
Graphic design student focused on visual communication, branding and digital illustration.
SKILLS
Adobe Photoshop, Adobe Illustrator, Figma, Canva, UI Design, Branding, Typography
EXPERIENCE
Graphic Design Intern | Jun 2025 - Jun 2026
- Designed 40+ social media creatives and brand assets.
- Created visual layouts and illustrations for 15 client projects.
- Improved campaign engagement by 20% through revised visual designs.
EDUCATION
Bachelor of Design in Visual Communication | 2022 - 2026
PROJECTS
Brand Identity Project - Created logos, typography systems and marketing assets.
Mobile App Mockups - Designed high-fidelity UI mockups in Figma."""


def test_strong_match_materially_higher_similarity_than_poor_match():
    """
    Regression Test 1:
    Strong resume vs matching backend JD must produce a materially higher
    text similarity than the poor-match resume by a substantial margin (> 40%).
    """
    strong_result = run_resume_job_analysis(
        resume_text=STRONG_BACKEND_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )
    poor_result = run_resume_job_analysis(
        resume_text=POOR_MATCH_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )

    strong_sim = strong_result.score_breakdown.text_similarity_score
    poor_sim = poor_result.score_breakdown.text_similarity_score

    # Strong match text similarity should be at least 50%
    assert strong_sim >= 50.0, f"Expected strong similarity >= 50.0%, got {strong_sim}%"
    # Poor match text similarity should remain very low (< 10%)
    assert poor_sim <= 10.0, f"Expected poor similarity <= 10.0%, got {poor_sim}%"
    # Material separation margin > 40 percentage points
    assert (strong_sim - poor_sim) > 40.0, f"Separation {strong_sim - poor_sim} is below 40.0"


def test_technical_terms_survive_preprocessing():
    """
    Regression Test 2:
    Technical terms (Python, FastAPI, Node.js, JavaScript, PostgreSQL, REST API,
    Docker, GitHub, C++, C#, .NET, CI/CD, Go) must survive preprocessing and
    vectorization without being purged or corrupted.
    """
    tech_terms = [
        "Python", "FastAPI", "Node.js", "JavaScript", "PostgreSQL",
        "SQL", "REST API", "Docker", "Git", "GitHub", "React",
        "C++", "C#", ".NET", "CI/CD", "Go"
    ]

    vectorizer = TfidfVectorizer(
        stop_words=list(TECH_STOP_WORDS),
        ngram_range=(1, 1),
        use_idf=False,
        token_pattern=r"(?u)\b[a-zA-Z0-9_]+\b",
    )

    for term in tech_terms:
        preprocessed = preprocess_for_similarity(term)
        assert preprocessed.strip(), f"Term {term} preprocessed to empty string"
        
        matrix = vectorizer.fit_transform([preprocessed])
        features = list(vectorizer.get_feature_names_out())
        assert len(features) > 0, f"Term '{term}' lost all tokens during vectorization"


def test_overall_score_strictly_equals_weighted_formula():
    """
    Regression Test 3:
    The final overall score must exactly equal the 40/30/15/15 weighted formula:
    overall = round(0.40 * skill + 0.30 * text_similarity + 0.15 * experience + 0.15 * ats, 1)
    """
    test_cases = [STRONG_BACKEND_RESUME, PARTIAL_BACKEND_RESUME, POOR_MATCH_RESUME]

    for resume in test_cases:
        res = run_resume_job_analysis(
            resume_text=resume,
            job_description_text=CONTROLLED_BACKEND_JD,
        )
        b = res.score_breakdown
        expected_score = round(
            0.40 * b.skill_score
            + 0.30 * b.text_similarity_score
            + 0.15 * b.experience_score
            + 0.15 * b.ats_quality_score,
            1,
        )
        assert res.overall_score == expected_score, (
            f"Overall score {res.overall_score} != expected {expected_score} for breakdown {b}"
        )


def test_skill_gap_recommendations_still_work():
    """
    Regression Test 4:
    Missing required skills must continue to generate skill-gap recommendations.
    """
    partial_res = run_resume_job_analysis(
        resume_text=PARTIAL_BACKEND_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )
    assert len(partial_res.missing_required_skills) > 0
    # Must have recommendation mentioning missing core required skills
    has_skill_rec = any(
        "Add missing core required skills:" in rec for rec in partial_res.recommendations
    )
    assert has_skill_rec, f"Missing required skills recommendation not found: {partial_res.recommendations}"

    # Poor match should also recommend adding core skills
    poor_res = run_resume_job_analysis(
        resume_text=POOR_MATCH_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )
    assert len(poor_res.missing_required_skills) == 11
    has_poor_skill_rec = any(
        "Add missing core required skills:" in rec for rec in poor_res.recommendations
    )
    assert has_poor_skill_rec, "Missing skills recommendation missing for poor match"


def test_poor_match_substantially_lower_skill_coverage():
    """
    Regression Test 5:
    Poor-match resume must continue to have substantially lower skill coverage
    than strong-match resume (0% vs 100%).
    """
    strong_res = run_resume_job_analysis(
        resume_text=STRONG_BACKEND_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )
    poor_res = run_resume_job_analysis(
        resume_text=POOR_MATCH_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )

    assert strong_res.score_breakdown.skill_score == 100.0
    assert len(strong_res.matching_skills) == 11
    assert len(strong_res.missing_required_skills) == 0

    assert poor_res.score_breakdown.skill_score == 0.0
    assert len(poor_res.matching_skills) == 0
    assert len(poor_res.missing_required_skills) == 11


def test_score_hierarchy_strong_partial_poor():
    """
    Regression Test 6:
    Verify the strict hierarchy across profiles without hardcoding artificial values:
    Strong-match:
      - high skill coverage (100%)
      - high text similarity (>= 50%)
      - high overall score (>= 80%)
    Partial-match:
      - clearly lower than strong across skill, text similarity, and overall
    Poor-match:
      - very low skill coverage (0%)
      - very low text similarity (<= 10%)
      - clearly lower overall score than partial
    """
    strong_res = run_resume_job_analysis(
        resume_text=STRONG_BACKEND_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )
    partial_res = run_resume_job_analysis(
        resume_text=PARTIAL_BACKEND_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )
    poor_res = run_resume_job_analysis(
        resume_text=POOR_MATCH_RESUME,
        job_description_text=CONTROLLED_BACKEND_JD,
    )

    # 1. Skill Coverage Gradient
    assert strong_res.score_breakdown.skill_score == 100.0
    assert strong_res.score_breakdown.skill_score > partial_res.score_breakdown.skill_score
    assert partial_res.score_breakdown.skill_score > poor_res.score_breakdown.skill_score
    assert poor_res.score_breakdown.skill_score == 0.0

    # 2. Text Similarity (Cosine Text Similarity) Gradient
    assert strong_res.score_breakdown.text_similarity_score >= 50.0
    assert strong_res.score_breakdown.text_similarity_score > partial_res.score_breakdown.text_similarity_score
    assert partial_res.score_breakdown.text_similarity_score > poor_res.score_breakdown.text_similarity_score
    assert poor_res.score_breakdown.text_similarity_score <= 10.0

    # 3. Overall Composite Score Gradient
    assert strong_res.overall_score >= 80.0
    assert strong_res.overall_score > partial_res.overall_score
    assert partial_res.overall_score > poor_res.overall_score

