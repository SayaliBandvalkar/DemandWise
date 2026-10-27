"""Probabilistic prediction interval methods for demand forecasting.

Implements:
1. Residual-based parametric intervals (variance scaling over horizon: sigma_h = sigma * sqrt(h))
2. Residual bootstrap simulation (non-parametric empirical path sampling)
3. Conformal Prediction (finite-sample distribution-free coverage guarantee)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import scipy.stats as stats


@dataclass
class PredictionInterval:
    """Represents probabilistic prediction intervals for a forecast horizon."""

    nominal_level: float  # e.g., 0.80 or 0.95
    point_forecast: np.ndarray
    lower_bound: np.ndarray
    upper_bound: np.ndarray
    method: str  # 'bootstrap', 'conformal', 'parametric'

    def __post_init__(self):
        # Physical constraint: retail demand cannot be negative
        self.lower_bound = np.maximum(0.0, self.lower_bound)
        self.upper_bound = np.maximum(self.lower_bound, self.upper_bound)
        self.point_forecast = np.maximum(0.0, self.point_forecast)

    @property
    def width(self) -> np.ndarray:
        """Interval width for each horizon step."""
        return self.upper_bound - self.lower_bound


class ResidualBootstrapIntervals:
    """Non-parametric residual bootstrap generator."""

    def __init__(self, n_bootstraps: int = 1000, random_seed: int = 42):
        self.n_bootstraps = n_bootstraps
        self.rng = np.random.default_rng(random_seed)

    def generate(
        self,
        point_forecast: np.ndarray,
        residuals: np.ndarray,
        confidence_level: float = 0.95,
    ) -> PredictionInterval:
        """Sample empirical residuals with replacement to construct prediction paths."""
        h = len(point_forecast)
        clean_residuals = residuals[~np.isnan(residuals)]

        if len(clean_residuals) < 5:
            # Fallback if residuals are insufficient: nominal 20% margin
            std = float(np.mean(point_forecast) * 0.20) if len(point_forecast) > 0 else 1.0
            clean_residuals = self.rng.normal(0, max(0.5, std), size=50)

        # Draw (n_bootstraps, h) residual samples
        boot_resids = self.rng.choice(clean_residuals, size=(self.n_bootstraps, h), replace=True)

        # Simulated demand paths
        simulated_paths = point_forecast + boot_resids
        simulated_paths = np.maximum(0.0, simulated_paths)

        # Compute empirical quantiles
        alpha = 1.0 - confidence_level
        q_low = (alpha / 2.0) * 100.0
        q_high = (1.0 - alpha / 2.0) * 100.0

        lower = np.percentile(simulated_paths, q_low, axis=0)
        upper = np.percentile(simulated_paths, q_high, axis=0)

        return PredictionInterval(
            nominal_level=confidence_level,
            point_forecast=point_forecast,
            lower_bound=lower,
            upper_bound=upper,
            method="bootstrap",
        )


class ConformalPredictor:
    """Split Conformal Prediction for time-series forecasting intervals."""

    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)
        self.cal_scores: Optional[np.ndarray] = None

    def fit_calibration(self, y_cal: np.ndarray, y_hat_cal: np.ndarray) -> ConformalPredictor:
        """Compute nonconformity scores: absolute residuals on held-out calibration set."""
        self.cal_scores = np.abs(y_cal - y_hat_cal)
        return self

    def predict_intervals(
        self,
        point_forecast: np.ndarray,
        confidence_level: float = 0.95,
    ) -> PredictionInterval:
        """Compute conformal prediction interval bounds with theoretical finite-sample coverage."""
        if self.cal_scores is None or len(self.cal_scores) == 0:
            # Default fallback to 15% width
            margin = point_forecast * 0.20
            return PredictionInterval(
                nominal_level=confidence_level,
                point_forecast=point_forecast,
                lower_bound=np.maximum(0.0, point_forecast - margin),
                upper_bound=point_forecast + margin,
                method="conformal_fallback",
            )

        n = len(self.cal_scores)
        alpha = 1.0 - confidence_level
        # Conformal quantile index: ceil((n + 1) * (1 - alpha)) / n
        q_level = min(1.0, np.ceil((n + 1) * (1.0 - alpha)) / n)
        q_val = float(np.quantile(self.cal_scores, q_level, method="higher"))

        lower = np.maximum(0.0, point_forecast - q_val)
        upper = point_forecast + q_val

        return PredictionInterval(
            nominal_level=confidence_level,
            point_forecast=point_forecast,
            lower_bound=lower,
            upper_bound=upper,
            method="conformal",
        )


def calculate_prediction_intervals(
    point_forecast: np.ndarray,
    residuals: np.ndarray,
    confidence_levels: List[float] = None,
    method: str = "bootstrap",
    cal_actuals: Optional[np.ndarray] = None,
    cal_preds: Optional[np.ndarray] = None,
) -> Dict[float, PredictionInterval]:
    """Calculate multi-level prediction intervals for a point forecast."""
    if confidence_levels is None:
        confidence_levels = [0.80, 0.95]

    results = {}
    if method == "conformal" and cal_actuals is not None and cal_preds is not None:
        cp = ConformalPredictor().fit_calibration(cal_actuals, cal_preds)
        for cl in confidence_levels:
            results[cl] = cp.predict_intervals(point_forecast, confidence_level=cl)
    elif method == "parametric":
        clean_res = residuals[~np.isnan(residuals)]
        std = float(np.std(clean_res)) if len(clean_res) > 2 else float(np.mean(point_forecast) * 0.20)
        h = len(point_forecast)
        horizon_scaling = np.sqrt(np.arange(1, h + 1))
        for cl in confidence_levels:
            z = float(stats.norm.ppf(1.0 - (1.0 - cl) / 2.0))
            margin = z * std * horizon_scaling
            results[cl] = PredictionInterval(
                nominal_level=cl,
                point_forecast=point_forecast,
                lower_bound=np.maximum(0.0, point_forecast - margin),
                upper_bound=point_forecast + margin,
                method="parametric",
            )
    else:  # default to bootstrap
        boot = ResidualBootstrapIntervals()
        for cl in confidence_levels:
            results[cl] = boot.generate(point_forecast, residuals, confidence_level=cl)

    return results
