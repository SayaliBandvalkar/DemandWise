import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { DriftResponse } from '../types';
import { Activity, AlertTriangle, CheckCircle, Flame, Layers, RefreshCw, ShieldAlert, Zap } from 'lucide-react';

export const ExperimentsMonitoring: React.FC = () => {
  const [seriesName, setSeriesName] = useState('Total');
  const [driftData, setDriftData] = useState<DriftResponse | null>(null);
  const [benchmarks, setBenchmarks] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDrift = async (series: string) => {
    setLoading(true);
    setError(null);
    try {
      const [driftRes, benchRes] = await Promise.all([
        api.getDrift(series),
        benchmarks ? Promise.resolve(benchmarks) : api.getBenchmarks(),
      ]);
      setDriftData(driftRes);
      if (!benchmarks) setBenchmarks(benchRes);
    } catch (e: any) {
      setError(e.message || 'Drift check failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrift(seriesName);
  }, [seriesName]);

  const ablationData = benchmarks?.ablation_stress_test || [];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Activity className="w-5 h-5 text-cyan" />
            <span>Experiments, Concept Drift & Model Monitoring</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time tracking signal surveillance, distribution shift detection via Population Stability Index (PSI), and stress-test ablation experiments.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={seriesName}
            onChange={(e) => setSeriesName(e.target.value)}
            className="bg-navy-800 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan"
          >
            <option value="Total">Total (Top Level)</option>
            <option value="Region_A">Region_A</option>
            <option value="Region_B">Region_B</option>
            <option value="Store_01">Store_01</option>
            <option value="Store_02">Store_02</option>
            <option value="Store_03">Store_03</option>
            <option value="Store_04">Store_04</option>
          </select>

          <button
            onClick={() => fetchDrift(seriesName)}
            disabled={loading}
            className="px-3 py-2 rounded-xl bg-navy-800 border border-white/10 text-cyan text-xs font-bold flex items-center space-x-1.5 hover:bg-navy-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Check</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Drift & Surveillance Cards */}
      {driftData && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* PSI Card */}
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-widest text-slate-400">
                Population Stability Index (PSI)
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  driftData.psi_alert_level === 'STABLE'
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : driftData.psi_alert_level === 'MODERATE'
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}
              >
                {driftData.psi_alert_level}
              </span>
            </div>

            <div className="flex items-baseline space-x-3">
              <span className="text-4xl font-extrabold text-white font-mono">{driftData.psi_value.toFixed(4)}</span>
              <span className="text-xs text-slate-400">Baseline vs Target Window</span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-navy-800/80 p-3 rounded-xl border border-white/5">
              {driftData.summary}
            </p>

            <div className="pt-2 border-t border-white/10 flex justify-between text-[11px] text-slate-400">
              <span>Thresholds:</span>
              <span className="text-emerald-400">&lt; 0.10 Stable</span>
              <span className="text-amber-400">0.10 - 0.25 Moderate</span>
              <span className="text-rose-400">&gt; 0.25 Severe</span>
            </div>
          </div>

          {/* Tracking Signal Card */}
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-widest text-slate-400">
                Max Tracking Signal (TS)
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  !driftData.tracking_signal_alert
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}
              >
                {!driftData.tracking_signal_alert ? 'In Control' : 'Bias Alert'}
              </span>
            </div>

            <div className="flex items-baseline space-x-3">
              <span className="text-4xl font-extrabold text-white font-mono">{driftData.max_tracking_signal.toFixed(2)}</span>
              <span className="text-xs text-slate-400">Threshold: ±4.0 MADs</span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-navy-800/80 p-3 rounded-xl border border-white/5">
              {!driftData.tracking_signal_alert
                ? 'Cumulative forecast errors remain balanced around zero. No persistent over- or under-forecasting bias detected.'
                : 'Cumulative forecast errors have exceeded 4 standard mean absolute deviations, indicating systematic model bias.'}
            </p>

            <div className="pt-2 border-t border-white/10 flex justify-between text-[11px] text-slate-400">
              <span>Formula: TS = Σ(y_t - ŷ_t) / MAD_t</span>
              <span className="text-cyan font-mono">Control Limits: [-4.0, +4.0]</span>
            </div>
          </div>
        </div>
      )}

      {/* Ablation Stress-Testing Section */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Flame className="w-4 h-4 text-amber-400" />
            <span>Ablation Stress-Testing (Intermittent & Shock Regimes)</span>
          </h3>
          <span className="text-xs text-slate-400">Controlled perturbation stress tests under synthetic demand spikes</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-800 text-slate-300 border-b border-white/10">
              <tr>
                <th className="p-3">Replenishment Policy</th>
                <th className="p-3">Total Demand</th>
                <th className="p-3">Fulfilled Units</th>
                <th className="p-3">Lost Sales</th>
                <th className="p-3">Fill Rate (%)</th>
                <th className="p-3">Stockout Days</th>
                <th className="p-3">Orders Placed</th>
                <th className="p-3">Total Incurred Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {ablationData.map((row: any, idx: number) => {
                const isUncertainty = row.Policy === 'uncertainty_aware';
                return (
                  <tr key={idx} className={`hover:bg-navy-700/40 ${isUncertainty ? 'bg-cyan/5 font-semibold' : ''}`}>
                    <td className="p-3 text-white flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-cyan"></span>
                      <span>{row.Policy}</span>
                    </td>
                    <td className="p-3 text-slate-300">{row['Total Demand']}</td>
                    <td className="p-3 text-slate-200">{row['Fulfilled Units']}</td>
                    <td className={`p-3 ${row['Lost Sales'] > 0 ? 'text-rose-400 font-bold' : 'text-emerald-400'}`}>
                      {row['Lost Sales']}
                    </td>
                    <td className="p-3 font-bold text-cyan">{row['Fill Rate (%)']}%</td>
                    <td className="p-3 text-slate-300">{row['Stockout Days']}</td>
                    <td className="p-3 text-slate-300">{row['Orders Placed']}</td>
                    <td className="p-3 text-amber-300 font-bold">${row['Total Cost ($)']}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
