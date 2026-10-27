import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { AuditLogRecord } from '../types';
import { CheckCircle2, Download, FileText, Filter, Hash, Lock, RefreshCw, ShieldCheck, XCircle } from 'lucide-react';

export const AuditTrail: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('ALL');
  const [selectedLog, setSelectedLog] = useState<AuditLogRecord | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.getAuditLogs(100);
      setLogs(res);
    } catch (e: any) {
      alert(`Failed to load audit logs: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const eventTypes = ['ALL', ...Array.from(new Set(logs.map((l) => l.event_type)))];

  const filteredLogs = selectedFilter === 'ALL'
    ? logs
    : logs.filter((l) => l.event_type === selectedFilter);

  const exportToJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(logs, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `demandwise_audit_ledger_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Lock className="w-5 h-5 text-cyan" />
            <span>Cryptographic Governance & Audit Ledger</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Immutable, SHA-256 hash-chained compliance audit log tracking all dataset uploads, model executions, reconciliations, and inventory simulations.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={exportToJson}
            className="px-3.5 py-2 rounded-xl bg-navy-800 border border-white/10 text-slate-300 text-xs font-semibold flex items-center space-x-2 hover:bg-navy-700 transition"
          >
            <Download className="w-3.5 h-3.5 text-cyan" />
            <span>Export JSON Ledger</span>
          </button>

          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-cyan text-navy-950 text-xs font-bold flex items-center space-x-1.5 hover:bg-cyan/90 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Ledger</span>
          </button>
        </div>
      </div>

      {/* Ledger Stats Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-cyan/10 flex items-center justify-center text-cyan">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white font-mono">{logs.length}</div>
            <div className="text-xs text-slate-400">Total Immutable Records</div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm font-bold text-white flex items-center space-x-1">
              <span>SHA-256 Chained</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-xs text-slate-400">Tamper-Evident Hash Verification</div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
            <Hash className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">SQLite Persistent</div>
            <div className="text-xs text-slate-400">artifacts/demandwise_audit.db</div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center space-x-3 text-xs">
        <span className="text-slate-400 flex items-center space-x-1">
          <Filter className="w-3.5 h-3.5" />
          <span>Filter by Event:</span>
        </span>
        <div className="flex flex-wrap gap-2">
          {eventTypes.map((type) => (
            <button
              key={type}
              onClick={() => setSelectedFilter(type)}
              className={`px-3 py-1.5 rounded-lg font-mono text-xs transition ${
                selectedFilter === type
                  ? 'bg-cyan text-navy-950 font-bold'
                  : 'bg-navy-800 text-slate-400 hover:text-white border border-white/5'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Ledger Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-white/10">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-800 text-slate-300 border-b border-white/10">
              <tr>
                <th className="p-3.5">ID</th>
                <th className="p-3.5">Timestamp (UTC)</th>
                <th className="p-3.5">Event Type</th>
                <th className="p-3.5">Action</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Actor</th>
                <th className="p-3.5">Record Hash (SHA-256)</th>
                <th className="p-3.5">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-navy-700/40">
                  <td className="p-3.5 text-slate-400">#{log.id}</td>
                  <td className="p-3.5 text-slate-300">{log.timestamp.slice(0, 19).replace('T', ' ')}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded bg-navy-800 text-cyan border border-cyan/20 text-[11px]">
                      {log.event_type}
                    </span>
                  </td>
                  <td className="p-3.5 font-semibold text-white">{log.action}</td>
                  <td className="p-3.5">
                    {log.status === 'SUCCESS' ? (
                      <span className="inline-flex items-center space-x-1 text-emerald-400 text-[11px]">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>SUCCESS</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 text-rose-400 text-[11px]">
                        <XCircle className="w-3.5 h-3.5" />
                        <span>FAILED</span>
                      </span>
                    )}
                  </td>
                  <td className="p-3.5 text-slate-400">{log.actor}</td>
                  <td className="p-3.5 text-slate-400 font-mono text-[11px]">
                    <span title={log.record_hash} className="cursor-help text-cyan/80 hover:text-cyan">
                      {log.record_hash.slice(0, 14)}...
                    </span>
                  </td>
                  <td className="p-3.5">
                    <button
                      onClick={() => setSelectedLog(log)}
                      className="text-cyan underline hover:text-cyan/80 font-sans text-xs"
                    >
                      View Payload
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-navy-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl max-w-2xl w-full space-y-4 border border-cyan/30 shadow-2xl">
            <div className="flex justify-between items-center border-b border-white/10 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <FileText className="w-4 h-4 text-cyan" />
                <span>Audit Record #{selectedLog.id} — Payload Details</span>
              </h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-slate-400 hover:text-white font-mono text-sm"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Timestamp:</span>
                <span className="text-white font-mono">{selectedLog.timestamp}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Full SHA-256 Hash:</span>
                <span className="text-cyan font-mono text-[11px] select-all">{selectedLog.record_hash}</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Parsed JSON Payload:</label>
              <pre className="bg-navy-900 border border-white/10 rounded-xl p-4 text-[11px] font-mono text-emerald-400 overflow-auto max-h-72">
                {JSON.stringify(selectedLog.details, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 rounded-xl bg-navy-800 border border-white/10 text-white text-xs hover:bg-navy-700 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
