/**
 * DemandWise TypeScript Data Types & Schemas
 */

export interface DatasetSummary {
  name: string;
  file_path: string;
  total_records: number;
  num_skus: number;
  num_stores: number;
  num_categories: number;
  num_regions: number;
  date_min: string;
  date_max: string;
  zero_demand_percentage: number;
  total_revenue: number;
  total_units: number;
}

export interface DataQualityIssue {
  severity: 'ERROR' | 'WARNING' | 'INFO';
  field?: string;
  message: string;
  count?: number;
}

export interface DataQualityResult {
  is_valid: boolean;
  total_records: number;
  num_skus: number;
  num_stores: number;
  num_categories: number;
  num_regions: number;
  missing_dates_count: number;
  duplicate_rows_count: number;
  negative_quantity_count: number;
  zero_demand_percentage: number;
  missing_values: Record<string, number>;
  issues: DataQualityIssue[];
}

export interface HierarchySummary {
  m_total_series: number;
  k_bottom_series: number;
  levels: string[];
  regions: string[];
  stores: string[];
  categories: string[];
  bottom_series: string[];
  all_series: string[];
  level_map: Record<string, string>;
}

export interface SummingMatrixData {
  shape: [number, number];
  series_names: string[];
  bottom_names: string[];
  non_zero_coordinates: [number, number][];
}

export interface PointForecastPoint {
  date: string;
  actual?: number | null;
  forecast: number;
}

export interface ModelAccuracyMetrics {
  mae: number;
  rmse: number;
  mase: number;
  rmsse: number;
  bias: number;
  norm_bias_pct: number;
  wape_pct: number;
}

export interface ForecastResponse {
  series_name: string;
  model_name: string;
  horizon: number;
  train_end_date: string;
  test_start_date: string;
  metrics: ModelAccuracyMetrics;
  predictions: PointForecastPoint[];
  historical_tail: { date: string; demand: number }[];
}

export interface ReconciliationMethodSummary {
  method: string;
  is_coherent: boolean;
  max_coherence_error: number;
  mean_coherence_error: number;
  total_series_mae: number;
  avg_bottom_mae: number;
  total_wape_pct: number;
}

export interface ReconciliationResponse {
  horizon: number;
  base_model: string;
  methods: ReconciliationMethodSummary[];
  top_level_comparison: Record<string, any>[];
}

export interface CalibrationMetricRow {
  method: string;
  nominal_level: number;
  empirical_coverage: number;
  coverage_error: number;
  mean_width: number;
  winkler_score: number;
}

export interface IntervalPoint {
  date: string;
  actual: number;
  point_forecast: number;
  lower_80: number;
  upper_80: number;
  lower_95: number;
  upper_95: number;
}

export interface CalibrationResponse {
  series_name: string;
  horizon: number;
  summary_metrics: CalibrationMetricRow[];
  conformal_intervals: IntervalPoint[];
  bootstrap_intervals: IntervalPoint[];
}

export interface DailyInventoryStep {
  day_idx: number;
  date: string;
  starting_stock: number;
  orders_arrived: number;
  actual_demand: number;
  fulfilled_units: number;
  lost_sales: number;
  ending_stock: number;
  pipeline_stock: number;
  order_placed: boolean;
  order_quantity: number;
  holding_cost: number;
  stockout_cost: number;
  total_cost: number;
}

export interface PolicySummary {
  policy: string;
  total_demand: number;
  fulfilled_units: number;
  lost_sales: number;
  fill_rate_pct: number;
  stockout_days: number;
  orders_placed: number;
  holding_cost: number;
  stockout_cost: number;
  ordering_cost: number;
  total_cost: number;
}

export interface InventorySimResponse {
  sku_id: string;
  store_id: string;
  horizon_days: number;
  policies_summary: PolicySummary[];
  daily_trajectory: DailyInventoryStep[];
}

export interface DriftResponse {
  series_name: string;
  psi_value: number;
  psi_alert_level: 'STABLE' | 'MODERATE' | 'SIGNIFICANT';
  max_tracking_signal: number;
  tracking_signal_alert: boolean;
  summary: string;
}

export interface AuditLogRecord {
  id: number;
  timestamp: string;
  event_type: string;
  action: string;
  status: string;
  actor: string;
  details: Record<string, any>;
  record_hash: string;
}
