import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { ReconciliationResponse } from '../types';
import { Scale, Play, CheckCircle2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const ReconciliationLab: React.FC = () => {
  const [data, setData] = useState<ReconciliationResponse | null>(null);
  const [baseModel, setBaseModel] = useState('lightgbm');
  const [horizon, setHorizon] = useState(14);
  const [loading, setLoading] = useState(false);

  const handleRunReconciliation = async () => {
    setLoading(true);
    try {
      const res = await api.runReconciliation(baseModel, horizon);
      setData(res);
    } catch (e: any) {
      alert(`Reconciliation error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleRunReconciliation();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Control Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Scale className="w-5 h-5 text-cyan" />
            <span>Reconciliation Lab</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Reconcile uncoordinated base forecasts via $\tilde&#123;y&#125;_t = S \cdot P \cdot \hat&#123;y&#125;_t$ to guarantee 100% hierarchical summation coherence.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={baseModel}
            onChange={(e) => setBaseModel(e.target.value)}
            className="bg-navy-800 border border-white/10 rounded-lg p-2.5 text-xs text-white"
          >
            <option value="lightgbm">LightGBM Regressor</option>
            <option value="exponential_smoothing">Exponential Smoothing</option>
            <option value="seasonal_naive">Seasonal Naive</option>
            <option value="naive">Naive</option>
          </select>
          <button
            onClick={handleRunReconciliation}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-cyan text-navy-950 font-bold text-xs flex items-center space-x-2 hover:bg-cyan/90 transition disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Reconciling...' : 'Run Reconciliation'}</span>
          </button>
        </div>
      </div>

      {/* Comparative Matrix Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="text-sm font-bold text-white border-b border-white/10 pb-3 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Coherence & Accuracy Evaluation Across Methods</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-800 text-slate-300 border-b border-white/10">
              <tr>
                <th className="p-3">Method</th>
                <th className="p-3">Coherent?</th>
                <th className="p-3">Max Coherence Error</th>
                <th className="p-3">Total Series MAE</th>
                <th className="p-3">Avg Bottom MAE</th>
                <th className="p-3">Total WAPE (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {data?.methods.map((row) => (
                <tr key={row.method} className="hover:bg-navy-700/40">
                  <td className="p-3 font-semibold text-white capitalize">{row.method.replace('_', ' ')}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        row.is_coherent ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
                      }`}
                    >
                      {row.is_coherent ? 'YES' : 'NO'}
                    </span>
                  </td>
                  <td className={`p-3 ${row.max_coherence_error > 0.001 ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}`}>
                    {row.max_coherence_error.toFixed(4)}
                  </td>
                  <td className="p-3 text-slate-200">{row.total_series_mae.toFixed(2)}</td>
                  <td className="p-3 text-slate-200">{row.avg_bottom_mae.toFixed(2)}</td>
                  <td className="p-3 text-cyan font-bold">{row.total_wape_pct.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Comparison Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">
            Max Coherence Discrepancy by Method (Lower is Better)
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.methods || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#17375E" opacity={0.5} />
                <XAxis dataKey="method" stroke="#64748B" fontSize={11} tickFormatter={(m) => m.replace('_', ' ')} />
                <YAxis stroke="#64748B" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F2744',
                    borderColor: 'rgba(0, 229, 255, 0.4)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="max_coherence_error" fill="#00E5FF" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">
            Total Enterprise MAE (Top-Level Accuracy)
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.methods || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#17375E" opacity={0.5} />
                <XAxis dataKey="method" stroke="#64748B" fontSize={11} tickFormatter={(m) => m.replace('_', ' ')} />
                <YAxis stroke="#64748B" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F2744',
                    borderColor: 'rgba(0, 229, 255, 0.4)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="total_series_mae" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
