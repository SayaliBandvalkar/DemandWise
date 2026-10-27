"""Drift detection and tracking signal monitoring for DemandWise.

Implements:
1. Population Stability Index (PSI) for demand distribution drift
2. Tracking Signal (TS) = Cumulative Forecast Error / MAD (detects bias drift)
3. Hierarchical Coherence Drift Monitoring
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class DriftReport:
    """Encapsulates data and model stability metrics."""

    series_name: str
    psi_value: float
    psi_alert_level: str  # 'STABLE' (PSI < 0.1), 'MODERATE' (0.1 <= PSI < 0.25), 'SIGNIFICANT' (>= 0.25)
    max_tracking_signal: float
    tracking_signal_alert: bool  # Triggered if |TS| > 4.0
    coherence_drift_detected: bool
    summary: str


def calculate_psi(
    baseline: np.ndarray,
    target: np.ndarray,
    num_bins: int = 10,
) -> float:
    """Calculate the Population Stability Index (PSI) between baseline and target distributions.

    PSI = sum((target_pct - baseline_pct) * ln(target_pct / baseline_pct))
    PSI < 0.1: No significant change
    0.1 <= PSI < 0.25: Moderate shift
    PSI >= 0.25: Significant distributional shift
    """
    baseline = np.asarray(baseline, dtype=float)
    target = np.asarray(target, dtype=float)

    if len(baseline) == 0 or len(target) == 0:
        return 0.0

    # Determine quantile bin edges from baseline
    quantiles = np.linspace(0, 100, num_bins + 1)
    bin_edges = np.percentile(baseline, quantiles)
    bin_edges = np.unique(bin_edges)

    if len(bin_edges) < 2:
        return 0.0

    # Ensure open outer edges
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # Compute frequencies
    base_counts, _ = np.histogram(baseline, bins=bin_edges)
    target_counts, _ = np.histogram(target, bins=bin_edges)

    # Convert to proportions with smoothing epsilon to prevent division by zero
    eps = 1e-4
    base_pct = (base_counts + eps) / (len(baseline) + eps * len(base_counts))
    target_pct = (target_counts + eps) / (len(target) + eps * len(target_counts))

    psi_elements = (target_pct - base_pct) * np.log(target_pct / base_pct)
    return float(np.sum(psi_elements))


def calculate_tracking_signal(
    actuals: np.ndarray,
    forecasts: np.ndarray,
) -> Tuple[np.ndarray, float]:
    """Calculate the cumulative Tracking Signal (TS) = CFE_t / MAD_t.

    Threshold: standard statistical quality control triggers alert if |TS| > 4.0.
    """
    actuals = np.asarray(actuals, dtype=float)
    forecasts = np.asarray(forecasts, dtype=float)

    n = min(len(actuals), len(forecasts))
    if n == 0:
        return np.array([0.0]), 0.0

    errors = actuals[:n] - forecasts[:n]
    cfe = np.cumsum(errors)
    abs_errors = np.abs(errors)
    mad = np.cumsum(abs_errors) / np.arange(1, n + 1)

    # Safe tracking signal
    ts = np.where(mad > 1e-4, cfe / mad, 0.0)
    max_abs_ts = float(np.max(np.abs(ts)))
    return ts, max_abs_ts


def monitor_coherence_drift(
    reconciled_diff: float,
    threshold: float = 1.0,
) -> bool:
    """Returns True if coherence discrepancy exceeds acceptable operational threshold."""
    return bool(reconciled_diff > threshold)
