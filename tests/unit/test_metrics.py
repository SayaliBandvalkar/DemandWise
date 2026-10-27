"""Unit tests for statistical evaluation metrics."""

import pytest
import numpy as np

from demandwise.evaluation.metrics import (
    calculate_forecast_metrics,
    calculate_mase,
    calculate_rmsse,
)


def test_basic_metrics():
    actual = np.array([10.0, 20.0, 30.0])
    pred = np.array([12.0, 18.0, 32.0])

    m = calculate_forecast_metrics(actual, pred)
    # Errors: [2, -2, 2], abs: [2, 2, 2] -> MAE = 2.0
    assert m.mae == pytest.approx(2.0)
    assert m.rmse == pytest.approx(2.0)
    # Bias: (2 - 2 + 2) / 3 = 2/3 = 0.667
    assert m.bias == pytest.approx(2.0 / 3.0)
    # WAPE: sum(abs) / sum(act) = 6 / 60 = 0.10 (10%)
    assert m.wape == pytest.approx(0.10)


def test_mase_seasonal_scaling():
    # In-sample constant differences: diff = 2.0
    in_sample = np.array([10.0, 12.0, 14.0, 16.0, 18.0, 20.0])
    actual = np.array([22.0, 24.0])
    pred = np.array([23.0, 25.0])  # abs errors = [1, 1], MAE = 1.0

    mase = calculate_mase(actual, pred, in_sample, seasonality=1)
    # Scale = mean(abs(diff)) = 2.0. MASE = 1.0 / 2.0 = 0.5
    assert mase == pytest.approx(0.5)


def test_zero_scale_fallback():
    # In-sample is completely flat (diffs are all 0)
    in_sample = np.array([10.0, 10.0, 10.0, 10.0])
    actual = np.array([10.0, 12.0])
    pred = np.array([11.0, 11.0])  # MAE = 1.0

    # Should not crash with division by zero or return Inf/NaN
    mase = calculate_mase(actual, pred, in_sample, seasonality=1)
    assert not np.isnan(mase)
    assert not np.isinf(mase)
    assert mase == pytest.approx(1.0)
