import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ResultsPage from '../pages/ResultsPage';
import * as analysisApi from '../api/analysis';
import { AuthProvider } from '../context/AuthContext';

vi.mock('../api/analysis', () => ({
  getAnalysisById: vi.fn(),
  downloadAnalysisPdf: vi.fn(),
}));

describe('Results Page Component', () => {
  const mockAnalysisResponse = {
    analysis_id: 'analysis-999',
    overall_score: 81.1,
    job_title: 'Senior Python Engineer',
    score_breakdown: {
      skill_score: 100.0,
      text_similarity_score: 45.2,
      experience_score: 100.0,
      ats_quality_score: 83.3,
    },
    weights: {
      skill: 0.40,
      text_similarity: 0.30,
      experience: 0.15,
      ats: 0.15,
    },
    matching_skills: ['Python', 'FastAPI', 'PostgreSQL'],
    missing_required_skills: ['Docker', 'Kubernetes'],
    missing_preferred_skills: ['Redis'],
    experience_alignment: {
      required_years: 3,
      candidate_years: 5,
      score: 100,
      status: 'aligned',
      explanation: 'Candidate experience meets requirement.',
    },
    education_alignment: {
      required_degree: 'Bachelor of Science',
      candidate_degree: 'Bachelor of Science in Computer Science',
      score: 100,
      status: 'aligned',
      explanation: 'Candidate holds required degree.',
    },
    ats_breakdown: {
      score: 83.3,
      details: {
        section_completeness_score: 100,
        action_verb_score: 75,
        quantifiable_metrics_score: 75,
        sections_found: ['Experience', 'Education', 'Skills'],
        sections_missing: [],
        metrics_count: 4,
      },
    },
    recommendations: [
      'Add Docker and Kubernetes to your skills or project descriptions.',
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders complete analysis breakdown correctly', async () => {
    analysisApi.getAnalysisById.mockResolvedValueOnce(mockAnalysisResponse);

    render(
      <MemoryRouter initialEntries={['/app/results/analysis-999']}>
        <AuthProvider>
          <Routes>
            <Route path="/app/results/:analysisId" element={<ResultsPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Senior Python Engineer')).toBeInTheDocument();
      expect(screen.getByText('81%')).toBeInTheDocument();
      expect(screen.getByText('Python')).toBeInTheDocument();
      expect(screen.getByText('Docker')).toBeInTheDocument();
      expect(screen.getByText('Kubernetes')).toBeInTheDocument();
      expect(screen.getByText(/Add Docker and Kubernetes/i)).toBeInTheDocument();
    });
  });

  it('handles API error when analysis ID is invalid', async () => {
    analysisApi.getAnalysisById.mockRejectedValueOnce(new Error('Analysis not found or unauthorized.'));

    render(
      <MemoryRouter initialEntries={['/app/results/invalid-id']}>
        <AuthProvider>
          <Routes>
            <Route path="/app/results/:analysisId" element={<ResultsPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Analysis not found or unauthorized/i)).toBeInTheDocument();
    });
  });

  it('renders Phase 5 role recommendations, prioritized skill gaps, and ATS advice', async () => {
    const phase5Response = {
      ...mockAnalysisResponse,
      role_recommendations: [
        {
          role: 'Python Developer',
          score: 85.0,
          fit_level: 'Strong fit',
          matched_skills: ['Python', 'FastAPI'],
          missing_core_skills: ['Django'],
          reason: 'Strong alignment with Python Developer requirements.',
        },
      ],
      prioritized_skill_gaps: [
        {
          skill: 'Docker',
          category: 'devops',
          priority: 'high',
          required_or_preferred: 'required',
          reason: 'Docker is listed as a required devops skill in the job description.',
          action: 'Add a relevant Docker project before applying.',
        },
      ],
      ats_recommendations: [
        {
          category: 'metrics',
          priority: 'medium',
          title: 'Add Measurable Achievements',
          issue: 'Detected 2 quantifiable metrics in your resume.',
          action: 'Where truthful, incorporate measurable outcomes.',
        },
      ],
      unified_recommendations: [
        {
          type: 'skill_gap',
          priority: 'high',
          title: 'Acquire / Highlight Docker',
          reason: 'Docker is listed as a required skill.',
          action: 'Add a relevant Docker project before applying.',
          evidence: { skill: 'Docker' },
        },
      ],
    };

    analysisApi.getAnalysisById.mockResolvedValueOnce(phase5Response);

    render(
      <MemoryRouter initialEntries={['/app/results/analysis-999']}>
        <AuthProvider>
          <Routes>
            <Route path="/app/results/:analysisId" element={<ResultsPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Role Recommendations \(Taxonomy Fit\)/i)).toBeInTheDocument();
      expect(screen.getByText('Python Developer')).toBeInTheDocument();
      expect(screen.getByText('Strong fit')).toBeInTheDocument();
      expect(screen.getByText(/Prioritized Skill Gaps & Recommendations/i)).toBeInTheDocument();
      expect(screen.getByText(/ATS Optimization Advice/i)).toBeInTheDocument();
      expect(screen.getByText(/Unified Improvement Recommendations/i)).toBeInTheDocument();
    });
  });

  it('renders Download PDF Report button and triggers download', async () => {
    analysisApi.getAnalysisById.mockResolvedValueOnce(mockAnalysisResponse);
    const mockBlob = new Blob(['%PDF-1.4 mock content'], { type: 'application/pdf' });
    analysisApi.downloadAnalysisPdf.mockResolvedValueOnce(mockBlob);

    window.URL.createObjectURL = vi.fn().mockReturnValue('blob:http://localhost/fake-pdf');
    window.URL.revokeObjectURL = vi.fn();
    const anchorClickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});

    render(
      <MemoryRouter initialEntries={['/app/results/analysis-999']}>
        <AuthProvider>
          <Routes>
            <Route path="/app/results/:analysisId" element={<ResultsPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    const downloadBtn = await screen.findByRole('button', { name: /Download PDF Report/i });
    expect(downloadBtn).toBeInTheDocument();

    fireEvent.click(downloadBtn);

    await waitFor(() => {
      expect(analysisApi.downloadAnalysisPdf).toHaveBeenCalledWith('analysis-999');
    });
  });
});
