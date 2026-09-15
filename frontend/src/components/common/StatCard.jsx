import React from 'react';

export default function StatCard({ title, value, subtitle, description, icon: Icon, trend }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className="p-2 bg-slate-50 rounded-lg text-slate-600 border border-slate-100">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold text-slate-900 tracking-tight">{value}</span>
        {trend && (
          <span className="text-xs font-medium text-teal-800 bg-teal-50 px-2 py-0.5 rounded-md border border-teal-200">
            {trend}
          </span>
        )}
      </div>
      {(subtitle || description) && (
        <p className="mt-1 text-xs text-slate-500">{subtitle || description}</p>
      )}
    </div>
  );
}

export { StatCard };
