import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import HistoryPage from '../pages/HistoryPage';
import * as analysisApi from '../api/analysis';
import { AuthProvider } from '../context/AuthContext';

vi.mock('../api/analysis', () => ({
  getAnalysisHistory: vi.fn(),
  deleteAnalysis: vi.fn(),
}));

describe('History Page', () => {
  const mockHistory = [
    {
      id: 'h-1',
      job_title: 'Frontend Engineer',
      overall_score: 85.0,
      resume_filename: 'resume.pdf',
      created_at: '2026-09-14T10:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders analysis history list', async () => {
    analysisApi.getAnalysisHistory.mockResolvedValueOnce({ analyses: mockHistory });

    render(
      <BrowserRouter>
        <AuthProvider>
          <HistoryPage />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
    });
  });

  it('handles delete flow confirmation', async () => {
    analysisApi.getAnalysisHistory.mockResolvedValueOnce({ analyses: mockHistory });
    analysisApi.deleteAnalysis.mockResolvedValueOnce({ message: 'Deleted' });

    render(
      <BrowserRouter>
        <AuthProvider>
          <HistoryPage />
        </AuthProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
    });

    const deleteBtn = screen.getByRole('button', { name: /delete analysis/i });
    fireEvent.click(deleteBtn);

    expect(screen.getByText('Delete?')).toBeInTheDocument();

    const confirmYes = screen.getByText('Yes');
    fireEvent.click(confirmYes);

    await waitFor(() => {
      expect(analysisApi.deleteAnalysis).toHaveBeenCalledWith('h-1');
    });
  });
});
