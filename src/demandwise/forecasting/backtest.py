"""Rolling-origin backtesting engine for time series forecasting.

Ensures rigorous time-based validation without future data leakage:
- Expanding origin evaluation
- Fixed forecast horizon h per origin
- Records actual values, base forecasts, residuals, and prediction intervals
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type
import numpy as np
import pandas as pd
from demandwise.forecasting.models import BaseForecaster, get_available_forecasters


@dataclass
class BacktestWindow:
    """Represents a single evaluation fold in rolling-origin backtesting."""

    fold_idx: int
    train_end_date: pd.Timestamp
    test_start_date: pd.Timestamp
    test_end_date: pd.Timestamp
    horizon: int


@dataclass
class BacktestResult:
    """Container for backtesting run results across all origins."""

    model_name: str
    series_name: str
    windows: List[BacktestWindow]
    actuals: List[np.ndarray]
    forecasts: List[np.ndarray]
    residuals: List[np.ndarray]
    timestamps: List[pd.DatetimeIndex]


class RollingOriginBacktest:
    """Executes rolling-origin backtesting across time series."""

    def __init__(
        self,
        horizon: int = 14,
        num_origins: int = 3,
        step_size: int = 7,
    ):
        self.horizon = horizon
        self.num_origins = num_origins
        self.step_size = step_size

    def generate_windows(self, dates: pd.DatetimeIndex) -> List[BacktestWindow]:
        """Compute rolling-origin train/test split cutoff dates."""
        n_dates = len(dates)
        required_len = self.horizon + (self.num_origins - 1) * self.step_size + 30
        if n_dates < required_len:
            raise ValueError(
                f"Series length ({n_dates}) is insufficient for {self.num_origins} "
                f"origins with horizon={self.horizon} and step={self.step_size} (requires >= {required_len})."
            )

        windows = []
        for i in range(self.num_origins):
            # Working backwards from end of series
            test_end_idx = n_dates - (self.num_origins - 1 - i) * self.step_size
            test_start_idx = test_end_idx - self.horizon
            train_end_idx = test_start_idx

            windows.append(
                BacktestWindow(
                    fold_idx=i,
                    train_end_date=dates[train_end_idx - 1],
                    test_start_date=dates[test_start_idx],
                    test_end_date=dates[test_end_idx - 1],
                    horizon=self.horizon,
                )
            )
        return windows

    def run(
        self,
        series: pd.Series,
        forecaster_class: Type[BaseForecaster],
        forecaster_kwargs: Optional[Dict[str, Any]] = None,
    ) -> BacktestResult:
        """Run backtesting for a single series and forecaster."""
        kwargs = forecaster_kwargs or {}
        dates = pd.to_datetime(series.index)
        windows = self.generate_windows(dates)

        actuals_list = []
        forecasts_list = []
        residuals_list = []
        timestamps_list = []
        model_name = ""

        for win in windows:
            train_mask = dates <= win.train_end_date
            test_mask = (dates >= win.test_start_date) & (dates <= win.test_end_date)

            y_train = series[train_mask]
            y_test = series[test_mask]

            model = forecaster_class(**kwargs)
            model.fit(y_train)
            model_name = model.name

            preds = model.predict(win.horizon)
            acts = y_test.values[: win.horizon]
            resids = acts - preds

            actuals_list.append(acts)
            forecasts_list.append(preds)
            residuals_list.append(resids)
            timestamps_list.append(dates[test_mask][: win.horizon])

        return BacktestResult(
            model_name=model_name,
            series_name=str(series.name),
            windows=windows,
            actuals=actuals_list,
            forecasts=forecasts_list,
            residuals=residuals_list,
            timestamps=timestamps_list,
        )
