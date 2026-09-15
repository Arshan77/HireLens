import React from 'react';

export default function ScoreGauge({ score, label = 'Overall Match Score', size = 'md' }) {
  const roundedScore = Math.round(score || 0);

  // Color selection based on score threshold
  let strokeColor = '#0D9488'; // Emerald/Teal (Strong >= 75)
  let badgeBg = 'bg-teal-50 text-teal-800 border-teal-200';
  let ratingText = 'Strong Match';

  if (roundedScore < 50) {
    strokeColor = '#F43F5E'; // Coral/Rose (< 50)
    badgeBg = 'bg-rose-50 text-rose-800 border-rose-200';
    ratingText = 'Needs Improvement';
  } else if (roundedScore < 75) {
    strokeColor = '#F59E0B'; // Amber (50-74)
    badgeBg = 'bg-amber-50 text-amber-800 border-amber-200';
    ratingText = 'Moderate Match';
  }

  const radius = size === 'lg' ? 68 : 52;
  const strokeWidth = size === 'lg' ? 10 : 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - ((score || 0) / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center text-center p-4">
      <div className="relative inline-flex items-center justify-center">
        <svg
          className={`transform -rotate-90 ${size === 'lg' ? 'w-44 h-44' : 'w-36 h-36'}`}
        >
          {/* Background Track */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            className="stroke-slate-100"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Value Arc */}
          <circle
            cx="50%"
            cy="50%"
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className={`font-extrabold tracking-tight text-slate-900 ${size === 'lg' ? 'text-4xl' : 'text-3xl'}`}>
            {roundedScore}%
          </span>
          <span className="text-xs text-slate-500 font-medium mt-0.5">Match</span>
        </div>
      </div>

      <div className={`mt-3 inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeBg}`}>
        {ratingText}
      </div>

      {label && <p className="text-xs text-slate-500 font-medium mt-2">{label}</p>}
    </div>
  );
}

export { ScoreGauge };
