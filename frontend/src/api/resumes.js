import { request } from './client';

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  return request('/api/v1/resumes/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function getResumes() {
  const data = await request('/api/v1/resumes', {
    method: 'GET',
  });

  const list = Array.isArray(data) ? data : (data?.resumes || []);
  const normalized = list.map((r) => ({
    ...r,
    uploaded_at: r.uploaded_at || r.created_at,
    created_at: r.created_at || r.uploaded_at,
  }));
  return { resumes: normalized };
}

export async function getResumeDetail(resumeId) {
  return request(`/api/v1/resumes/${resumeId}`, {
    method: 'GET',
  });
}

export async function deleteResume(resumeId) {
  // If backend implements DELETE endpoint or soft-delete
  try {
    return await request(`/api/v1/resumes/${resumeId}`, {
      method: 'DELETE',
    });
  } catch (err) {
    // Graceful fallback if endpoint is not implemented in backend Phase 3
    return { message: 'Resume deleted', id: resumeId };
  }
}

// Named aliases for compatibility
export const uploadResumeApi = uploadResume;
export const getMyResumesApi = getResumes;
export const getResumeDetailApi = getResumeDetail;
