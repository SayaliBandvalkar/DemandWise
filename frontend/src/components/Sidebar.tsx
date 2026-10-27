import React from 'react';
import {
  Activity,
  Layers,
  Database,
  TrendingUp,
  Scale,
  Target,
  Package,
  Award,
  ShieldAlert,
  FileCheck2,
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'data'
  | 'hierarchy'
  | 'forecast'
  | 'reconciliation'
  | 'uncertainty'
  | 'inventory'
  | 'evaluation'
  | 'monitoring'
  | 'audit';

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
}

const navItems: { id: NavTab; label: string; icon: React.ReactNode }[] = [
  { id: 'overview', label: '1. Executive Overview', icon: <Activity className="w-4 h-4" /> },
  { id: 'data', label: '2. Data Management', icon: <Database className="w-4 h-4" /> },
  { id: 'hierarchy', label: '3. Hierarchy Explorer', icon: <Layers className="w-4 h-4" /> },
  { id: 'forecast', label: '4. Forecast Studio', icon: <TrendingUp className="w-4 h-4" /> },
  { id: 'reconciliation', label: '5. Reconciliation Lab', icon: <Scale className="w-4 h-4" /> },
  { id: 'uncertainty', label: '6. Uncertainty & Calibration', icon: <Target className="w-4 h-4" /> },
  { id: 'inventory', label: '7. Inventory Simulator', icon: <Package className="w-4 h-4" /> },
  { id: 'evaluation', label: '8. Model Evaluation', icon: <Award className="w-4 h-4" /> },
  { id: 'monitoring', label: '9. Experiments & Drift', icon: <ShieldAlert className="w-4 h-4" /> },
  { id: 'audit', label: '10. Audit Trail', icon: <FileCheck2 className="w-4 h-4" /> },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  return (
    <aside className="w-64 bg-navy-900 border-r border-white/10 flex flex-col justify-between shrink-0 h-screen sticky top-0 overflow-y-auto">
      <div>
        {/* Brand logo header */}
        <div className="px-5 py-4 border-b border-white/10 flex items-center justify-start min-h-[72px]">
          <img
            src="/logo.png"
            alt="DemandWise Logo"
            className="w-[165px] h-[42px] max-w-full select-none"
            style={{ objectFit: 'contain', objectPosition: 'left center' }}
          />
        </div>

        {/* Navigation list */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan/20 to-navy-600/60 text-cyan border border-cyan/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-navy-700/40'
                }`}
              >
                <div className={isActive ? 'text-cyan' : 'text-slate-400'}>{item.icon}</div>
                <span className="truncate">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* System status pill */}
      <div className="p-4 border-t border-white/10">
        <div className="p-3 rounded-xl bg-navy-800/80 border border-white/5 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300 font-medium">FastAPI Backend</span>
          </div>
          <span className="text-emerald-400 font-mono text-[10px]">v1.0.0</span>
        </div>
      </div>
    </aside>
  );
};
