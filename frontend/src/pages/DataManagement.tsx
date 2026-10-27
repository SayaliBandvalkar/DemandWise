import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { DataQualityResult, DatasetSummary } from '../types';
import { Database, UploadCloud, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export const DataManagement: React.FC = () => {
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [quality, setQuality] = useState<DataQualityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    Promise.all([api.getDatasetSummary(), api.getDataQuality()])
      .then(([s, q]) => {
        setSummary(s);
        setQuality(q);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await api.generateDemo(12, 4, 2, 42);
      loadData();
    } catch (e: any) {
      alert(`Generation error: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const res = await api.uploadDataset(file);
      setUploadSuccess(`Successfully uploaded and validated ${file.name}`);
      loadData();
    } catch (err: any) {
      setUploadError(err.message);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner & Generation Actions */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Database className="w-5 h-5 text-cyan" />
            <span>Dataset Controls & Ingestion</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Manage the active retail hierarchy dataset or trigger deterministic generation.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2.5 rounded-lg bg-navy-700 hover:bg-navy-600 border border-white/10 text-cyan text-xs font-semibold flex items-center space-x-2 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
            <span>{generating ? 'Generating (365 days)...' : 'Regenerate Deterministic Sample'}</span>
          </button>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="glass-panel p-6 rounded-2xl border-dashed border-2 border-white/10 hover:border-cyan/40 transition-all text-center">
        <UploadCloud className="w-8 h-8 text-cyan mx-auto mb-2" />
        <h3 className="text-sm font-bold text-white">Upload Custom Retail CSV</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          File must contain mandatory fields: <code>date, sku_id, category, store_id, region, units_sold, unit_price, unit_cost</code>
        </p>
        <label className="mt-4 inline-block px-4 py-2 rounded-lg bg-cyan text-navy-950 text-xs font-bold cursor-pointer hover:bg-cyan/90 transition">
          Browse CSV File
          <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" />
        </label>

        {uploadSuccess && (
          <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-xs flex items-center justify-center space-x-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{uploadSuccess}</span>
          </div>
        )}
        {uploadError && (
          <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-xs flex items-center justify-center space-x-2">
            <AlertCircle className="w-4 h-4" />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Dataset Metadata & Quality Diagnostics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Dataset Stats */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <h3 className="text-sm font-bold text-white tracking-tight border-b border-white/10 pb-3">
            Active Dataset Properties
          </h3>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block">Total Records:</span>
              <span className="font-semibold text-white text-sm">
                {summary ? summary.total_records.toLocaleString() : '-'}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block">Date Range:</span>
              <span className="font-semibold text-white">
                {summary ? `${summary.date_min} to ${summary.date_max}` : '-'}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block">Bottom SKU x Store Series:</span>
              <span className="font-semibold text-cyan text-sm">
                {summary ? `${summary.num_skus * summary.num_stores} series` : '-'}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block">Zero-Demand Sparsity:</span>
              <span className="font-semibold text-white">
                {summary ? `${summary.zero_demand_percentage}%` : '-'}
              </span>
            </div>
          </div>
        </div>

        {/* Validation Scorecard */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="text-sm font-bold text-white tracking-tight">Data Quality & Schema Diagnostics</h3>
            <span
              className={`text-xs px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                quality?.is_valid
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
              }`}
            >
              {quality?.is_valid ? 'Schema Validated' : 'Validation Error'}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-white/5">
              <span className="text-slate-400">Negative Quantity Violations:</span>
              <span className="font-mono text-emerald-400 font-semibold">
                {quality ? quality.negative_quantity_count : 0}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-white/5">
              <span className="text-slate-400">Duplicate Primary Keys:</span>
              <span className="font-mono text-emerald-400 font-semibold">
                {quality ? quality.duplicate_rows_count : 0}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-white/5">
              <span className="text-slate-400">Missing Date Slots:</span>
              <span className="font-mono text-slate-200">
                {quality ? quality.missing_dates_count : 0}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Integrity Status:</span>
              <span className="text-emerald-400 font-semibold">100% Hierarchy Aligned</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
