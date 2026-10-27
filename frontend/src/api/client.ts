/**
 * DemandWise API Client
 */

import {
  AuditLogRecord,
  CalibrationResponse,
  DataQualityResult,
  DatasetSummary,
  DriftResponse,
  ForecastResponse,
  HierarchySummary,
  InventorySimResponse,
  ReconciliationResponse,
  SummingMatrixData,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const resp = await fetch(url, {
    ...options,
    headers: {
      'Content-Control': 'no-cache',
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!resp.ok) {
    const errorText = await resp.text();
    let parsedError = errorText;
    try {
      const errObj = JSON.parse(errorText);
      parsedError = errObj.detail || errorText;
    } catch {
      // Keep raw
    }
    throw new Error(`API Error [${resp.status}]: ${parsedError}`);
  }

  return resp.json();
}

export const api = {
  // Datasets
  getDatasetSummary: () => fetchJson<DatasetSummary>('/datasets'),
  getDataQuality: () => fetchJson<DataQualityResult>('/datasets/quality'),
  generateDemo: (numSkus = 12, numStores = 4, numRegions = 2, randomSeed = 42) =>
    fetchJson<DatasetSummary>('/datasets/generate-demo', {
      method: 'POST',
      body: JSON.stringify({
        num_skus: numSkus,
        num_stores: numStores,
        num_regions: numRegions,
        random_seed: randomSeed,
      }),
    }),
  uploadDataset: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const resp = await fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!resp.ok) {
      const errorText = await resp.text();
      throw new Error(`Upload Error [${resp.status}]: ${errorText}`);
    }
    return resp.json();
  },

  // Hierarchy
  getHierarchySummary: () => fetchJson<HierarchySummary>('/hierarchy'),
  getSummingMatrix: () => fetchJson<SummingMatrixData>('/hierarchy/summing-matrix'),

  // Forecasting
  getModels: () => fetchJson<string[]>('/forecasts/models'),
  generateForecast: (seriesName: string, modelName: string, horizon: number) =>
    fetchJson<ForecastResponse>('/forecasts', {
      method: 'POST',
      body: JSON.stringify({
        series_name: seriesName,
        model_name: modelName,
        horizon,
      }),
    }),

  // Reconciliation
  runReconciliation: (baseModelName: string, horizon: number) =>
    fetchJson<ReconciliationResponse>('/reconciliation', {
      method: 'POST',
      body: JSON.stringify({
        base_model_name: baseModelName,
        horizon,
      }),
    }),

  // Uncertainty & Calibration
  evaluateCalibration: (seriesName: string, horizon: number) =>
    fetchJson<CalibrationResponse>('/calibration/evaluate', {
      method: 'POST',
      body: JSON.stringify({
        series_name: seriesName,
        horizon,
      }),
    }),

  // Inventory
  simulateInventory: (params: {
    sku_id: string;
    store_id: string;
    lead_time_days: number;
    review_period_days: number;
    target_service_level: number;
    holding_cost_daily: number;
    stockout_penalty: number;
    ordering_cost: number;
  }) =>
    fetchJson<InventorySimResponse>('/inventory/simulations', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  // Evaluations & Benchmarks
  getBenchmarks: () => fetchJson<Record<string, any>>('/evaluations/benchmark'),

  // Monitoring & Audit
  getDrift: (seriesName = 'Total') =>
    fetchJson<DriftResponse>(`/monitoring/drift?series_name=${encodeURIComponent(seriesName)}`),
  getAuditLogs: (limit = 50) => fetchJson<AuditLogRecord[]>(`/monitoring/audit?limit=${limit}`),
};
