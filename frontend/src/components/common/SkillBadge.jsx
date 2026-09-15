import React from 'react';
import { Check, X, AlertCircle } from 'lucide-react';

export default function SkillBadge({ name, skill, type = 'matched', subtext }) {
  const skillName = name || skill;
  let styleClasses = 'bg-emerald-50 text-emerald-800 border-emerald-200';
  let Icon = Check;

  if (type === 'missing_required') {
    styleClasses = 'bg-rose-50 text-rose-800 border-rose-200';
    Icon = X;
  } else if (type === 'missing_preferred') {
    styleClasses = 'bg-amber-50 text-amber-800 border-amber-200';
    Icon = AlertCircle;
  }

  return (
    <span className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium border shadow-2xs ${styleClasses}`}>
      <Icon className="w-3.5 h-3.5 mr-1.5 shrink-0 opacity-80" />
      <span>{skillName}</span>
      {subtext && (
        <span className="ml-1.5 opacity-70 text-[10px]">({subtext})</span>
      )}
    </span>
  );
}

export { SkillBadge };
