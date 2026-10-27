import React from 'react';
import { Database, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  activeDataset?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  activeDataset = 'retail_hierarchy.csv',
}) => {
  return (
    <header className="bg-navy-900/80 backdrop-blur-md border-b border-white/10 px-8 py-4 flex items-center justify-between sticky top-0 z-30">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-3">
          <span>{title}</span>
        </h1>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center space-x-3 text-xs">
        {/* Active dataset indicator */}
        <div className="px-3 py-1.5 rounded-lg bg-navy-800 border border-white/10 flex items-center space-x-2 text-slate-300">
          <Database className="w-3.5 h-3.5 text-cyan" />
          <span className="font-mono text-[11px] text-slate-200">{activeDataset}</span>
        </div>

        {/* Verification badge */}
        <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-1.5 text-emerald-400 font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Coherence Validated</span>
        </div>
      </div>
    </header>
  );
};
