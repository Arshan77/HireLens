import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import { getAnalysisHistory, deleteAnalysis } from '../api/analysis';
import { History, Trash2, Eye, PlusCircle, AlertCircle } from 'lucide-react';

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await getAnalysisHistory({ limit: 50 });
      setHistory(res.analyses || []);
    } catch (err) {
      setError(err.message || 'Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      setDeletingId(id);
      await deleteAnalysis(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
      setConfirmDeleteId(null);
    } catch (err) {
      setError(err.message || 'Failed to delete analysis record.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Analysis History</h1>
            <p className="mt-1 text-sm text-slate-600">
              View and manage your previous resume match evaluations.
            </p>
          </div>
          <Link
            to="/app/analyze"
            className="inline-flex items-center px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-sm font-medium rounded-lg shadow-sm transition-colors shrink-0"
          >
            <PlusCircle className="w-4 h-4 mr-2" />
            New Analysis
          </Link>
        </div>

        {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}

        {loading ? (
          <LoadingSpinner label="Loading analysis history..." />
        ) : history.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-4">
              <History className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-900 mb-1">No analysis history found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mb-6">
              You haven't evaluated any job descriptions yet. Perform your first analysis to see history here.
            </p>
            <Link
              to="/app/analyze"
              className="inline-flex items-center px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-medium rounded-lg transition-colors"
            >
              <PlusCircle className="w-3.5 h-3.5 mr-1.5" />
              Analyze Match Now
            </Link>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-700">
                <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase text-slate-500 tracking-wider">
                  <tr>
                    <th scope="col" className="px-6 py-3.5">Job Title</th>
                    <th scope="col" className="px-6 py-3.5">Match Score</th>
                    <th scope="col" className="px-6 py-3.5">Date</th>
                    <th scope="col" className="px-6 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {history.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {item.job_title || 'Untitled Job Position'}
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-50 text-teal-800 border border-teal-200">
                          {Math.round(item.overall_score)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500">
                        {new Date(item.created_at).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="px-6 py-4 text-right space-x-2">
                        <Link
                          to={`/app/results/${item.id}`}
                          className="inline-flex items-center text-xs font-medium text-teal-700 hover:text-teal-900 px-2.5 py-1.5 rounded hover:bg-teal-50 transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5 mr-1" /> View
                        </Link>

                        {confirmDeleteId === item.id ? (
                          <span className="inline-flex items-center space-x-1">
                            <span className="text-xs text-rose-600 font-medium">Delete?</span>
                            <button
                              onClick={() => handleDelete(item.id)}
                              disabled={deletingId === item.id}
                              className="text-xs text-rose-700 font-bold hover:underline"
                            >
                              Yes
                            </button>
                            <button
                              onClick={() => setConfirmDeleteId(null)}
                              className="text-xs text-slate-500 hover:underline ml-1"
                            >
                              No
                            </button>
                          </span>
                        ) : (
                          <button
                            onClick={() => setConfirmDeleteId(item.id)}
                            aria-label="Delete analysis"
                            className="inline-flex items-center text-xs font-medium text-rose-600 hover:text-rose-800 px-2 py-1.5 rounded hover:bg-rose-50 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
