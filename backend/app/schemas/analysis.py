from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisPreviewRequest(BaseModel):
    resume_text: str = Field(..., description="Cleaned resume text to analyze")
    job_description_text: str = Field(..., description="Target job description text")


class RunAnalysisRequest(BaseModel):
    resume_id: str = Field(..., description="ID of previously uploaded resume owned by user")
    job_title: Optional[str] = Field(None, description="Optional target job title")
    job_description_text: str = Field(..., description="Target job description text")


class ScoreBreakdown(BaseModel):
    skill_score: float = Field(..., description="Skill match sub-score (0-100)")
    text_similarity_score: float = Field(..., description="Cosine Text Similarity sub-score (0-100)")
    experience_score: float = Field(..., description="Experience alignment sub-score (0-100)")
    ats_quality_score: float = Field(..., description="ATS quality sub-score (0-100)")


class ScoreWeights(BaseModel):
    skill: float = Field(default=0.40, description="Skill match weight (40%)")
    text_similarity: float = Field(default=0.30, description="Text similarity weight (30%)")
    experience: float = Field(default=0.15, description="Experience weight (15%)")
    ats: float = Field(default=0.15, description="ATS quality weight (15%)")


class SkillAliasMatch(BaseModel):
    resume_alias: str = Field(..., description="Raw alias found in resume text")
    canonical_name: str = Field(..., description="Normalized canonical skill name")


class SkillMatchDetails(BaseModel):
    required_match_percentage: float = Field(..., description="Percentage of required JD skills matched")
    preferred_match_percentage: float = Field(..., description="Percentage of preferred JD skills matched")
    exact_matches: List[str] = Field(default_factory=list, description="Canonical skills matched directly")
    alias_matches: List[SkillAliasMatch] = Field(default_factory=list, description="Skills matched via aliases")


class TextSimilarityDetails(BaseModel):
    similarity_score: float = Field(..., description="Cosine similarity scaled to 0-100")
    method: str = Field(
        default="Normalized Term-Frequency Cosine Similarity",
        description="Mathematical technique used for textual similarity",
    )
    note: str = Field(
        default="Measures term frequency overlap and lexical alignment between resume and job description text.",
        description="Technical description of similarity computation",
    )


class ExperienceAlignment(BaseModel):
    required_years: Optional[float] = Field(None, description="Extracted required years of experience")
    candidate_years: Optional[float] = Field(None, description="Estimated candidate years of experience")
    score: float = Field(..., description="Experience alignment score (0-100)")
    status: str = Field(..., description="Alignment classification ('aligned', 'exceeds_requirement', 'below_requirement', 'unknown')")
    explanation: str = Field(..., description="Human readable explanation of experience evaluation")


class EducationAlignment(BaseModel):
    required_degree: Optional[str] = Field(None, description="Extracted degree requirement from JD")
    candidate_degree: Optional[str] = Field(None, description="Extracted candidate degree from resume")
    score: float = Field(..., description="Education alignment score (0-100)")
    status: str = Field(..., description="Alignment classification ('aligned', 'below_requirement', 'unknown')")
    explanation: str = Field(..., description="Human readable explanation of education evaluation")


class AtsDetailBreakdown(BaseModel):
    section_completeness_score: float = Field(..., description="Section completeness score (50% weight)")
    action_verb_score: float = Field(..., description="Action verb usage score (25% weight)")
    quantifiable_metrics_score: float = Field(..., description="Quantifiable metrics score (25% weight)")
    sections_found: List[str] = Field(default_factory=list, description="Standard sections detected in resume")
    sections_missing: List[str] = Field(default_factory=list, description="Standard sections missing in resume")
    action_verbs_found: List[str] = Field(default_factory=list, description="Unique action verbs detected")
    metrics_count: int = Field(..., description="Count of quantifiable metrics/numbers detected")


class AtsQualityBreakdown(BaseModel):
    score: float = Field(..., description="Overall ATS health score (0-100)")
    details: AtsDetailBreakdown = Field(..., description="Sub-breakdown of ATS factors")


class SkillGapRecommendation(BaseModel):
    skill: str = Field(..., description="Canonical skill name")
    category: str = Field(..., description="Skill category, e.g. backend, database, frontend")
    priority: str = Field(..., description="Priority classification: 'high', 'medium', or 'low'")
    required_or_preferred: str = Field(..., description="Whether skill was required or preferred in JD")
    reason: str = Field(..., description="Deterministic explanation of why this skill matters")
    action: str = Field(..., description="Concrete, actionable suggestion for the candidate")


class RoleRecommendation(BaseModel):
    role: str = Field(..., description="Target role title")
    score: float = Field(..., description="Deterministic role-fit score (0-100)")
    fit_level: str = Field(..., description="Fit category: Strong fit, Good fit, Moderate fit, Skills to strengthen")
    matched_skills: List[str] = Field(default_factory=list, description="Candidate skills aligned with this role")
    missing_core_skills: List[str] = Field(default_factory=list, description="Core role skills missing from resume")
    reason: str = Field(..., description="Explainable description of role alignment")


class AtsRecommendation(BaseModel):
    category: str = Field(..., description="ATS focus area: sections, action_verbs, metrics, length")
    priority: str = Field(..., description="Priority classification: 'high', 'medium', or 'low'")
    title: str = Field(..., description="Summary title of recommendation")
    issue: str = Field(..., description="Observation based on ATS heuristics")
    action: str = Field(..., description="Actionable step to improve resume formatting/content")


class UnifiedRecommendation(BaseModel):
    type: str = Field(..., description="Recommendation type: skill_gap, ats, content, structure")
    priority: str = Field(..., description="Priority classification: 'high', 'medium', or 'low'")
    title: str = Field(..., description="Summary title")
    reason: str = Field(..., description="Explainable factual rationale")
    action: str = Field(..., description="Recommended action step")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence data when available")


class AnalysisPreviewResponse(BaseModel):
    id: Optional[str] = Field(None, description="Saved analysis record ID (if persisted)")
    analysis_id: Optional[str] = Field(None, description="Saved analysis record ID (alias for compatibility)")
    resume_id: Optional[str] = Field(None, description="Associated resume ID (if persisted)")
    job_description_id: Optional[str] = Field(None, description="Associated job description ID (if persisted)")
    job_title: Optional[str] = Field(None, description="Job title if provided")
    created_at: Optional[datetime] = Field(None, description="Analysis creation timestamp (if persisted)")
    overall_score: float = Field(..., description="Final composite match score (0-100)")
    score_breakdown: ScoreBreakdown = Field(..., description="Sub-score breakdown")
    weights: ScoreWeights = Field(default_factory=ScoreWeights, description="Weight configuration used")
    resume_skills: List[str] = Field(..., description="All skills extracted from resume")
    required_jd_skills: List[str] = Field(..., description="Required skills extracted from job description")
    preferred_jd_skills: List[str] = Field(..., description="Preferred skills extracted from job description")
    matching_skills: List[str] = Field(..., description="Skills matching between resume and job description")
    missing_required_skills: List[str] = Field(..., description="Required job skills missing from candidate resume")
    missing_preferred_skills: List[str] = Field(..., description="Preferred job skills missing from candidate resume")
    skill_match_details: SkillMatchDetails = Field(..., description="Detailed skill match metadata")
    text_similarity_details: TextSimilarityDetails = Field(..., description="Text similarity metrics")
    experience_alignment: ExperienceAlignment = Field(..., description="Experience alignment assessment")
    education_alignment: EducationAlignment = Field(..., description="Education alignment assessment")
    ats_breakdown: AtsQualityBreakdown = Field(..., description="ATS structural health assessment")
    recommendations: List[str] = Field(default_factory=list, description="Actionable improvement suggestions")
    warnings: List[str] = Field(default_factory=list, description="Engine execution warnings or caveats")
    # Phase 5 Additions:
    prioritized_skill_gaps: List[SkillGapRecommendation] = Field(default_factory=list, description="Prioritized structured skill gaps")
    role_recommendations: List[RoleRecommendation] = Field(default_factory=list, description="Ranked deterministic role recommendations")
    ats_recommendations: List[AtsRecommendation] = Field(default_factory=list, description="Actionable ATS recommendations")
    unified_recommendations: List[UnifiedRecommendation] = Field(default_factory=list, description="Unified improvement recommendations")


class AnalysisHistorySummary(BaseModel):
    id: str = Field(..., description="Analysis ID")
    overall_score: float = Field(..., description="Final composite score")
    resume_id: str = Field(..., description="Resume ID")
    resume_filename: Optional[str] = Field(None, description="Original resume filename")
    job_description_id: str = Field(..., description="Job Description ID")
    job_title: Optional[str] = Field(None, description="Job title if provided")
    created_at: datetime = Field(..., description="Timestamp created")
