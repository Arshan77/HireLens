import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import ErrorAlert from '../components/common/ErrorAlert';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getResumes, uploadResume } from '../api/resumes';
import { analyzeResume } from '../api/analysis';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, RefreshCw } from 'lucide-react';

export default function AnalyzePage() {
  const navigate = useNavigate();

  // Resume selection state
  const [resumes, setResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState('');
  const [loadingResumes, setLoadingResumes] = useState(true);

  // File upload state
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Job description state
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');

  // Analysis process state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      setLoadingResumes(true);
      const res = await getResumes();
      const list = res.resumes || [];
      setResumes(list);
      if (list.length > 0 && !selectedResumeId) {
        setSelectedResumeId(list[0].id);
      }
    } catch (err) {
      console.error('Error fetching resumes:', err);
    } finally {
      setLoadingResumes(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('File size exceeds 5 MB limit.');
      return;
    }

    // Validate extension
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setUploadError('Please select a valid PDF or DOCX file.');
      return;
    }

    setUploadFile(file);
    setUploadError(null);
    setUploadSuccess(false);
  };

  const handleUploadSubmit = async () => {
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const newResume = await uploadResume(uploadFile);
      setUploadSuccess(true);
      setUploadFile(null);
      // Refresh list & select newly uploaded resume
      await fetchResumes();
      if (newResume && newResume.id) {
        setSelectedResumeId(newResume.id);
      }
    } catch (err) {
      setUploadError(err.message || 'We couldn\'t process this file. Please check that it is a valid PDF or DOCX under 5 MB.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setAnalysisError(null);

    if (!selectedResumeId) {
      setAnalysisError('Please select or upload a resume for analysis.');
      return;
    }

    if (!jobDescription || jobDescription.trim().length < 20) {
      setAnalysisError('Please provide a complete job description (at least 20 characters).');
      return;
    }

    setIsAnalyzing(true);

    try {
      const result = await analyzeResume({
        resume_id: selectedResumeId,
        job_description_text: jobDescription.trim(),
        job_title: jobTitle.trim() || undefined,
      });

      const analysisId = result?.id || result?.analysis_id;
      if (analysisId) {
        navigate(`/app/results/${analysisId}`);
      } else {
        throw new Error('Analysis returned invalid response structure.');
      }
    } catch (err) {
      setAnalysisError(err.message || 'We couldn\'t complete this analysis. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Analyze Resume Match</h1>
          <p className="mt-1 text-sm text-slate-600">
            Compare your resume against a job description to extract skill coverage, experience alignment, and quality scoring.
          </p>
        </div>

        {analysisError && <ErrorAlert message={analysisError} onDismiss={() => setAnalysisError(null)} />}

        <form onSubmit={handleAnalyze} className="space-y-8">
          {/* Step 1: Resume Selection / Upload */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
            <div className="flex items-center space-x-3 pb-4 border-b border-slate-100">
              <span className="w-7 h-7 rounded-full bg-teal-700 text-white flex items-center justify-center text-sm font-semibold">
                1
              </span>
              <h2 className="text-base font-semibold text-slate-900">Select or Upload Resume</h2>
            </div>

            {loadingResumes ? (
              <LoadingSpinner label="Loading your resumes..." size="sm" />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Choose from Existing */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-slate-700">
                    Existing Uploaded Resumes
                  </label>
                  {resumes.length === 0 ? (
                    <p className="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200">
                      No saved resumes found. Upload one using the form on the right.
                    </p>
                  ) : (
                    <select
                      value={selectedResumeId}
                      onChange={(e) => setSelectedResumeId(e.target.value)}
                      className="block w-full border border-slate-300 rounded-lg p-2.5 text-sm bg-white text-slate-800 focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                    >
                      {resumes.map((r) => {
                        const dateVal = r.uploaded_at || r.created_at;
                        const dateStr = dateVal && !isNaN(new Date(dateVal).getTime())
                          ? new Date(dateVal).toLocaleDateString()
                          : '';
                        return (
                          <option key={r.id} value={r.id}>
                            {r.filename} {dateStr ? `(${dateStr})` : ''}
                          </option>
                        );
                      })}
                    </select>
                  )}
                </div>

                {/* Upload New Resume */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-slate-700">
                    Or Upload New File (PDF, DOCX max 5MB)
                  </label>
                  <div className="border-2 border-dashed border-slate-300 rounded-lg p-4 text-center hover:border-teal-500 transition-colors bg-slate-50">
                    <input
                      type="file"
                      id="resume-file-input"
                      accept=".pdf,.docx"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <label htmlFor="resume-file-input" className="cursor-pointer block">
                      <Upload className="w-6 h-6 text-slate-400 mx-auto mb-2" />
                      <span className="text-xs font-medium text-teal-700 hover:text-teal-800">
                        {uploadFile ? uploadFile.name : 'Click to select a resume file'}
                      </span>
                      {uploadFile && (
                        <span className="block text-xs text-slate-500 mt-1">
                          {(uploadFile.size / 1024).toFixed(0)} KB
                        </span>
                      )}
                    </label>

                    {uploadFile && (
                      <button
                        type="button"
                        onClick={handleUploadSubmit}
                        disabled={isUploading}
                        className="mt-3 px-3 py-1.5 bg-teal-700 hover:bg-teal-800 text-white text-xs font-medium rounded transition-colors disabled:opacity-50 inline-flex items-center"
                      >
                        {isUploading ? (
                          <>
                            <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                            Uploading...
                          </>
                        ) : (
                          'Upload Now'
                        )}
                      </button>
                    )}
                  </div>

                  {uploadError && (
                    <p className="text-xs text-rose-600 flex items-center">
                      <AlertCircle className="w-3.5 h-3.5 mr-1 shrink-0" />
                      {uploadError}
                    </p>
                  )}
                  {uploadSuccess && (
                    <p className="text-xs text-emerald-600 flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 shrink-0" />
                      Resume uploaded successfully!
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Step 2: Job Description */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
            <div className="flex items-center space-x-3 pb-4 border-b border-slate-100">
              <span className="w-7 h-7 rounded-full bg-teal-700 text-white flex items-center justify-center text-sm font-semibold">
                2
              </span>
              <h2 className="text-base font-semibold text-slate-900">Job Details</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="jobTitle" className="block text-sm font-medium text-slate-700">
                  Job Title <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <input
                  id="jobTitle"
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Senior Software Engineer"
                  className="mt-1 block w-full border border-slate-300 rounded-lg p-2.5 text-sm text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label htmlFor="jobDescription" className="block text-sm font-medium text-slate-700">
                    Job Description <span className="text-rose-500">*</span>
                  </label>
                  <span className="text-xs text-slate-400">
                    {jobDescription.length} characters
                  </span>
                </div>
                <textarea
                  id="jobDescription"
                  rows={8}
                  required
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the complete job description here, including responsibilities, required skills, and qualifications..."
                  className="block w-full border border-slate-300 rounded-lg p-3 text-sm text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 leading-relaxed font-sans"
                />
                <p className="mt-1 text-xs text-slate-500">
                  Tip: Include the complete text for the best skill extraction and text similarity results.
                </p>
              </div>
            </div>
          </div>

          {/* Action CTA */}
          <div className="flex items-center justify-end space-x-4">
            <button
              type="submit"
              disabled={isAnalyzing || !selectedResumeId || jobDescription.trim().length < 20}
              className="inline-flex items-center justify-center px-6 py-3 bg-teal-700 hover:bg-teal-800 text-white font-medium text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing Match...
                </>
              ) : (
                <>
                  <span>Analyze Match</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          </div>

          {isAnalyzing && (
            <p className="text-xs text-center text-slate-500 animate-pulse">
              Parsing resume text, calculating TF-IDF text similarity, and scoring skill coverage. This takes just a few seconds.
            </p>
          )}
        </form>
      </div>
    </AppShell>
  );
}
