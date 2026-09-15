import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export default function ScoreBreakdownChart({ breakdown, scoreBreakdown }) {
  const dataBreakdown = breakdown || scoreBreakdown;
  if (!dataBreakdown) return null;

  const data = [
    {
      name: 'Skill Coverage',
      score: Math.round(dataBreakdown.skill_score || 0),
      weight: '40%',
      color: '#0D9488', // Emerald
    },
    {
      name: 'Text Similarity',
      score: Math.round(dataBreakdown.text_similarity_score || 0),
      weight: '30%',
      color: '#0284C7', // Sky Blue
    },
    {
      name: 'Experience',
      score: Math.round(dataBreakdown.experience_score || 0),
      weight: '15%',
      color: '#6366F1', // Indigo
    },
    {
      name: 'ATS Quality',
      score: Math.round(dataBreakdown.ats_quality_score || 0),
      weight: '15%',
      color: '#8B5CF6', // Purple/Violet
    },
  ];

  return (
    <div className="w-full h-64 py-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <XAxis type="number" domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
          <YAxis dataKey="name" type="category" tickLine={false} axisLine={false} width={110} tick={{ fontSize: 12, fill: '#334155', fontWeight: 500 }} />
          <Tooltip
            formatter={(value, name, props) => [`${value}% (Weight: ${props.payload.weight})`, 'Score']}
            contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '12px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
          />
          <Bar dataKey="score" radius={[0, 6, 6, 0]} barSize={20}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
