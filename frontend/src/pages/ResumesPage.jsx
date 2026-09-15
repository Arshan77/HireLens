import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import { getResumes, uploadResume, deleteResume } from '../api/resumes';
import { FileText, Upload, Trash2, PlusCircle, CheckCircle2, ArrowRight } from 'lucide-react';

export default function ResumesPage() {
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getResumes();
      setResumes(res.resumes || []);
    } catch (err) {
      setError(err.message || 'Failed to load uploaded resumes.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('File size exceeds 5 MB limit.');
      return;
    }
    setUploadFile(file);
    setUploadError(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadError(null);
    try {
      await uploadResume(uploadFile);
      setUploadFile(null);
      await fetchResumes();
    } catch (err) {
      setUploadError(err.message || 'We couldn\'t process this file. Please check that it is a valid PDF or DOCX under 5 MB.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    try {
      await deleteResume(id);
      setResumes((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(err.message || 'Failed to delete resume.');
    }
  };

  return (
    <AppShell>
      <div className="space-y-8 max-w-5xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Resume Library</h1>
            <p className="mt-1 text-sm text-slate-600">
              Manage your uploaded PDF and DOCX resume documents.
            </p>
          </div>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {/* Upload Form Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900 mb-4">Upload New Resume</h2>
          <form onSubmit={handleUpload} className="flex flex-col sm:flex-row items-center gap-4">
            <div className="flex-1 w-full">
              <input
                type="file"
                id="resume-page-upload"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100 cursor-pointer border border-slate-300 rounded-lg"
              />
            </div>
            <button
              type="submit"
              disabled={isUploading || !uploadFile}
              className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2.5 bg-teal-700 hover:bg-teal-800 text-white text-sm font-medium rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              <Upload className="w-4 h-4 mr-2" />
              {isUploading ? 'Uploading...' : 'Upload Resume'}
            </button>
          </form>
          {uploadError && <p className="text-xs text-rose-600 mt-2">{uploadError}</p>}
        </div>

        {/* Resumes List */}
        {loading ? (
          <LoadingSpinner label="Loading resume library..." />
        ) : resumes.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-4">
              <FileText className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-900 mb-1">No resumes uploaded</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Upload your first resume above to get started with job matching evaluations.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {resumes.map((resume) => {
              const isPdf = resume.file_type?.toLowerCase().includes('pdf') || resume.filename.endsWith('.pdf');
              return (
                <div
                  key={resume.id}
                  className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex items-start justify-between hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-start space-x-3 min-w-0 pr-2">
                    <div className="w-10 h-10 rounded-lg bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-700 shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-sm font-semibold text-slate-900 truncate">
                        {resume.filename}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {isPdf ? 'PDF Document' : 'DOCX Document'} &bull;{' '}
                        {(resume.file_size / 1024).toFixed(0)} KB
                      </p>
                      <p className="text-[11px] text-slate-400 mt-1">
                        Uploaded{' '}
                        {(() => {
                          const dateVal = resume.uploaded_at || resume.created_at;
                          return dateVal && !isNaN(new Date(dateVal).getTime())
                            ? new Date(dateVal).toLocaleDateString()
                            : 'Recently';
                        })()}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-col items-end space-y-2 shrink-0">
                    <button
                      onClick={() => navigate('/app/analyze')}
                      className="inline-flex items-center text-xs font-medium text-teal-700 hover:text-teal-900 bg-teal-50 px-2.5 py-1.5 rounded-md hover:bg-teal-100 transition-colors"
                    >
                      Analyze <ArrowRight className="w-3 h-3 ml-1" />
                    </button>
                    <button
                      onClick={() => handleDelete(resume.id)}
                      className="text-xs text-slate-400 hover:text-rose-600 p-1 transition-colors"
                      title="Delete resume"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}
