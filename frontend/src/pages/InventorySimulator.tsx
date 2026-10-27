import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { InventorySimResponse, PolicySummary } from '../types';
import { Package, Play, ShieldAlert, DollarSign, TrendingDown, RefreshCw, BarChart2 } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area,
} from 'recharts';

export const InventorySimulator: React.FC = () => {
  const [skuId, setSkuId] = useState('SKU_001');
  const [storeId, setStoreId] = useState('Store_01');
  const [leadTime, setLeadTime] = useState(5);
  const [reviewPeriod, setReviewPeriod] = useState(7);
  const [serviceLevel, setServiceLevel] = useState(0.95);
  const [holdingCost, setHoldingCost] = useState(0.03);
  const [stockoutPenalty, setStockoutPenalty] = useState(12.5);
  const [orderingCost, setOrderingCost] = useState(15.0);

  const [data, setData] = useState<InventorySimResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.simulateInventory({
        sku_id: skuId,
        store_id: storeId,
        lead_time_days: leadTime,
        review_period_days: reviewPeriod,
        target_service_level: serviceLevel,
        holding_cost_daily: holdingCost,
        stockout_penalty: stockoutPenalty,
        ordering_cost: orderingCost,
      });
      setData(res);
    } catch (e: any) {
      setError(e.message || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSimulate();
  }, []);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Package className="w-5 h-5 text-cyan" />
            <span>Downstream Inventory Decision Simulation</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Evaluate (s, S) replenishment policies across Baseline, Forecast-Driven, and Uncertainty-Aware safety stock models.
          </p>
        </div>

        <button
          onClick={handleSimulate}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-cyan text-navy-950 font-bold text-xs flex items-center space-x-2 hover:bg-cyan/90 transition disabled:opacity-50 shadow-lg shadow-cyan/20"
        >
          <Play className={`w-3.5 h-3.5 fill-current ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Simulating Policy Runs...' : 'Run Simulation'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Control Parameters Grid */}
      <div className="glass-panel p-6 rounded-2xl space-y-6">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider text-slate-300 border-b border-white/10 pb-3 flex items-center space-x-2">
          <RefreshCw className="w-4 h-4 text-cyan" />
          <span>Simulation Parameters & Operational Costs</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Target SKU</label>
            <select
              value={skuId}
              onChange={(e) => setSkuId(e.target.value)}
              className="w-full bg-navy-800 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan"
            >
              {Array.from({ length: 12 }, (_, i) => {
                const id = `SKU_${String(i + 1).padStart(3, '0')}`;
                return <option key={id} value={id}>{id}</option>;
              })}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">Store Location</label>
            <select
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
              className="w-full bg-navy-800 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan"
            >
              {['Store_01', 'Store_02', 'Store_03', 'Store_04'].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-2">
              <span>Lead Time (Days)</span>
              <span className="text-cyan font-mono">{leadTime}d</span>
            </div>
            <input
              type="range"
              min="1"
              max="21"
              value={leadTime}
              onChange={(e) => setLeadTime(Number(e.target.value))}
              className="w-full accent-cyan bg-navy-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-2">
              <span>Review Period (Days)</span>
              <span className="text-cyan font-mono">{reviewPeriod}d</span>
            </div>
            <input
              type="range"
              min="1"
              max="14"
              value={reviewPeriod}
              onChange={(e) => setReviewPeriod(Number(e.target.value))}
              className="w-full accent-cyan bg-navy-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-2">
              <span>Target Service Level</span>
              <span className="text-cyan font-mono">{(serviceLevel * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.80"
              max="0.99"
              step="0.01"
              value={serviceLevel}
              onChange={(e) => setServiceLevel(Number(e.target.value))}
              className="w-full accent-cyan bg-navy-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-2">
              <span>Holding Cost ($/unit/day)</span>
              <span className="text-cyan font-mono">${holdingCost.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="0.20"
              step="0.01"
              value={holdingCost}
              onChange={(e) => setHoldingCost(Number(e.target.value))}
              className="w-full accent-cyan bg-navy-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-2">
              <span>Stockout Penalty ($/unit)</span>
              <span className="text-rose-400 font-mono">${stockoutPenalty.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="2.0"
              max="50.0"
              step="1.0"
              value={stockoutPenalty}
              onChange={(e) => setStockoutPenalty(Number(e.target.value))}
              className="w-full accent-cyan bg-navy-800"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-300 mb-2">
              <span>Fixed Order Cost ($/order)</span>
              <span className="text-cyan font-mono">${orderingCost.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="5.0"
              max="50.0"
              step="2.5"
              value={orderingCost}
              onChange={(e) => setOrderingCost(Number(e.target.value))}
              className="w-full accent-cyan bg-navy-800"
            />
          </div>
        </div>
      </div>

      {/* Policy Comparison Cards */}
      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {data.policies_summary.map((p, idx) => {
              const isUncertainty = p.policy === 'uncertainty_aware';
              const isForecast = p.policy === 'forecast_driven';
              return (
                <div
                  key={idx}
                  className={`p-6 rounded-2xl border transition-all ${
                    isUncertainty
                      ? 'bg-gradient-to-b from-cyan/10 to-navy-900 border-cyan/40 shadow-lg shadow-cyan/10'
                      : 'glass-panel'
                  }`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs uppercase font-mono tracking-widest text-slate-400">
                      {isUncertainty ? '🛡️ Uncertainty-Aware' : isForecast ? '📈 Forecast-Driven' : '⚙️ Static Baseline'}
                    </span>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                      p.fill_rate_pct >= serviceLevel * 98 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    }`}>
                      {p.fill_rate_pct.toFixed(1)}% Fill Rate
                    </span>
                  </div>

                  <div className="text-2xl font-bold text-white mb-4">
                    ${p.total_cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    <span className="text-xs font-normal text-slate-400 block mt-0.5">Total Incurred Cost</span>
                  </div>

                  <div className="space-y-2.5 text-xs border-t border-white/10 pt-4 text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Fulfilled Demand:</span>
                      <span className="font-mono text-white">{p.fulfilled_units.toFixed(0)} / {p.total_demand.toFixed(0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Lost Sales (Stockouts):</span>
                      <span className={`font-mono ${p.lost_sales > 0 ? 'text-rose-400 font-bold' : 'text-emerald-400'}`}>
                        {p.lost_sales.toFixed(1)} units ({p.stockout_days} days)
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Orders Placed:</span>
                      <span className="font-mono text-white">{p.orders_placed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Holding Costs:</span>
                      <span className="font-mono text-cyan">${p.holding_cost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Stockout Costs:</span>
                      <span className="font-mono text-rose-400">${p.stockout_cost.toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Daily Trajectory Recharts Chart */}
          <div className="glass-panel p-6 rounded-2xl space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <BarChart2 className="w-4 h-4 text-cyan" />
              <span>Simulated Daily On-Hand Stock & Pipeline Trajectory</span>
            </h3>
            <p className="text-xs text-slate-400">
              Daily discrete-event inventory trace showing actual demand consumption, arrivals of lead-time orders, and safety stock buffers.
            </p>

            <div className="h-80 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.daily_trajectory}>
                  <defs>
                    <linearGradient id="stockGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderColor: 'rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="ending_stock"
                    name="On-Hand Ending Stock"
                    stroke="#06b6d4"
                    fillOpacity={1}
                    fill="url(#stockGrad)"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="actual_demand"
                    name="Actual Daily Demand"
                    stroke="#f59e0b"
                    strokeWidth={1.5}
                    dot={false}
                  />
                  <Line
                    type="stepAfter"
                    dataKey="lost_sales"
                    name="Lost Sales"
                    stroke="#f43f5e"
                    strokeWidth={2}
                  />
                  <Line
                    type="stepAfter"
                    dataKey="orders_arrived"
                    name="Orders Arrived"
                    stroke="#10b981"
                    strokeWidth={1.5}
                    strokeDasharray="4 4"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
