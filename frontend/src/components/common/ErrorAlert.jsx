import React from 'react';
import { AlertCircle, XCircle } from 'lucide-react';

export default function ErrorAlert({ message, title = 'Error', onDismiss }) {
  if (!message) return null;

  return (
    <div className="rounded-lg bg-rose-50 border border-rose-200 p-4 text-rose-800 flex items-start justify-between">
      <div className="flex items-start space-x-3">
        <AlertCircle className="w-5 h-5 text-rose-600 mt-0.5 shrink-0" />
        <div>
          <h4 className="text-sm font-semibold text-rose-900">{title}</h4>
          <p className="text-sm text-rose-700 mt-0.5">{message}</p>
        </div>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-rose-500 hover:text-rose-700 p-1 rounded-md transition-colors"
          aria-label="Dismiss error"
        >
          <XCircle className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
