import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { ProgressBar } from './ui/ProgressBar';

const labels = {
  digital_presence: 'Digital Presence',
  productivity: 'Productivity',
  customer_management: 'Customer Management',
  data_security: 'Data & Security',
  ai_readiness: 'AI Readiness',
};

export function MaturityChart({ scores = {}, compact = false }) {
  const data = Object.entries(labels).map(([key, subject]) => ({
    subject,
    score: Math.max(0, Math.min(5, Number(scores[key]) || 0)),
  }));

  return (
    <div className="min-w-0">
      <div className={compact ? 'h-52 min-h-52 w-full' : 'h-72 min-h-72 w-full'}>
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={200}>
          <RadarChart cx="50%" cy="50%" outerRadius="62%" data={data}>
            <PolarGrid stroke="#d1d5db" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#4B5563', fontSize: compact ? 8 : 10 }} />
            <PolarRadiusAxis domain={[0, 5]} tick={false} axisLine={false} />
            <Radar name="Maturity" dataKey="score" stroke="#005B9F" strokeWidth={2} fill="#005B9F" fillOpacity={0.25} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-5 gap-y-3 mt-4">
        {data.map((item) => (
          <div key={item.subject}>
            <div className="flex justify-between text-xs mb-1 text-gray-600"><span>{item.subject}</span><span>{item.score}/5</span></div>
            <ProgressBar value={item.score} max={5} />
          </div>
        ))}
      </div>
    </div>
  );
}
