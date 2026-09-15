import React from 'react';

export default function LoadingSpinner({ size = 'md', label = 'Loading...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-3" role="status">
      <div
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full border-teal-600 border-t-transparent animate-spin`}
      />
      {label && <span className="text-sm font-medium text-slate-600">{label}</span>}
      <span className="sr-only">{label}</span>
    </div>
  );
}
