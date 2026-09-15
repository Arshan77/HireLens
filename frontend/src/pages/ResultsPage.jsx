import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import ScoreGauge from '../components/common/ScoreGauge';
import SkillBadge from '../components/common/SkillBadge';
import ScoreBreakdownChart from '../components/charts/ScoreBreakdownChart';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import { getAnalysisById, downloadAnalysisPdf } from '../api/analysis';
import {
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  FileText,
  Award,
  Layers,
  Search,
  Target,
  ArrowLeft,
  Info,
  Briefcase,
  GraduationCap,
  Download,
} from 'lucide-react';

export default function ResultsPage() {
  const { analysisId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true);
      setPdfError(null);
      const blob = await downloadAnalysisPdf(analysisId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `HireLens_Analysis_${analysisId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setPdfError(err.message || 'Failed to download PDF report.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  useEffect(() => {
    async function fetchAnalysis() {
      try {
        setLoading(true);
        setError(null);
        const res = await getAnalysisById(analysisId);
        setData(res);
      } catch (err) {
        setError(err.message || 'Failed to load analysis results.');
      } finally {
        setLoading(false);
      }
    }
    if (analysisId) {
      fetchAnalysis();
    }
  }, [analysisId]);

  if (loading) {
    return (
      <AppShell>
        <LoadingSpinner label="Retrieving analysis report..." size="lg" />
      </AppShell>
    );
  }

  if (error || !data) {
    return (
      <AppShell>
        <div className="space-y-6">
          <Link to="/app/history" className="inline-flex items-center text-sm text-slate-600 hover:text-slate-900">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to History
          </Link>
          <ErrorAlert message={error || 'Analysis results could not be loaded.'} />
        </div>
      </AppShell>
    );
  }

  const {
    overall_score,
    score_breakdown,
    weights,
    matching_skills = [],
    missing_required_skills = [],
    missing_preferred_skills = [],
    text_similarity_details,
    experience_alignment,
    education_alignment,
    ats_breakdown,
    recommendations = [],
    prioritized_skill_gaps = [],
    role_recommendations = [],
    ats_recommendations = [],
    unified_recommendations = [],
  } = data;

  const atsDetails = ats_breakdown?.details || {};

  const getStatusBadge = (status) => {
    switch (status) {
      case 'aligned':
      case 'exceeds_requirement':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 mr-1" /> Aligned
          </span>
        );
      case 'below_requirement':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-800 border border-amber-200">
            <AlertTriangle className="w-3 h-3 mr-1" /> Gaps Detected
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
            <HelpCircle className="w-3 h-3 mr-1" /> Not enough information detected
          </span>
        );
    }
  };

  const getFitBadge = (fitLevel) => {
    switch (fitLevel) {
      case 'Strong fit':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            Strong fit
          </span>
        );
      case 'Good fit':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-800 border border-blue-200">
            Good fit
          </span>
        );
      case 'Moderate fit':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            Moderate fit
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            Skills to strengthen
          </span>
        );
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-800 border border-rose-200">
            High Priority
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
            Medium Priority
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            Low Priority
          </span>
        );
    }
  };

  return (
    <AppShell>
      <div className="space-y-8 max-w-5xl mx-auto">
        {/* Navigation back */}
        <div className="flex items-center justify-between">
          <Link to="/app/history" className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-slate-900">
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to History
          </Link>
          <span className="text-xs text-slate-400 font-mono">ID: {analysisId}</span>
        </div>

        {/* Header Hero Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 text-center md:text-left">
            <div className="inline-flex items-center px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-medium">
              <Briefcase className="w-3.5 h-3.5 mr-1 text-slate-500" />
              Evaluation Report
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              {data.job_title || 'Target Job Match Analysis'}
            </h1>
            <p className="text-sm text-slate-500">
              Evaluated against parsed resume &bull; Deterministic engine score
            </p>
            <div className="pt-2 flex flex-col sm:flex-row items-center sm:items-start gap-2">
              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={downloadingPdf}
                className="inline-flex items-center px-4 py-2 rounded-lg text-xs font-semibold bg-teal-700 hover:bg-teal-800 text-white shadow-xs transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" />
                {downloadingPdf ? 'Generating PDF...' : 'Download PDF Report'}
              </button>
              {pdfError && (
                <p className="text-xs text-rose-600 self-center">{pdfError}</p>
              )}
            </div>
          </div>

          <div className="shrink-0 flex flex-col items-center">
            <ScoreGauge score={overall_score} size={150} strokeWidth={12} label="Overall Match" />
          </div>
        </div>

        {/* Role Recommendations (Independent from JD match score) */}
        {role_recommendations.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div>
                <h2 className="text-base font-semibold text-slate-900 flex items-center">
                  <Target className="w-4 h-4 mr-2 text-teal-700" />
                  Role Recommendations (Taxonomy Fit)
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Deterministic alignment between your candidate skills and target tech roles (scored independently from the JD)
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              {role_recommendations.slice(0, 4).map((roleItem, idx) => (
                <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">{roleItem.role}</h3>
                      <p className="text-[11px] text-slate-500 mt-0.5">{roleItem.reason}</p>
                    </div>
                    <div className="text-right shrink-0 ml-3">
                      <div className="text-sm font-bold text-teal-800">{Math.round(roleItem.score)}%</div>
                      {getFitBadge(roleItem.fit_level)}
                    </div>
                  </div>

                  {roleItem.matched_skills.length > 0 && (
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                        Matched Skills:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {roleItem.matched_skills.map((skill, sIdx) => (
                          <span
                            key={sIdx}
                            className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {roleItem.missing_core_skills.length > 0 && (
                    <div>
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                        Core Skills to Strengthen:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {roleItem.missing_core_skills.slice(0, 4).map((skill, sIdx) => (
                          <span
                            key={sIdx}
                            className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Score Breakdown Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-slate-900 mb-1">Score Breakdown</h2>
            <p className="text-xs text-slate-500 mb-6">Sub-score results across four key criteria</p>
            <ScoreBreakdownChart scoreBreakdown={score_breakdown} />
          </div>

          {/* Transparent Weight Explanation */}
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2 text-slate-900 font-semibold text-sm mb-3">
                <Info className="w-4 h-4 text-teal-700" />
                <span>Score Weighting Formula</span>
              </div>
              <p className="text-xs text-slate-600 mb-4 leading-relaxed">
                Your overall score is calculated deterministically from four components:
              </p>
              <ul className="space-y-2.5 text-xs text-slate-700 font-medium">
                <li className="flex justify-between items-center py-1 border-b border-slate-200">
                  <span className="flex items-center"><Target className="w-3.5 h-3.5 mr-1.5 text-teal-700" /> Skill Coverage</span>
                  <span className="font-semibold text-slate-900">{((weights?.skill || 0.4) * 100).toFixed(0)}%</span>
                </li>
                <li className="flex justify-between items-center py-1 border-b border-slate-200">
                  <span className="flex items-center"><Search className="w-3.5 h-3.5 mr-1.5 text-teal-700" /> Text Similarity</span>
                  <span className="font-semibold text-slate-900">{((weights?.text_similarity || 0.3) * 100).toFixed(0)}%</span>
                </li>
                <li className="flex justify-between items-center py-1 border-b border-slate-200">
                  <span className="flex items-center"><Briefcase className="w-3.5 h-3.5 mr-1.5 text-teal-700" /> Experience</span>
                  <span className="font-semibold text-slate-900">{((weights?.experience || 0.15) * 100).toFixed(0)}%</span>
                </li>
                <li className="flex justify-between items-center py-1 font-semibold">
                  <span className="flex items-center"><Award className="w-3.5 h-3.5 mr-1.5 text-teal-700" /> ATS Quality</span>
                  <span className="font-semibold text-slate-900">{((weights?.ats || 0.15) * 100).toFixed(0)}%</span>
                </li>
              </ul>
            </div>
            <p className="text-[11px] text-slate-500 mt-4 italic leading-tight">
              Text Similarity is computed using Normalized Term-Frequency Cosine Similarity.
            </p>
          </div>
        </div>

        {/* Skill Analysis Section */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <h2 className="text-base font-semibold text-slate-900">Skill Analysis</h2>

          <div className="space-y-4">
            {/* Matching Skills */}
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Matching Skills ({matching_skills.length})
              </h3>
              {matching_skills.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No matching skills detected.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {matching_skills.map((skill, i) => (
                    <SkillBadge key={i} skill={skill} type="matched" />
                  ))}
                </div>
              )}
            </div>

            {/* Missing Required Skills */}
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Missing Required Skills ({missing_required_skills.length})
              </h3>
              {missing_required_skills.length === 0 ? (
                <p className="text-xs text-emerald-600 font-medium">All required skills detected in resume!</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {missing_required_skills.map((skill, i) => (
                    <SkillBadge key={i} skill={skill} type="missing_required" />
                  ))}
                </div>
              )}
            </div>

            {/* Missing Preferred Skills */}
            {missing_preferred_skills.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Missing Preferred Skills ({missing_preferred_skills.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {missing_preferred_skills.map((skill, i) => (
                    <SkillBadge key={i} skill={skill} type="missing_preferred" />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Prioritized Skill Gaps */}
          {prioritized_skill_gaps.length > 0 && (
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Prioritized Skill Gaps & Recommendations ({prioritized_skill_gaps.length})
              </h3>
              <div className="space-y-2.5">
                {prioritized_skill_gaps.map((gap, i) => (
                  <div key={i} className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-slate-900 text-sm">{gap.skill}</span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-200 text-slate-700 uppercase">
                          {gap.category}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                          {gap.required_or_preferred}
                        </span>
                      </div>
                      {getPriorityBadge(gap.priority)}
                    </div>
                    <p className="text-slate-600 leading-relaxed">{gap.reason}</p>
                    <p className="text-slate-800 font-medium">
                      <span className="text-teal-800 font-semibold">Action:</span> {gap.action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Experience & Education Alignment */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Experience */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-5 h-5 text-teal-700" />
                <h3 className="text-base font-semibold text-slate-900">Experience Alignment</h3>
              </div>
              {getStatusBadge(experience_alignment?.status)}
            </div>

            <div className="space-y-2 text-xs text-slate-600">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span>Required Experience:</span>
                <span className="font-semibold text-slate-900">
                  {experience_alignment?.required_years !== null && experience_alignment?.required_years !== undefined
                    ? `${experience_alignment.required_years} years`
                    : 'Not specified'}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span>Detected Experience:</span>
                <span className="font-semibold text-slate-900">
                  {experience_alignment?.candidate_years !== null && experience_alignment?.candidate_years !== undefined
                    ? `${experience_alignment.candidate_years} years`
                    : 'Not specified'}
                </span>
              </div>
              <p className="pt-2 text-slate-600 leading-relaxed">
                {experience_alignment?.explanation || 'Not enough information detected.'}
              </p>
            </div>
          </div>

          {/* Education */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <GraduationCap className="w-5 h-5 text-teal-700" />
                <h3 className="text-base font-semibold text-slate-900">Education Alignment</h3>
              </div>
              {getStatusBadge(education_alignment?.status)}
            </div>

            <div className="space-y-2 text-xs text-slate-600">
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span>Required Degree:</span>
                <span className="font-semibold text-slate-900">
                  {education_alignment?.required_degree || 'Not specified'}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100">
                <span>Detected Degree:</span>
                <span className="font-semibold text-slate-900">
                  {education_alignment?.candidate_degree || 'Not specified'}
                </span>
              </div>
              <p className="pt-2 text-slate-600 leading-relaxed">
                {education_alignment?.explanation || 'Not enough information detected.'}
              </p>
            </div>
          </div>
        </div>

        {/* ATS Quality Section */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-base font-semibold text-slate-900">ATS Structure & Formatting Analysis</h2>
              <p className="text-xs text-slate-500">Heuristic resume-quality checker</p>
            </div>
            <span className="text-sm font-bold text-teal-800 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
              {ats_breakdown?.score !== undefined ? Math.round(ats_breakdown.score) : 0} / 100
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-500">Section Completeness</p>
              <p className="text-lg font-bold text-slate-900 mt-1">
                {atsDetails.section_completeness_score !== undefined ? Math.round(atsDetails.section_completeness_score) : 0}%
              </p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-500">Action Verb Density</p>
              <p className="text-lg font-bold text-slate-900 mt-1">
                {atsDetails.action_verb_score !== undefined ? Math.round(atsDetails.action_verb_score) : 0}%
              </p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-500">Quantifiable Metrics</p>
              <p className="text-lg font-bold text-slate-900 mt-1">
                {atsDetails.metrics_count !== undefined ? atsDetails.metrics_count : 0} detected
              </p>
            </div>
          </div>

          <div className="text-xs text-slate-600 space-y-1.5 pt-1">
            <p>
              <span className="font-semibold text-slate-800">Sections Found:</span>{' '}
              {atsDetails.sections_found?.length ? atsDetails.sections_found.join(', ') : 'None'}
            </p>
            {atsDetails.sections_missing?.length > 0 && (
              <p className="text-amber-800">
                <span className="font-semibold">Missing Sections:</span> {atsDetails.sections_missing.join(', ')}
              </p>
            )}
          </div>

          {/* Actionable ATS Recommendations */}
          {ats_recommendations.length > 0 && (
            <div className="pt-4 border-t border-slate-100 space-y-3">
              <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                ATS Optimization Advice ({ats_recommendations.length})
              </h3>
              <div className="space-y-2.5">
                {ats_recommendations.map((atsRec, i) => (
                  <div key={i} className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{atsRec.title}</span>
                      {getPriorityBadge(atsRec.priority)}
                    </div>
                    <p className="text-slate-600 leading-relaxed">{atsRec.issue}</p>
                    <p className="text-slate-800 font-medium">
                      <span className="text-teal-800 font-semibold">Suggested Action:</span> {atsRec.action}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Unified Improvement Recommendations */}
        {unified_recommendations.length > 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-semibold text-slate-900 flex items-center">
              <Layers className="w-4 h-4 mr-2 text-teal-700" />
              Unified Improvement Recommendations ({unified_recommendations.length})
            </h2>
            <div className="space-y-3">
              {unified_recommendations.map((rec, i) => (
                <div key={i} className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-[11px] font-bold shrink-0">
                        {i + 1}
                      </span>
                      <span className="font-bold text-slate-900 text-sm">{rec.title}</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-200 text-slate-700 uppercase tracking-wider">
                        {rec.type}
                      </span>
                    </div>
                    {getPriorityBadge(rec.priority)}
                  </div>
                  <p className="text-slate-600 leading-relaxed pl-7">{rec.reason}</p>
                  <div className="pl-7 text-slate-800 font-medium">
                    <span className="text-teal-800 font-semibold">Action:</span> {rec.action}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : recommendations.length > 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
            <h2 className="text-base font-semibold text-slate-900 flex items-center">
              <Layers className="w-4 h-4 mr-2 text-teal-700" />
              Actionable Recommendations
            </h2>
            <ul className="space-y-3">
              {recommendations.map((rec, i) => (
                <li key={i} className="flex items-start text-xs sm:text-sm text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-xs font-bold mr-3 shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}
