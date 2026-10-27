"""Reconciliation service for hierarchical coherence optimization."""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
import pandas as pd

from backend.app.schemas.reconciliation import (
    ReconciliationMethodSummary,
    ReconciliationResponse,
)
from backend.app.services.data_service import DataService, audit_logger
from backend.app.services.forecast_service import ForecastService
from demandwise.evaluation.metrics import calculate_coherence_metrics, calculate_forecast_metrics
from demandwise.reconciliation.reconciler import ForecastReconciler


class ReconciliationService:
    """Manages hierarchical forecast reconciliation and cross-echelon coherence."""

    @classmethod
    def run_reconciliation(
        cls,
        base_model_name: str = "lightgbm",
        horizon: int = 14,
        test_days: int = 28,
    ) -> ReconciliationResponse:
        tree, wide_df = DataService.get_hierarchy_tree()
        all_series = tree.all_series
        bottom_series = tree.bottom_series
        S = tree.summing_matrix.matrix
        k = tree.k
        m_count = len(all_series)

        # Train/test split
        train_df = wide_df.iloc[:-test_days]
        test_df = wide_df.iloc[-test_days : -test_days + horizon]

        # Generate base forecasts for all series
        y_hat_matrix = np.zeros((m_count, horizon))
        residuals_matrix = np.zeros((m_count, 30))

        for idx, s_name in enumerate(all_series):
            series_train = train_df[s_name]
            model = ForecastService.get_model_instance(base_model_name)
            model.fit(series_train)
            preds = model.predict(horizon)
            y_hat_matrix[idx, :] = preds

            # In-sample residuals for MinT
            res = model.residuals if model.residuals is not None else np.array([0.0])
            if len(res) >= 30:
                residuals_matrix[idx, :] = res[-30:]
            else:
                residuals_matrix[idx, :] = np.pad(res, (max(0, 30 - len(res)), 0))

        reconciler = ForecastReconciler(tree.summing_matrix)
        rec_dict = reconciler.reconcile_all(
            y_hat_matrix,
            residuals=residuals_matrix,
            historical_bottom=train_df[bottom_series].values,
        )

        test_acts = test_df[all_series].values.T
        tot_act = test_acts[0, :]
        bot_act = test_acts[-k:, :]

        summaries: List[ReconciliationMethodSummary] = []
        top_comparison: List[Dict[str, Any]] = []

        # Prepare dates
        dates = [d.strftime("%Y-%m-%d") for d in test_df.index[:horizon]]

        # Initialize top-level comparison dictionary per date
        for step_i in range(horizon):
            top_comparison.append({"date": dates[step_i], "actual": round(float(tot_act[step_i]), 2)})

        for rec_name, rec_res in rec_dict.items():
            y_rec = rec_res.reconciled_forecasts
            coh_m = calculate_coherence_metrics(y_rec, S, k)

            tot_pred = y_rec[0, :]
            tot_m = calculate_forecast_metrics(tot_act, tot_pred, train_df["Total"].values)

            bot_pred = y_rec[-k:, :]
            bot_maes = [float(np.mean(np.abs(bot_act[i, :] - bot_pred[i, :]))) for i in range(k)]
            avg_bot_mae = float(np.mean(bot_maes))

            summaries.append(
                ReconciliationMethodSummary(
                    method=rec_name,
                    is_coherent=coh_m["is_coherent"],
                    max_coherence_error=round(coh_m["max_coherence_error"], 4),
                    mean_coherence_error=round(coh_m["mean_coherence_error"], 4),
                    total_series_mae=round(tot_m.mae, 2),
                    avg_bottom_mae=round(avg_bot_mae, 2),
                    total_wape_pct=round(tot_m.wape * 100.0, 2),
                )
            )

            # Add to top comparison
            for step_i in range(horizon):
                top_comparison[step_i][rec_name] = round(float(tot_pred[step_i]), 2)

        audit_logger.log_event(
            event_type="RECONCILIATION",
            action="Executed hierarchical forecast reconciliation",
            details={
                "base_model": base_model_name,
                "horizon": horizon,
                "methods": [s.method for s in summaries],
            },
        )

        return ReconciliationResponse(
            horizon=horizon,
            base_model=base_model_name,
            methods=summaries,
            top_level_comparison=top_comparison,
        )
