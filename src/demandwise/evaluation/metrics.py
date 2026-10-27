"""Statistical and operational evaluation metrics for hierarchical forecasting.

Implements:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MASE (Mean Absolute Scaled Error, Hyndman & Koehler 2006)
- RMSSE (Root Mean Squared Scaled Error, Makridakis et al. M5 Competition)
- Forecast Bias and Normalized Percentage Bias
- Absolute and Relative Coherence Error
- Winkler / Interval Score
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np


@dataclass
class ForecastMetrics:
    """Comprehensive statistical accuracy and operational metrics."""

    mae: float
    rmse: float
    mase: float
    rmsse: float
    bias: float
    percentage_bias: float
    wape: float  # Weighted Absolute Percentage Error: sum(|y - y_hat|) / sum(y)

    def to_dict(self) -> Dict[str, float]:
        return {
            "MAE": round(self.mae, 3),
            "RMSE": round(self.rmse, 3),
            "MASE": round(self.mase, 3),
            "RMSSE": round(self.rmsse, 3),
            "Bias": round(self.bias, 3),
            "NormBias (%)": round(self.percentage_bias, 2),
            "WAPE (%)": round(self.wape * 100.0, 2),
        }


def calculate_mase(
    actual: np.ndarray,
    predicted: np.ndarray,
    in_sample_history: np.ndarray,
    seasonality: int = 1,
) -> float:
    """Calculate Mean Absolute Scaled Error (MASE).

    Scale is computed from in-sample naive (or seasonal naive) differences.
    Safe against zero-denominators for flat/constant series.
    """
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    in_sample = np.asarray(in_sample_history)

    if len(in_sample) <= seasonality:
        # Fallback to MAE if in-sample history is too short to compute scale
        return float(np.mean(np.abs(actual - predicted)))

    # In-sample naive difference scale
    diffs = np.abs(in_sample[seasonality:] - in_sample[:-seasonality])
    scale = float(np.mean(diffs))

    if scale < 1e-6:
        # Scale is zero (constant history); return MAE directly to avoid inf/nan
        return float(np.mean(np.abs(actual - predicted)))

    mae = float(np.mean(np.abs(actual - predicted)))
    return mae / scale


def calculate_rmsse(
    actual: np.ndarray,
    predicted: np.ndarray,
    in_sample_history: np.ndarray,
    seasonality: int = 1,
) -> float:
    """Calculate Root Mean Squared Scaled Error (RMSSE)."""
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    in_sample = np.asarray(in_sample_history)

    if len(in_sample) <= seasonality:
        return float(np.sqrt(np.mean((actual - predicted) ** 2)))

    sq_diffs = (in_sample[seasonality:] - in_sample[:-seasonality]) ** 2
    scale_sq = float(np.mean(sq_diffs))

    if scale_sq < 1e-6:
        return float(np.sqrt(np.mean((actual - predicted) ** 2)))

    mse = float(np.mean((actual - predicted) ** 2))
    return float(np.sqrt(mse / scale_sq))


def calculate_forecast_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
    in_sample_history: Optional[np.ndarray] = None,
    seasonality: int = 7,
) -> ForecastMetrics:
    """Calculate the full suite of forecast accuracy metrics."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    n = min(len(actual), len(predicted))
    act = actual[:n]
    pred = predicted[:n]

    errors = pred - act
    abs_errors = np.abs(errors)

    mae = float(np.mean(abs_errors)) if n > 0 else 0.0
    rmse = float(np.sqrt(np.mean(errors ** 2))) if n > 0 else 0.0
    bias = float(np.mean(errors)) if n > 0 else 0.0

    sum_act = float(np.sum(act))
    pct_bias = (bias / (sum_act / max(1, n)) * 100.0) if sum_act > 1e-6 else 0.0
    wape = float(np.sum(abs_errors) / max(1e-6, sum_act))

    if in_sample_history is not None and len(in_sample_history) > seasonality:
        mase = calculate_mase(act, pred, in_sample_history, seasonality)
        rmsse = calculate_rmsse(act, pred, in_sample_history, seasonality)
    else:
        mase = mae
        rmsse = rmse

    return ForecastMetrics(
        mae=mae,
        rmse=rmse,
        mase=mase,
        rmsse=rmsse,
        bias=bias,
        percentage_bias=pct_bias,
        wape=wape,
    )


def calculate_coherence_metrics(
    y: np.ndarray,
    S: np.ndarray,
    k: int,
) -> Dict[str, float]:
    """Calculate maximum, mean, and relative coherence errors across hierarchy.

    Relative coherence error is normalized by average top-level demand.
    """
    if y.ndim == 1:
        y_vec = y[:, np.newaxis]
    else:
        y_vec = y

    b_vec = y_vec[-k:, :]
    expected_y = S @ b_vec
    diff = np.abs(y_vec - expected_y)

    max_err = float(np.max(diff))
    mean_err = float(np.mean(diff))
    top_demand = max(1.0, float(np.mean(y_vec[0, :])))
    rel_err_pct = (mean_err / top_demand) * 100.0

    return {
        "max_coherence_error": round(max_err, 5),
        "mean_coherence_error": round(mean_err, 5),
        "relative_coherence_error_pct": round(rel_err_pct, 4),
        "is_coherent": max_err < 1e-4,
    }
