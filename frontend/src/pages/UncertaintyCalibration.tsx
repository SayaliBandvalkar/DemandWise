import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { CalibrationResponse } from '../types';
import { Target, Play, ShieldCheck } from 'lucide-react';
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

export const UncertaintyCalibration: React.FC = () => {
  const [data, setData] = useState<CalibrationResponse | null>(null);
  const [seriesName, setSeriesName] = useState('Total');
  const [horizon, setHorizon] = useState(14);
  const [loading, setLoading] = useState(false);

  const handleEvaluate = async () => {
    setLoading(true);
    try {
      const res = await api.evaluateCalibration(seriesName, horizon);
      setData(res);
    } catch (e: any) {
      alert(`Calibration evaluation failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleEvaluate();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Target className="w-5 h-5 text-cyan" />
            <span>Uncertainty Quantification & Conformal Calibration</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Compare distribution-free Split Conformal Prediction against standard Residual Bootstrap intervals at 80% and 95% nominal levels.
          </p>
        </div>

        <button
          onClick={handleEvaluate}
          disabled={loading}
          className="px-4 py-2.5 rounded-xl bg-cyan text-navy-950 font-bold text-xs flex items-center space-x-2 hover:bg-cyan/90 transition disabled:opacity-50"
        >
          <Play className={`w-3.5 h-3.5 fill-current ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Evaluating...' : 'Evaluate Calibration'}</span>
        </button>
      </div>

      {/* Calibration Comparison Table */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <h3 className="text-sm font-bold text-white border-b border-white/10 pb-3 flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Empirical Calibration Performance ({seriesName})</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-800 text-slate-300 border-b border-white/10">
              <tr>
                <th className="p-3">Interval Method</th>
                <th className="p-3">Nominal Level</th>
                <th className="p-3">Empirical Coverage</th>
                <th className="p-3">Coverage Error (Δ)</th>
                <th className="p-3">Mean Width</th>
                <th className="p-3">Winkler Score (Lower is Better)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {data?.summary_metrics.map((row, idx) => (
                <tr key={idx} className="hover:bg-navy-700/40">
                  <td className="p-3 font-semibold text-white">{row.method}</td>
                  <td className="p-3 text-cyan">{(row.nominal_level * 100).toFixed(0)}%</td>
                  <td className={`p-3 font-bold ${row.empirical_coverage >= row.nominal_level * 95 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {row.empirical_coverage.toFixed(1)}%
                  </td>
                  <td className="p-3 text-slate-300">{row.coverage_error > 0 ? `+${row.coverage_error}%` : `${row.coverage_error}%`}</td>
                  <td className="p-3 text-slate-200">{row.mean_width.toFixed(2)}</td>
                  <td className="p-3 text-cyan font-bold">{row.winkler_score.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Chart Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">
            Empirical Coverage Rate vs. Nominal Confidence
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.summary_metrics || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#17375E" opacity={0.5} />
                <XAxis dataKey="method" stroke="#64748B" fontSize={10} tickFormatter={(m) => m.split(' ')[0]} />
                <YAxis stroke="#64748B" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F2744',
                    borderColor: 'rgba(0, 229, 255, 0.4)',
                    borderRadius: '8px',
                    color: '#F8FAFC',
                    fontSize: '12px',
                  }}
                />
                <ReferenceLine y={95} stroke="#10B981" strokeDasharray="3 3" label="Nominal 95%" />
                <Bar dataKey="empirical_coverage" fill="#00E5FF" radius={[4, 4, 0, 0]} name="Empirical Coverage (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">
            Winkler Interval Score (Lower is Better)
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.summary_metrics || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#17375E" opacity={0.5} />
                <XAxis dataKey="method" stroke="#64748B" fontSize={10} tickFormatter={(m) => m.split(' ')[0]} />
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
                <Bar dataKey="winkler_score" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Winkler Penalty Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
