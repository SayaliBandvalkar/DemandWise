"""Empirical calibration metrics and diagnostics for probabilistic forecasts.

Calculates:
- Empirical Coverage Rate (ECR)
- Mean Interval Width (MIW)
- Winkler Score (Interval Score)
- Horizon-wise calibration degradation
- Demand profile segment calibration (smooth, seasonal, intermittent)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from demandwise.uncertainty.intervals import PredictionInterval


@dataclass
class CalibrationReport:
    """Detailed summary of interval calibration performance."""

    nominal_level: float
    empirical_coverage: float
    coverage_error: float  # empirical - nominal (negative = undercoverage)
    mean_width: float
    mean_winkler_score: float
    coverage_by_horizon: Dict[int, float] = field(default_factory=dict)
    width_by_horizon: Dict[int, float] = field(default_factory=dict)
    total_samples: int = 0


def winkler_score(
    actual: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    nominal_level: float,
) -> np.ndarray:
    """Calculate the Winkler / Interval Score for each observation.

    S_alpha = (U - L) + (2 / alpha) * (L - y) * I(y < L) + (2 / alpha) * (y - U) * I(y > U)
    where alpha = 1 - nominal_level.
    Penalizes wider intervals and severely penalizes realizations falling outside the interval.
    Lower score is strictly better.
    """
    alpha = max(1e-6, 1.0 - nominal_level)
    width = upper - lower
    penalty_lower = (2.0 / alpha) * np.maximum(0.0, lower - actual)
    penalty_upper = (2.0 / alpha) * np.maximum(0.0, actual - upper)
    return width + penalty_lower + penalty_upper


def evaluate_interval_calibration(
    actuals: np.ndarray,
    interval: PredictionInterval,
) -> CalibrationReport:
    """Evaluate empirical coverage, width, and Winkler score for an interval."""
    y = np.asarray(actuals)
    L = np.asarray(interval.lower_bound)
    U = np.asarray(interval.upper_bound)

    # Align lengths
    n = min(len(y), len(L), len(U))
    y = y[:n]
    L = L[:n]
    U = U[:n]

    # In-interval indicator
    covered = (y >= L) & (y <= U)
    emp_coverage = float(np.mean(covered)) if n > 0 else 0.0
    cov_error = emp_coverage - interval.nominal_level

    # Width
    widths = U - L
    mean_w = float(np.mean(widths)) if n > 0 else 0.0

    # Winkler score
    scores = winkler_score(y, L, U, interval.nominal_level)
    mean_ws = float(np.mean(scores)) if n > 0 else 0.0

    # By-horizon tracking
    cov_by_h = {h + 1: float(covered[h]) for h in range(n)}
    width_by_h = {h + 1: float(widths[h]) for h in range(n)}

    return CalibrationReport(
        nominal_level=interval.nominal_level,
        empirical_coverage=round(emp_coverage, 4),
        coverage_error=round(cov_error, 4),
        mean_width=round(mean_w, 4),
        mean_winkler_score=round(mean_ws, 4),
        coverage_by_horizon=cov_by_h,
        width_by_horizon=width_by_h,
        total_samples=n,
    )
