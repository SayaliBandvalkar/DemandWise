import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { HierarchySummary, SummingMatrixData } from '../types';
import { Layers, Network, Table } from 'lucide-react';

export const HierarchyExplorer: React.FC = () => {
  const [hierarchy, setHierarchy] = useState<HierarchySummary | null>(null);
  const [matrixData, setMatrixData] = useState<SummingMatrixData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getHierarchySummary(), api.getSummingMatrix()])
      .then(([h, sm]) => {
        setHierarchy(h);
        setMatrixData(sm);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 min-h-[400px] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-cyan border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="glass-panel p-6 rounded-2xl">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyan" />
          <span>Mathematical Hierarchy & Summing Matrix S</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Structural summing mapping satisfying $y_t = S \cdot b_t$ where $b_t \in \mathbb&#123;R&#125;^k$ and $y_t \in \mathbb&#123;R&#125;^m$.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="p-4 bg-navy-800/80 rounded-xl border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Total Series (m)</span>
            <div className="text-2xl font-bold text-white mt-1">{hierarchy?.m_total_series}</div>
          </div>
          <div className="p-4 bg-navy-800/80 rounded-xl border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Bottom Series (k)</span>
            <div className="text-2xl font-bold text-cyan mt-1">{hierarchy?.k_bottom_series}</div>
          </div>
          <div className="p-4 bg-navy-800/80 rounded-xl border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Matrix S Dimensions</span>
            <div className="text-lg font-bold text-white mt-1">
              {matrixData ? `${matrixData.shape[0]} × ${matrixData.shape[1]}` : '-'}
            </div>
          </div>
          <div className="p-4 bg-navy-800/80 rounded-xl border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Hierarchy Depth</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">5 Tiers</div>
          </div>
        </div>
      </div>

      {/* Hierarchy Tree Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2 border-b border-white/10 pb-2">
            <Network className="w-4 h-4 text-cyan" />
            <span>Regional Aggregates</span>
          </h3>
          <div className="space-y-1 text-xs">
            {hierarchy?.regions.map((reg) => (
              <div key={reg} className="p-2 rounded bg-navy-800/60 text-slate-200 font-mono">
                {reg}
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2 border-b border-white/10 pb-2">
            <Network className="w-4 h-4 text-violet-400" />
            <span>Store Aggregates</span>
          </h3>
          <div className="space-y-1 text-xs">
            {hierarchy?.stores.map((store) => (
              <div key={store} className="p-2 rounded bg-navy-800/60 text-slate-200 font-mono">
                {store}
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2 border-b border-white/10 pb-2">
            <Network className="w-4 h-4 text-emerald-400" />
            <span>Product Categories</span>
          </h3>
          <div className="space-y-1 text-xs">
            {hierarchy?.categories.map((cat) => (
              <div key={cat} className="p-2 rounded bg-navy-800/60 text-slate-200 font-mono">
                {cat}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summing Matrix Visualizer */}
      <div className="glass-panel p-6 rounded-2xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Table className="w-4 h-4 text-cyan" />
              <span>Summing Matrix S Aggregation Mappings (Sample)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Showing active summing weights connecting upper tiers to bottom SKU x Store nodes.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto max-h-96 border border-white/10 rounded-xl">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-800 text-slate-300 sticky top-0 border-b border-white/10">
              <tr>
                <th className="p-3">Series Name (Row)</th>
                <th className="p-3">Level</th>
                <th className="p-3">Bottom Contributing Nodes (Sample)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {hierarchy?.all_series.slice(0, 15).map((sName) => (
                <tr key={sName} className="hover:bg-navy-700/40">
                  <td className="p-3 font-semibold text-white">{sName}</td>
                  <td className="p-3 text-cyan">{hierarchy.level_map[sName]}</td>
                  <td className="p-3 text-slate-400">
                    {hierarchy.level_map[sName] === 'total'
                      ? 'All 48 bottom series (Summed)'
                      : hierarchy.level_map[sName] === 'region'
                      ? '24 bottom series in operating zone'
                      : hierarchy.level_map[sName] === 'store'
                      ? '12 SKUs for this store'
                      : hierarchy.level_map[sName] === 'category'
                      ? '12 SKUs in category across stores'
                      : 'Self (Identity mapping = 1.0)'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
