"""Forecasting service wrapping core forecasters and accuracy metrics."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from backend.app.schemas.forecast import (
    ForecastResponse,
    ModelAccuracyMetrics,
    PointForecastPoint,
)
from backend.app.services.data_service import DataService, audit_logger
from demandwise.evaluation.metrics import calculate_forecast_metrics
from demandwise.forecasting.models import (
    CrostonForecaster,
    ExponentialSmoothingForecaster,
    LightGBMForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
    get_available_forecasters,
)


class ForecastService:
    """Orchestrates time-series splitting, model training, prediction, and metric computation."""

    @classmethod
    def get_model_instance(cls, model_name: str):
        name = model_name.lower()
        if "seasonal" in name:
            return SeasonalNaiveForecaster(seasonality=7)
        elif "naive" in name:
            return NaiveForecaster()
        elif "croston" in name or "sba" in name:
            return CrostonForecaster(method="sba")
        elif "exponential" in name or "holt" in name:
            return ExponentialSmoothingForecaster()
        else:
            return LightGBMForecaster()

    @classmethod
    def generate_forecast(
        cls,
        series_name: str = "Total",
        model_name: str = "lightgbm",
        horizon: int = 14,
        test_days: int = 28,
    ) -> ForecastResponse:
        """Fit model on training portion of series and forecast future horizon."""
        tree, wide_df = DataService.get_hierarchy_tree()

        if series_name not in wide_df.columns:
            # Fallback to closest match or Total
            series_name = "Total"

        full_series = wide_df[series_name]
        n_total = len(full_series)

        # Chronological forward split (zero lookahead leakage)
        train_end_idx = n_total - test_days
        y_train = full_series.iloc[:train_end_idx]
        test_end_idx = min(n_total, train_end_idx + horizon)
        y_test = full_series.iloc[train_end_idx:test_end_idx]

        model = cls.get_model_instance(model_name)
        model.fit(y_train)
        predictions = model.predict(len(y_test))

        # Metrics against actuals
        m = calculate_forecast_metrics(y_test.values, predictions, y_train.values)

        pred_points: List[PointForecastPoint] = []
        for i, dt in enumerate(y_test.index):
            pred_points.append(
                PointForecastPoint(
                    date=dt.strftime("%Y-%m-%d"),
                    actual=round(float(y_test.iloc[i]), 2),
                    forecast=round(float(predictions[i]), 2),
                )
            )

        # Historical tail (last 45 days of train for visual context)
        hist_tail_slice = y_train.iloc[-45:]
        hist_tail = [
            {"date": dt.strftime("%Y-%m-%d"), "demand": round(float(val), 2)}
            for dt, val in hist_tail_slice.items()
        ]

        metrics = ModelAccuracyMetrics(
            mae=round(m.mae, 2),
            rmse=round(m.rmse, 2),
            mase=round(m.mase, 3),
            rmsse=round(m.rmsse, 3),
            bias=round(m.bias, 2),
            norm_bias_pct=round(m.percentage_bias, 2),
            wape_pct=round(m.wape * 100.0, 2),
        )

        audit_logger.log_event(
            event_type="FORECAST_RUN",
            action=f"Generate {model_name} forecast for {series_name}",
            details={"horizon": horizon, "mae": metrics.mae, "wape_pct": metrics.wape_pct},
        )

        return ForecastResponse(
            series_name=series_name,
            model_name=model.name,
            horizon=len(y_test),
            train_end_date=y_train.index[-1].strftime("%Y-%m-%d"),
            test_start_date=y_test.index[0].strftime("%Y-%m-%d"),
            metrics=metrics,
            predictions=pred_points,
            historical_tail=hist_tail,
        )
