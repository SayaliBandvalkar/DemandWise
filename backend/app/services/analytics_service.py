"""Analytics, evaluation benchmark, drift monitoring, and audit log service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from backend.app.core.config import settings
from backend.app.schemas.monitoring import AuditLogRecordResponse, DriftResponse
from backend.app.services.data_service import DataService, audit_logger
from demandwise.monitoring.drift import calculate_psi, calculate_tracking_signal


class AnalyticsService:
    """Manages benchmarks, drift detection, and compliance audit trail retrieval."""

    @classmethod
    def get_benchmark_results(cls) -> Dict[str, Any]:
        """Fetch pre-computed benchmark results or fallback to basic structure."""
        json_path = settings.artifacts_dir / "experiments" / "benchmark_results.json"
        if json_path.exists():
            with open(json_path, "r") as f:
                return json.load(f)
        return {
            "models_benchmark": [],
            "reconciliation_benchmark": [],
            "calibration_summary": [],
            "inventory_benchmark": [],
            "ablation_stress_test": [],
        }

    @classmethod
    def evaluate_drift(cls, series_name: str = "Total") -> DriftResponse:
        """Compute PSI and Tracking Signal between train baseline and test periods."""
        tree, wide_df = DataService.get_hierarchy_tree()

        if series_name not in wide_df.columns:
            series_name = "Total"

        full_series = wide_df[series_name]
        n_total = len(full_series)

        baseline = full_series.iloc[: n_total - 28].values
        target = full_series.iloc[n_total - 28 :].values

        psi_val = calculate_psi(baseline, target)
        if psi_val < 0.10:
            level = "STABLE"
            summary = "No significant distributional shift detected between baseline and target periods."
        elif psi_val < 0.25:
            level = "MODERATE"
            summary = "Moderate distributional shift detected. Model performance should be closely watched."
        else:
            level = "SIGNIFICANT"
            summary = "Significant distributional shift detected. Retraining is strongly recommended."

        # Tracking signal on last 14 days
        test_acts = target[:14]
        # Baseline mean forecast
        mean_base = float(np.mean(baseline[-14:]))
        fc_dummy = np.full(len(test_acts), mean_base)
        _, max_ts = calculate_tracking_signal(test_acts, fc_dummy)

        return DriftResponse(
            series_name=series_name,
            psi_value=round(psi_val, 4),
            psi_alert_level=level,
            max_tracking_signal=round(max_ts, 2),
            tracking_signal_alert=max_ts > 4.0,
            summary=summary,
        )

    @classmethod
    def get_audit_logs(cls, limit: int = 50) -> List[AuditLogRecordResponse]:
        """Retrieve recent SQLite audit log entries."""
        df = audit_logger.get_recent_logs(limit=limit)
        records: List[AuditLogRecordResponse] = []
        for _, row in df.iterrows():
            details_obj = {}
            try:
                details_obj = json.loads(row["details_json"])
            except Exception:
                details_obj = {"raw": str(row["details_json"])}

            records.append(
                AuditLogRecordResponse(
                    id=int(row["id"]),
                    timestamp=str(row["timestamp"]),
                    event_type=str(row["event_type"]),
                    action=str(row["action"]),
                    status=str(row["status"]),
                    actor=str(row["actor"]),
                    details=details_obj,
                    record_hash=str(row["record_hash"]),
                )
            )
        return records
