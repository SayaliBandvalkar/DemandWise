"""Probabilistic calibration and prediction interval service."""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
import pandas as pd

from backend.app.schemas.uncertainty import (
    CalibrationMetricRow,
    CalibrationResponse,
    IntervalPoint,
)
from backend.app.services.data_service import DataService, audit_logger
from backend.app.services.forecast_service import ForecastService
from demandwise.uncertainty.calibration import evaluate_interval_calibration
from demandwise.uncertainty.intervals import calculate_prediction_intervals


class CalibrationService:
    """Evaluates probabilistic uncertainty quantification and interval calibration."""

    @classmethod
    def evaluate_calibration(
        cls,
        series_name: str = "Total",
        horizon: int = 14,
        test_days: int = 28,
    ) -> CalibrationResponse:
        tree, wide_df = DataService.get_hierarchy_tree()

        if series_name not in wide_df.columns:
            series_name = "Total"

        full_series = wide_df[series_name]
        n_total = len(full_series)

        train_end_idx = n_total - test_days
        y_train = full_series.iloc[:train_end_idx]
        test_end_idx = min(n_total, train_end_idx + horizon)
        y_test = full_series.iloc[train_end_idx:test_end_idx]
        h = len(y_test)

        # Fit model
        model = ForecastService.get_model_instance("lightgbm")
        model.fit(y_train)
        point_pred = model.predict(h)
        residuals = model.residuals if model.residuals is not None else np.array([1.0])

        # Calibration set for conformal prediction (last 14 days of train)
        cal_actuals = y_train.values[-14:]
        cal_preds = np.full(14, float(np.mean(cal_actuals)))

        summary_metrics: List[CalibrationMetricRow] = []

        # Bootstrap intervals (80% and 95%)
        boot_intervals = calculate_prediction_intervals(
            point_forecast=point_pred,
            residuals=residuals,
            confidence_levels=[0.80, 0.95],
            method="bootstrap",
        )

        for lvl in [0.80, 0.95]:
            rep = evaluate_interval_calibration(y_test.values, boot_intervals[lvl])
            summary_metrics.append(
                CalibrationMetricRow(
                    method="Residual Bootstrap",
                    nominal_level=lvl,
                    empirical_coverage=round(rep.empirical_coverage * 100.0, 1),
                    coverage_error=round(rep.coverage_error * 100.0, 1),
                    mean_width=round(rep.mean_width, 2),
                    winkler_score=round(rep.mean_winkler_score, 2),
                )
            )

        # Conformal intervals (80% and 95%)
        conf_intervals = calculate_prediction_intervals(
            point_forecast=point_pred,
            residuals=residuals,
            confidence_levels=[0.80, 0.95],
            method="conformal",
            cal_actuals=cal_actuals,
            cal_preds=cal_preds,
        )

        for lvl in [0.80, 0.95]:
            rep = evaluate_interval_calibration(y_test.values, conf_intervals[lvl])
            summary_metrics.append(
                CalibrationMetricRow(
                    method="Split Conformal Prediction",
                    nominal_level=lvl,
                    empirical_coverage=round(rep.empirical_coverage * 100.0, 1),
                    coverage_error=round(rep.coverage_error * 100.0, 1),
                    mean_width=round(rep.mean_width, 2),
                    winkler_score=round(rep.mean_winkler_score, 2),
                )
            )

        dates = [dt.strftime("%Y-%m-%d") for dt in y_test.index]
        conf_points: List[IntervalPoint] = []
        boot_points: List[IntervalPoint] = []

        for i in range(h):
            conf_points.append(
                IntervalPoint(
                    date=dates[i],
                    actual=round(float(y_test.iloc[i]), 2),
                    point_forecast=round(float(point_pred[i]), 2),
                    lower_80=round(float(conf_intervals[0.80].lower_bound[i]), 2),
                    upper_80=round(float(conf_intervals[0.80].upper_bound[i]), 2),
                    lower_95=round(float(conf_intervals[0.95].lower_bound[i]), 2),
                    upper_95=round(float(conf_intervals[0.95].upper_bound[i]), 2),
                )
            )
            boot_points.append(
                IntervalPoint(
                    date=dates[i],
                    actual=round(float(y_test.iloc[i]), 2),
                    point_forecast=round(float(point_pred[i]), 2),
                    lower_80=round(float(boot_intervals[0.80].lower_bound[i]), 2),
                    upper_80=round(float(boot_intervals[0.80].upper_bound[i]), 2),
                    lower_95=round(float(boot_intervals[0.95].lower_bound[i]), 2),
                    upper_95=round(float(boot_intervals[0.95].upper_bound[i]), 2),
                )
            )

        audit_logger.log_event(
            event_type="CALIBRATION",
            action=f"Evaluated interval calibration for {series_name}",
            details={"horizon": h, "series": series_name},
        )

        return CalibrationResponse(
            series_name=series_name,
            horizon=h,
            summary_metrics=summary_metrics,
            conformal_intervals=conf_points,
            bootstrap_intervals=boot_points,
        )
