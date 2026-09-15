import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import StatCard from '../components/common/StatCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import { useAuth } from '../context/AuthContext';
import { getAnalysisHistory } from '../api/analysis';
import { getResumes } from '../api/resumes';
import { FileText, PlusCircle, ArrowRight, History, BarChart2 } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const [historyRes, resumesRes] = await Promise.all([
          getAnalysisHistory({ limit: 5 }),
          getResumes(),
        ]);
        setHistory(historyRes.analyses || []);
        setResumes(resumesRes.resumes || []);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const averageScore = history.length > 0
    ? Math.round(history.reduce((acc, curr) => acc + (curr.overall_score || 0), 0) / history.length)
    : null;

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Welcome Banner */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Welcome back, <span className="text-teal-700">{user?.email?.split('@')[0] || 'User'}</span>
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              Upload a resume and job description to get an explainable match score.
            </p>
          </div>
          <Link
            to="/app/analyze"
            className="inline-flex items-center px-4 py-2.5 bg-teal-700 hover:bg-teal-800 text-white text-sm font-medium rounded-lg shadow-sm transition-colors shrink-0"
          >
            <PlusCircle className="w-4 h-4 mr-2" />
            Analyze Resume
          </Link>
        </div>

        {error && <ErrorAlert message={error} />}

        {loading ? (
          <LoadingSpinner label="Loading dashboard metrics..." />
        ) : (
          <>
            {/* Stat Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <StatCard
                title="Resumes Uploaded"
                value={resumes.length}
                icon={FileText}
                subtitle="Active documents in your library"
              />
              <StatCard
                title="Total Analyses"
                value={history.length}
                icon={History}
                subtitle="Completed match evaluations"
              />
              <StatCard
                title="Recent Avg Score"
                value={averageScore !== null ? `${averageScore}%` : 'N/A'}
                icon={BarChart2}
                subtitle={history.length > 0 ? 'Based on recent evaluations' : 'No analyses performed yet'}
              />
            </div>

            {/* Recent Analyses Section */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-slate-900">Recent Analyses</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Your latest job compatibility evaluations</p>
                </div>
                {history.length > 0 && (
                  <Link
                    to="/app/history"
                    className="text-xs font-medium text-teal-700 hover:text-teal-800 flex items-center"
                  >
                    View all <ArrowRight className="w-3 h-3 ml-1" />
                  </Link>
                )}
              </div>

              {history.length === 0 ? (
                <div className="p-12 text-center">
                  <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-4">
                    <History className="w-6 h-6" />
                  </div>
                  <h3 className="text-sm font-semibold text-slate-900 mb-1">No analyses yet</h3>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto mb-6">
                    Start by uploading a resume and pasting a job description to see your match results.
                  </p>
                  <Link
                    to="/app/analyze"
                    className="inline-flex items-center px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-medium rounded-lg transition-colors"
                  >
                    <PlusCircle className="w-3.5 h-3.5 mr-1.5" />
                    Start New Analysis
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-slate-200">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
                    >
                      <div className="min-w-0 pr-4">
                        <h3 className="text-sm font-medium text-slate-900 truncate">
                          {item.job_title || 'Untitled Job Position'}
                        </h3>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {item.resume_filename ? item.resume_filename : 'Resume'} &bull;{' '}
                          {new Date(item.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-4 shrink-0">
                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-teal-50 text-teal-800 border border-teal-200">
                          {Math.round(item.overall_score)}% Match
                        </span>
                        <Link
                          to={`/app/results/${item.id}`}
                          className="text-xs font-medium text-slate-600 hover:text-slate-900"
                        >
                          View Results
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
