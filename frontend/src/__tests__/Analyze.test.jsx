import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AnalyzePage from '../pages/AnalyzePage';
import * as resumesApi from '../api/resumes';
import * as analysisApi from '../api/analysis';
import { AuthProvider } from '../context/AuthContext';

vi.mock('../api/resumes', () => ({
  getResumes: vi.fn(),
  uploadResume: vi.fn(),
}));

vi.mock('../api/analysis', () => ({
  analyzeResume: vi.fn(),
}));

describe('Analyze Page Workflow', () => {
  const mockResumes = [
    { id: 'res-1', filename: 'software_engineer.pdf', file_size: 102400, uploaded_at: '2026-09-14T10:00:00Z' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    resumesApi.getResumes.mockResolvedValue({ resumes: mockResumes });
  });

  it('loads and displays existing resumes', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <AnalyzePage />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/software_engineer.pdf/i)).toBeInTheDocument();
    });
  });

  it('prevents analysis submission with short job description', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <AnalyzePage />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/software_engineer.pdf/i)).toBeInTheDocument();
    });

    const textarea = screen.getByLabelText(/job description/i);
    fireEvent.change(textarea, { target: { value: 'Too short' } });

    const submitBtn = screen.getByRole('button', { name: /analyze match/i });
    expect(submitBtn).toBeDisabled();
  });

  it('triggers analysis API call with valid payload', async () => {
    analysisApi.analyzeResume.mockResolvedValueOnce({
      id: 'analysis-123',
      overall_score: 82.5,
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <AnalyzePage />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/software_engineer.pdf/i)).toBeInTheDocument();
    });

    const titleInput = screen.getByLabelText(/job title/i);
    fireEvent.change(titleInput, { target: { value: 'Backend Developer' } });

    const textarea = screen.getByLabelText(/job description/i);
    fireEvent.change(textarea, {
      target: { value: 'We are seeking a Backend Developer proficient in Python, FastAPI, and PostgreSQL.' },
    });

    const submitBtn = screen.getByRole('button', { name: /analyze match/i });
    expect(submitBtn).not.toBeDisabled();
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(analysisApi.analyzeResume).toHaveBeenCalledWith({
        resume_id: 'res-1',
        job_description_text: 'We are seeking a Backend Developer proficient in Python, FastAPI, and PostgreSQL.',
        job_title: 'Backend Developer',
      });
    });
  });
});
