import React from 'react';

interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string;
  deltaType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  label,
  value,
  delta,
  deltaType = 'neutral',
  icon,
}) => {
  const deltaColor =
    deltaType === 'positive'
      ? 'text-emerald-400'
      : deltaType === 'negative'
      ? 'text-rose-400'
      : 'text-cyan';

  return (
    <div className="glass-panel p-5 rounded-xl flex flex-col justify-between transition-all duration-200 hover:-translate-y-0.5">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
          {label}
        </span>
        {icon && <div className="text-cyan p-2 bg-navy-700/60 rounded-lg">{icon}</div>}
      </div>
      <div className="mt-2">
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        {delta && <div className={`text-xs mt-1 font-medium ${deltaColor}`}>{delta}</div>}
      </div>
    </div>
  );
};
