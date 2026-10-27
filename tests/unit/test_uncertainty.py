"""Unit tests for prediction intervals, conformal prediction, and calibration."""

import pytest
import numpy as np

from demandwise.uncertainty.intervals import (
    ConformalPredictor,
    ResidualBootstrapIntervals,
    calculate_prediction_intervals,
)
from demandwise.uncertainty.calibration import evaluate_interval_calibration, winkler_score


def test_residual_bootstrap_bounds():
    pt = np.array([10.0, 12.0, 15.0])
    resids = np.array([-1.0, 0.5, 1.2, -0.8, 2.0, -1.5])
    boot = ResidualBootstrapIntervals(n_bootstraps=500, random_seed=42)
    interval = boot.generate(pt, resids, confidence_level=0.95)

    assert len(interval.lower_bound) == 3
    assert len(interval.upper_bound) == 3
    assert np.all(interval.lower_bound <= interval.upper_bound)
    assert np.all(interval.lower_bound >= 0.0)


def test_conformal_prediction():
    y_cal = np.array([10.0, 15.0, 20.0, 25.0])
    y_hat_cal = np.array([9.5, 14.8, 21.0, 24.2])
    cp = ConformalPredictor().fit_calibration(y_cal, y_hat_cal)

    pt = np.array([12.0, 18.0])
    interval = cp.predict_intervals(pt, confidence_level=0.90)

    assert len(interval.lower_bound) == 2
    assert np.all(interval.lower_bound <= interval.upper_bound)


def test_winkler_score_properties():
    # If actual is inside [L, U], score equals U - L
    actual = np.array([10.0])
    L = np.array([8.0])
    U = np.array([12.0])
    score = winkler_score(actual, L, U, nominal_level=0.90)
    assert score[0] == pytest.approx(4.0)

    # If actual is below L (say actual = 6), penalty applies: (U-L) + (2/0.1)*(8 - 6) = 4 + 40 = 44
    actual_low = np.array([6.0])
    score_low = winkler_score(actual_low, L, U, nominal_level=0.90)
    assert score_low[0] == pytest.approx(44.0)


def test_calibration_report():
    actuals = np.array([10.0, 12.0, 14.0, 16.0])
    intervals = calculate_prediction_intervals(
        point_forecast=actuals,
        residuals=np.array([0.5, -0.5, 0.8, -0.8]),
        confidence_levels=[0.95],
    )
    rep = evaluate_interval_calibration(actuals, intervals[0.95])
    assert rep.empirical_coverage == 1.0
    assert rep.coverage_error >= 0.0
