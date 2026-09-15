import pytest
from app.services.recommender import (
    ROLE_TAXONOMY,
    compute_role_score,
    evaluate_role_recommendations,
    generate_prioritized_skill_gaps,
    generate_unified_recommendations,
)
from app.services.ats_analyzer import (
    analyze_ats_quality,
    generate_ats_recommendations,
)
from app.services.analysis_engine import run_resume_job_analysis
from app.schemas.analysis import (
    ExperienceAlignment,
    EducationAlignment,
)


# =====================================================================
# 1. ROLE RECOMMENDATION ENGINE TESTS
# =====================================================================

def test_role_recommendation_python_skills():
    """
    Candidate with Python + FastAPI + PostgreSQL should naturally favor
    Python Developer and Backend Developer over Java Developer or Frontend Developer.
    """
    resume_skills = ["Python", "FastAPI", "PostgreSQL", "Git"]
    roles = evaluate_role_recommendations(resume_skills)
    role_map = {r.role: r for r in roles}

    # Python Developer and Backend Developer must score significantly higher than Java/Frontend
    assert role_map["Python Developer"].score > role_map["Java Developer"].score
    assert role_map["Python Developer"].score > role_map["Frontend Developer"].score
    assert role_map["Backend Developer"].score > role_map["Frontend Developer"].score
    assert role_map["Python Developer"].score > 0.0
    assert "Python" in role_map["Python Developer"].matched_skills
    assert "FastAPI" in role_map["Python Developer"].matched_skills


def test_role_recommendation_java_skills():
    """
    Candidate with Java + Spring Boot + MySQL + REST API should naturally favor
    Java Developer and Backend Developer over Python Developer or Frontend Developer.
    """
    resume_skills = ["Java", "Spring Boot", "MySQL", "REST API", "Git"]
    roles = evaluate_role_recommendations(resume_skills)
    role_map = {r.role: r for r in roles}

    assert role_map["Java Developer"].score > role_map["Python Developer"].score
    assert role_map["Java Developer"].score > role_map["Frontend Developer"].score
    assert role_map["Backend Developer"].score > role_map["Frontend Developer"].score
    assert "Java" in role_map["Java Developer"].matched_skills
    assert "Spring Boot" in role_map["Java Developer"].matched_skills


def test_role_recommendation_frontend_skills():
    """
    Candidate with React + TypeScript + JavaScript + HTML + CSS + Tailwind CSS + Git
    must rank Frontend Developer at the very top.
    """
    resume_skills = ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Tailwind CSS", "Git"]
    roles = evaluate_role_recommendations(resume_skills)
    top_role = roles[0]

    assert top_role.role == "Frontend Developer"
    assert top_role.score >= 50.0
    assert top_role.fit_level in ["Strong fit", "Good fit"]
    assert "React" in top_role.matched_skills
    assert "TypeScript" in top_role.matched_skills


def test_role_recommendation_full_stack():
    """
    Candidate with both frontend and backend skills should score well on Full Stack Developer.
    """
    resume_skills = ["React", "JavaScript", "HTML", "CSS", "Node.js", "Python", "SQL", "REST API", "Git"]
    roles = evaluate_role_recommendations(resume_skills)
    role_map = {r.role: r for r in roles}

    assert role_map["Full Stack Developer"].score >= 60.0
    assert role_map["Full Stack Developer"].fit_level in ["Strong fit", "Good fit"]
    assert len(role_map["Full Stack Developer"].matched_skills) >= 6


def test_role_recommendation_data_analyst():
    """
    Candidate with data skills should rank Data Analyst highly.
    """
    resume_skills = ["Python", "SQL", "Pandas", "NumPy", "Matplotlib"]
    roles = evaluate_role_recommendations(resume_skills)
    role_map = {r.role: r for r in roles}

    assert role_map["Data Analyst"].score > role_map["Frontend Developer"].score
    assert role_map["Data Analyst"].score >= 50.0


def test_role_recommendation_machine_learning():
    """
    Candidate with ML frameworks should rank Machine Learning Engineer highly.
    """
    resume_skills = ["Python", "scikit-learn", "TensorFlow", "PyTorch", "Machine Learning", "NumPy"]
    roles = evaluate_role_recommendations(resume_skills)
    role_map = {r.role: r for r in roles}

    assert role_map["Machine Learning Engineer"].score > role_map["Frontend Developer"].score
    assert role_map["Machine Learning Engineer"].score >= 50.0


def test_role_recommendation_deterministic_and_no_hallucinations():
    """
    Verify role scoring is 100% deterministic and does not invent any skills.
    """
    resume_skills = ["Python", "FastAPI", "SQL", "Docker"]
    run1 = evaluate_role_recommendations(resume_skills)
    run2 = evaluate_role_recommendations(resume_skills)

    assert len(run1) == len(run2) == 8
    for r1, r2 in zip(run1, run2):
        assert r1.role == r2.role
        assert r1.score == r2.score
        assert r1.fit_level == r2.fit_level
        assert r1.matched_skills == r2.matched_skills
        assert r1.missing_core_skills == r2.missing_core_skills
        # Ensure matched skills are strictly a subset of normalized input skills
        for s in r1.matched_skills:
            assert s in {"Python", "FastAPI", "SQL", "Docker"}


def test_role_recommendation_empty_skills():
    """
    Empty resume skill set must safely return 0.0 scores without crashing.
    """
    roles = evaluate_role_recommendations([])
    assert len(roles) == 8
    for r in roles:
        assert r.score == 0.0
        assert r.fit_level == "Skills to strengthen"
        assert r.matched_skills == []


def test_compute_role_score_exact_math():
    """
    Verify exact role score formula: 0.70 * core_cov + 0.30 * supp_cov.
    """
    # Python Developer core: [Python, FastAPI, Django, Flask, SQL, PostgreSQL] (6)
    # supporting: [Docker, Git, Linux, Redis, NumPy, Pandas] (6)
    # Matched core: Python, FastAPI (2/6 = 0.33333)
    # Matched supp: Docker (1/6 = 0.16667)
    # Raw = 0.70 * (2/6) + 0.30 * (1/6) = 0.23333 + 0.05 = 0.28333 -> 28.3
    score, fit_level, matched, missing_core, reason = compute_role_score(
        resume_skills=["Python", "FastAPI", "Docker"],
        role_name="Python Developer"
    )
    assert score == 28.3
    assert fit_level == "Moderate fit"
    assert "Python" in matched
    assert "FastAPI" in matched
    assert "Docker" in matched
    assert "Django" in missing_core


# =====================================================================
# 2. PRIORITIZED SKILL GAP ENGINE TESTS
# =====================================================================

def test_prioritized_skill_gaps_required_vs_preferred():
    """
    Missing required skills in core categories must receive HIGH priority.
    Missing preferred skills receive MEDIUM or LOW priority.
    """
    missing_req = ["FastAPI", "PostgreSQL"]
    missing_pref = ["Redis", "Jira"]
    jd_text = "Looking for a backend developer skilled in FastAPI, PostgreSQL, Redis, and Jira."

    gaps = generate_prioritized_skill_gaps(
        missing_required_skills=missing_req,
        missing_preferred_skills=missing_pref,
        job_description_text=jd_text,
    )

    gap_map = {g.skill: g for g in gaps}
    assert "FastAPI" in gap_map
    assert "PostgreSQL" in gap_map
    assert "Redis" in gap_map
    assert "Jira" in gap_map

    # Required core skills -> high priority
    assert gap_map["FastAPI"].priority == "high"
    assert gap_map["FastAPI"].required_or_preferred == "required"
    assert gap_map["PostgreSQL"].priority == "high"
    assert gap_map["PostgreSQL"].required_or_preferred == "required"

    # Preferred core skill -> medium priority
    assert gap_map["Redis"].priority in ["medium", "low"]
    assert gap_map["Redis"].required_or_preferred == "preferred"

    # Preferred secondary tool -> low priority
    assert gap_map["Jira"].priority == "low"
    assert gap_map["Jira"].required_or_preferred == "preferred"


def test_prioritized_skill_gaps_alias_normalization_and_deduplication():
    """
    Skill aliases (e.g. 'postgres' and 'PostgreSQL') must be normalized to
    canonical names and not duplicated.
    """
    missing_req = ["postgres", "PostgreSQL", "py"]
    missing_pref = ["Python"]

    gaps = generate_prioritized_skill_gaps(
        missing_required_skills=missing_req,
        missing_preferred_skills=missing_pref,
        job_description_text="Experience with Python and PostgreSQL required.",
    )

    skills = [g.skill for g in gaps]
    # "postgres" and "PostgreSQL" must deduplicate to single "PostgreSQL"
    assert skills.count("PostgreSQL") == 1
    # "py" and "Python" must deduplicate to single "Python"
    assert skills.count("Python") == 1
    assert len(skills) == 2


def test_prioritized_skill_gaps_only_jd_skills():
    """
    Only skills passed from the JD missing lists are recommended.
    """
    gaps = generate_prioritized_skill_gaps(
        missing_required_skills=["Docker"],
        missing_preferred_skills=[],
        job_description_text="Must know Docker.",
    )
    assert len(gaps) == 1
    assert gaps[0].skill == "Docker"
    assert "Kubernetes" not in [g.skill for g in gaps]


# =====================================================================
# 3. ATS RECOMMENDATION TESTS (Conservative Heuristics)
# =====================================================================

def test_ats_recommendations_missing_sections():
    """
    Missing sections produce clear, actionable section recommendations.
    """
    # Short resume missing contact, experience, education, projects
    resume = "SKILLS\nPython, Docker\nSUMMARY\nSoftware engineer."
    ats_breakdown = analyze_ats_quality(resume)
    recs = generate_ats_recommendations(ats_breakdown, resume)

    categories = [r.category for r in recs]
    assert "sections" in categories
    section_titles = [r.title for r in recs if r.category == "sections"]
    assert any("Contact" in t for t in section_titles)
    assert any("Experience" in t for t in section_titles)
    assert any("Education" in t for t in section_titles)


def test_ats_recommendations_length_heuristics():
    """
    Verify conservative wording for length heuristics.
    """
    short_resume = "Just a short resume of 10 words with no sections."
    ats_short = analyze_ats_quality(short_resume)
    recs = generate_ats_recommendations(ats_short, short_resume)

    length_recs = [r for r in recs if r.category == "length"]
    assert len(length_recs) == 1
    assert "HireLens's length heuristic" in length_recs[0].issue
    assert "reject" not in length_recs[0].issue.lower()
    assert "reject" not in length_recs[0].action.lower()


def test_ats_recommendations_good_resume_no_false_critical_warnings():
    """
    A well-formatted resume with complete sections, action verbs, and metrics
    should not receive critical ATS warnings.
    """
    good_resume = (
        "Jane Doe\n"
        "Email: jane@example.com | Phone: +1-555-0123\n"
        "SUMMARY\n"
        "Experienced full-stack software engineer with 5 years building scalable web services.\n"
        "SKILLS\n"
        "Python, React, FastAPI, PostgreSQL, Docker, Git\n"
        "WORK EXPERIENCE\n"
        "- Developed REST APIs reducing server response latency by 40% across all endpoints.\n"
        "- Engineered microservices architecture handling 10000+ daily active users seamlessly.\n"
        "- Optimized PostgreSQL database queries saving 25 hours of monthly background compute.\n"
        "- Deployed CI/CD container pipelines with Docker improving test cycle time by 50%.\n"
        "EDUCATION\n"
        "Bachelor of Science in Computer Science, State University, 2021\n"
        "PROJECTS\n"
        "- Built full-stack analytics platform utilizing React, FastAPI, and PostgreSQL.\n"
    )
    # Ensure words are >= 150
    good_resume_padded = good_resume + "\n" + " ".join(["responsibilities and leadership"] * 20)
    ats_breakdown = analyze_ats_quality(good_resume_padded)
    recs = generate_ats_recommendations(ats_breakdown, good_resume_padded)

    # A good resume should have 0 high-priority ATS warnings
    high_prio_recs = [r for r in recs if r.priority == "high"]
    assert len(high_prio_recs) == 0


# =====================================================================
# 4. UNIFIED RECOMMENDATION TESTS
# =====================================================================

def test_unified_recommendations_structure_and_sorting():
    """
    Unified recommendations must contain valid types, priorities, and
    be sorted with high priority first.
    """
    skill_gaps = generate_prioritized_skill_gaps(
        missing_required_skills=["FastAPI"],
        missing_preferred_skills=["Redis"],
        job_description_text="Requires FastAPI, prefers Redis.",
    )
    ats_breakdown = analyze_ats_quality("Short text without sections")
    ats_recs = generate_ats_recommendations(ats_breakdown, "Short text without sections")

    exp_alignment = ExperienceAlignment(
        required_years=3.0,
        candidate_years=1.0,
        score=40.0,
        status="below_requirement",
        explanation="Candidate has 1.0 year experience, less than 3.0 required.",
    )

    unified = generate_unified_recommendations(
        skill_gaps=skill_gaps,
        ats_recommendations=ats_recs,
        experience_alignment=exp_alignment,
    )

    assert len(unified) > 0

    # Validate types and priorities
    valid_types = {"skill_gap", "ats", "structure", "content"}
    valid_prios = {"high", "medium", "low"}
    for u in unified:
        assert u.type in valid_types
        assert u.priority in valid_prios
        assert len(u.title) > 0
        assert len(u.action) > 0

    # Validate sorting: High priority items must precede Medium and Low
    prio_order = {"high": 0, "medium": 1, "low": 2}
    ranks = [prio_order[u.priority] for u in unified]
    assert ranks == sorted(ranks)


# =====================================================================
# 5. END-TO-END ANALYSIS PIPELINE REGRESSION & RESPONSE VERIFICATION
# =====================================================================

def test_analysis_engine_end_to_end_phase5():
    """
    Verify complete analysis engine returns all Phase 5 fields cleanly
    while preserving existing scores and formula weights.
    """
    resume_text = (
        "John Developer\n"
        "Email: john@example.com | Phone: 555-123-4567\n"
        "SKILLS\n"
        "Python, FastAPI, SQL, PostgreSQL, Docker, Git\n"
        "EXPERIENCE\n"
        "Developed high-throughput APIs serving 5000 users daily, reducing latency by 35%.\n"
        "EDUCATION\n"
        "B.S. in Computer Science\n"
        "PROJECTS\n"
        "Engineered open-source backend framework in Python.\n"
    )
    jd_text = (
        "We are looking for a Backend Engineer with 3+ years experience in Python, FastAPI, "
        "PostgreSQL, Redis, and Kubernetes."
    )

    response = run_resume_job_analysis(
        resume_text=resume_text,
        job_description_text=jd_text,
    )

    # 1. Verify existing fields preserved
    assert response.overall_score > 0.0
    assert response.score_breakdown.skill_score > 0.0
    assert response.score_breakdown.text_similarity_score > 0.0
    assert response.score_breakdown.experience_score > 0.0
    assert response.score_breakdown.ats_quality_score > 0.0
    assert response.weights.skill == 0.40
    assert response.weights.text_similarity == 0.30
    assert response.weights.experience == 0.15
    assert response.weights.ats == 0.15

    # 2. Verify Phase 5 fields populated
    assert len(response.role_recommendations) == 8
    # Top role should be Python Developer or Backend Developer
    top_role_names = [r.role for r in response.role_recommendations[:2]]
    assert "Python Developer" in top_role_names or "Backend Developer" in top_role_names

    # Missing skills: Redis, Kubernetes
    assert len(response.prioritized_skill_gaps) >= 1
    gap_skills = [g.skill for g in response.prioritized_skill_gaps]
    assert "Redis" in gap_skills or "Kubernetes" in gap_skills

    # ATS recommendations generated
    assert isinstance(response.ats_recommendations, list)

    # Unified recommendations generated
    assert len(response.unified_recommendations) > 0
    assert any(u.type == "skill_gap" for u in response.unified_recommendations)
