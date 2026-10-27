import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { ForecastResponse } from '../types';
import { TrendingUp, Play, CheckCircle2 } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export const ForecastStudio: React.FC = () => {
  const [allSeries, setAllSeries] = useState<string[]>(['Total']);
  const [selectedSeries, setSelectedSeries] = useState('Total');
  const [models, setModels] = useState<string[]>(['LightGBM', 'ExponentialSmoothing', 'Croston_SBA', 'SeasonalNaive', 'Naive']);
  const [selectedModel, setSelectedModel] = useState('LightGBM');
  const [horizon, setHorizon] = useState(14);
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getHierarchySummary().then((h) => {
      setAllSeries(h.all_series);
    });
    api.getModels().then((m) => {
      setModels(m);
    });
    // Trigger initial forecast
    handleRunForecast('Total', 'LightGBM', 14);
  }, []);

  const handleRunForecast = async (series: string, model: string, h: number) => {
    setLoading(true);
    try {
      const res = await api.generateForecast(series, model, h);
      setForecastData(res);
    } catch (err: any) {
      alert(`Forecast generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Merge historical tail and predictions for seamless charting
  const chartData: any[] = [];
  if (forecastData) {
    forecastData.historical_tail.forEach((h) => {
      chartData.push({
        date: h.date,
        history: h.demand,
      });
    });
    forecastData.predictions.forEach((p) => {
      chartData.push({
        date: p.date,
        actual: p.actual,
        forecast: p.forecast,
      });
    });
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Control Panel */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-cyan" />
              <span>Forecast Studio</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select any hierarchical node and evaluate multi-horizon point predictions with zero future data leakage.
            </p>
          </div>

          <button
            onClick={() => handleRunForecast(selectedSeries, selectedModel, horizon)}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan to-cyan-accent text-navy-950 font-bold text-xs flex items-center space-x-2 shadow-lg hover:brightness-110 transition disabled:opacity-50"
          >
            <Play className={`w-4 h-4 fill-current ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Forecasting...' : 'Run Forecast Model'}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-3 border-t border-white/10">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Hierarchical Series:</label>
            <select
              value={selectedSeries}
              onChange={(e) => setSelectedSeries(e.target.value)}
              className="w-full bg-navy-800 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-cyan"
            >
              {allSeries.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">Forecasting Model:</label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full bg-navy-800 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-cyan"
            >
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1.5">
              <span>Forecast Horizon:</span>
              <span className="text-cyan font-mono">{horizon} days</span>
            </div>
            <input
              type="range"
              min={7}
              max={28}
              step={7}
              value={horizon}
              onChange={(e) => setHorizon(Number(e.target.value))}
              className="w-full accent-cyan"
            />
          </div>
        </div>
      </div>

      {/* Accuracy Badges */}
      {forecastData && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="glass-panel p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 font-semibold block">MAE</span>
            <span className="text-xl font-bold text-white mt-1 block">{forecastData.metrics.mae}</span>
          </div>
          <div className="glass-panel p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 font-semibold block">RMSE</span>
            <span className="text-xl font-bold text-white mt-1 block">{forecastData.metrics.rmse}</span>
          </div>
          <div className="glass-panel p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 font-semibold block">MASE</span>
            <span className="text-xl font-bold text-cyan mt-1 block">{forecastData.metrics.mase}</span>
          </div>
          <div className="glass-panel p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 font-semibold block">Normalized Bias</span>
            <span className="text-xl font-bold text-white mt-1 block">{forecastData.metrics.norm_bias_pct}%</span>
          </div>
          <div className="glass-panel p-4 rounded-xl text-center">
            <span className="text-[11px] text-slate-400 font-semibold block">WAPE</span>
            <span className="text-xl font-bold text-emerald-400 mt-1 block">{forecastData.metrics.wape_pct}%</span>
          </div>
        </div>
      )}

      {/* Main Forecast Chart */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>{selectedModel} Predictions vs. Ground-Truth Actuals ({selectedSeries})</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Historical train series (last 45 days) followed by 14-day held-out test predictions.
            </p>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#17375E" opacity={0.5} />
              <XAxis dataKey="date" stroke="#64748B" fontSize={10} tickFormatter={(d) => d.slice(5)} />
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
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Line type="monotone" dataKey="history" stroke="#94A3B8" strokeWidth={1.5} dot={false} name="History" />
              <Line type="monotone" dataKey="actual" stroke="#10B981" strokeWidth={2.5} name="Test Actuals" />
              <Line type="monotone" dataKey="forecast" stroke="#00E5FF" strokeWidth={2.5} strokeDasharray="4 4" name="Point Forecast" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
