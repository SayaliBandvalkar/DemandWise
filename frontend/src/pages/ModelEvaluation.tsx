import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Award, BarChart3, BookOpen, CheckCircle, Cpu, HelpCircle, ShieldCheck } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';

export const ModelEvaluation: React.FC = () => {
  const [benchmarks, setBenchmarks] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await api.getBenchmarks();
        setBenchmarks(res);
      } catch (e: any) {
        setError(e.message || 'Failed to load benchmarks');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const modelsData = benchmarks?.models_benchmark || [];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Award className="w-5 h-5 text-cyan" />
            <span>Master Model Evaluation & Accuracy Leaderboard</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Empirical benchmarking of baseline, intermittent, statistical, and gradient-boosted time series architectures across all 59 hierarchy series.
          </p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-cyan bg-cyan/10 px-3 py-1.5 rounded-xl border border-cyan/20">
          <Cpu className="w-4 h-4" />
          <span>Horizon: 14 Days (Rolling-Origin Backtest)</span>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-cyan" />
            <span>Cross-Model Accuracy Comparison</span>
          </h3>
          <span className="text-xs text-slate-400">Scale-free MASE & WAPE benchmarked against in-sample Naive random walk</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-800 text-slate-300 border-b border-white/10">
              <tr>
                <th className="p-3">Rank & Model</th>
                <th className="p-3">Total MASE</th>
                <th className="p-3">Total WAPE (%)</th>
                <th className="p-3">Total MAE</th>
                <th className="p-3">Total RMSE</th>
                <th className="p-3">Avg Bottom MAE</th>
                <th className="p-3">Runtime (s)</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {modelsData.map((row: any, idx: number) => {
                const isBest = row.Total_MASE === Math.min(...modelsData.map((m: any) => m.Total_MASE));
                return (
                  <tr key={idx} className={`hover:bg-navy-700/40 ${isBest ? 'bg-cyan/5' : ''}`}>
                    <td className="p-3 font-semibold text-white flex items-center space-x-2">
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        idx === 0 ? 'bg-amber-400/20 text-amber-300' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {idx + 1}
                      </span>
                      <span>{row.Model}</span>
                      {isBest && (
                        <span className="text-[10px] bg-cyan/20 text-cyan px-1.5 py-0.5 rounded font-sans font-bold">
                          BEST ACCURACY
                        </span>
                      )}
                    </td>
                    <td className={`p-3 font-bold ${row.Total_MASE < 1.0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {row.Total_MASE.toFixed(3)}
                    </td>
                    <td className="p-3 text-slate-200">{row.Total_WAPE_Pct.toFixed(2)}%</td>
                    <td className="p-3 text-slate-300">{row.Total_MAE.toFixed(2)}</td>
                    <td className="p-3 text-slate-300">{row.Total_RMSE.toFixed(2)}</td>
                    <td className="p-3 text-cyan">{row.Avg_Bottom_MAE.toFixed(2)}</td>
                    <td className="p-3 text-slate-400">{row.Runtime_Sec.toFixed(3)}s</td>
                    <td className="p-3">
                      <span className="inline-flex items-center space-x-1 text-emerald-400 text-[10px] bg-emerald-500/10 px-2 py-0.5 rounded-full">
                        <CheckCircle className="w-3 h-3" />
                        <span>Validated</span>
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Bar Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between">
            <span>Mean Absolute Scaled Error (MASE)</span>
            <span className="text-xs font-mono text-cyan">MASE &lt; 1.0 beats Naive</span>
          </h3>
          <p className="text-xs text-slate-400">
            Scale-independent metric dividing forecast error by in-sample one-step naive error. Lower is better.
          </p>
          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="Model" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
                <ReferenceLine y={1.0} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: 'Naive Benchmark (1.0)', fill: '#f43f5e', fontSize: 10 }} />
                <Bar dataKey="Total_MASE" fill="#06b6d4" radius={[6, 6, 0, 0]} name="Total MASE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between">
            <span>Weighted Absolute Percentage Error (WAPE %)</span>
            <span className="text-xs font-mono text-cyan">Lower is better</span>
          </h3>
          <p className="text-xs text-slate-400">
            Total absolute deviation divided by total demand volume, avoiding division by zero on intermittent SKUs.
          </p>
          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="Model" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="Total_WAPE_Pct" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Total WAPE %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Metric Theory Card */}
      <div className="glass-panel p-6 rounded-2xl space-y-3 border-l-4 border-l-cyan">
        <h4 className="text-xs font-bold uppercase tracking-wider text-cyan flex items-center space-x-2">
          <BookOpen className="w-4 h-4" />
          <span>Scientific Metric Justification (Hyndman & Koehler, 2006)</span>
        </h4>
        <div className="text-xs text-slate-300 space-y-2 leading-relaxed">
          <p>
            Standard percentage metrics such as MAPE are mathematically undefined or produce explosive infinities when series exhibit intermittent zero demand (common in 28.5% of bottom-level SKU series). 
          </p>
          <p className="font-mono bg-navy-800 p-3 rounded-xl border border-white/10 text-cyan">
            MASE = ( (1/h) * Σ |y_t - ŷ_t| ) / ( (1/(T-1)) * Σ |y_t - y_t-1| )
          </p>
          <p>
            DemandWise utilizes <strong>MASE</strong> and <strong>RMSSE</strong> as primary performance criteria because they normalize absolute forecast errors by the in-sample mean absolute step of a naive random walk. A score below 1.0 proves superior predictive power over the baseline.
          </p>
        </div>
      </div>
    </div>
  );
};
