import { request } from './client';

export async function previewAnalysis(resumeText, jdText) {
  return request('/api/v1/analysis/preview', {
    method: 'POST',
    body: {
      resume_text: resumeText,
      job_description_text: jdText,
    },
  });
}

export async function analyzeResume(payload) {
  // Support payload object { resume_id, job_title, job_description_text }
  // or positional args (resume_id, job_title, job_description_text)
  const body = typeof payload === 'object' && payload !== null
    ? {
        resume_id: payload.resume_id,
        job_title: payload.job_title,
        job_description_text: payload.job_description_text || payload.job_description,
      }
    : {
        resume_id: arguments[0],
        job_title: arguments[1],
        job_description_text: arguments[2],
      };

  const res = await request('/api/v1/analysis/run', {
    method: 'POST',
    body,
  });

  if (res) {
    if (!res.id && res.analysis_id) res.id = res.analysis_id;
    if (!res.analysis_id && res.id) res.analysis_id = res.id;
  }
  return res;
}

export async function getAnalysisHistory(options = {}) {
  let skip = 0;
  let limit = 20;

  if (typeof options === 'number') {
    limit = options;
  } else if (typeof options === 'object' && options !== null) {
    skip = options.skip ?? 0;
    limit = options.limit ?? 20;
  }

  const data = await request(`/api/v1/analysis/history?skip=${skip}&limit=${limit}`, {
    method: 'GET',
  });

  const list = Array.isArray(data) ? data : (data?.analyses || []);
  return { analyses: list };
}

export async function getAnalysisById(analysisId) {
  const res = await request(`/api/v1/analysis/${analysisId}`, {
    method: 'GET',
  });
  if (res) {
    if (!res.id && res.analysis_id) res.id = res.analysis_id;
    if (!res.analysis_id && res.id) res.analysis_id = res.id;
  }
  return res;
}

export async function deleteAnalysis(analysisId) {
  return request(`/api/v1/analysis/${analysisId}`, {
    method: 'DELETE',
  });
}

export async function downloadAnalysisPdf(analysisId) {
  const token = localStorage.getItem('hirelens_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/${analysisId}/report`, {
    method: 'GET',
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('hirelens_token');
    window.dispatchEvent(new Event('hirelens_unauthorized'));
    throw new Error('Authentication session expired. Please log in again.');
  }

  if (!response.ok) {
    let errorMsg = 'Failed to generate and download PDF report.';
    try {
      const err = await response.json();
      if (err.detail) errorMsg = err.detail;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return await response.blob();
}

// Named aliases to preserve compatibility with both naming styles
export const previewAnalysisApi = previewAnalysis;
export const runAnalysisApi = analyzeResume;
export const getHistoryApi = getAnalysisHistory;
export const getSingleAnalysisApi = getAnalysisById;
export const deleteAnalysisApi = deleteAnalysis;
export const downloadAnalysisPdfApi = downloadAnalysisPdf;
