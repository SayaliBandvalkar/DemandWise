"""Unit tests for forecast reconciliation and coherence guarantees."""

import pytest
import numpy as np

from demandwise.forecasting.hierarchy import SummingMatrix
from demandwise.reconciliation.reconciler import (
    BottomUpReconciler,
    ForecastReconciler,
    TopDownReconciler,
    coherence_error,
)


@pytest.fixture
def simple_summing_matrix():
    # 2 bottom series (b1, b2), 1 total series (Total = b1 + b2)
    # S = [[1, 1], [1, 0], [0, 1]]
    S = np.array([[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    series_names = ["Total", "b1", "b2"]
    bottom_names = ["b1", "b2"]
    level_map = {"Total": "total", "b1": "bottom", "b2": "bottom"}
    return SummingMatrix(series_names, bottom_names, S, level_map)


def test_coherence_error_calculation(simple_summing_matrix):
    # Incoherent vector: Total=10, b1=4, b2=4 (expected Total is 8, discrepancy is 2)
    y_incoherent = np.array([10.0, 4.0, 4.0])
    max_err, mean_err = coherence_error(y_incoherent, simple_summing_matrix.matrix, k=2)
    assert max_err == 2.0


def test_bottom_up_coherence(simple_summing_matrix):
    bu = BottomUpReconciler(simple_summing_matrix)
    y_incoherent = np.array([15.0, 6.0, 4.0])  # b1=6, b2=4 -> Total should be 10
    y_reconciled = bu.reconcile(y_incoherent)

    assert y_reconciled[0] == 10.0  # Total reconciled to sum
    assert y_reconciled[1] == 6.0
    assert y_reconciled[2] == 4.0

    max_err, _ = coherence_error(y_reconciled, simple_summing_matrix.matrix, k=2)
    assert max_err < 1e-6


def test_top_down_coherence(simple_summing_matrix):
    td = TopDownReconciler(simple_summing_matrix, method="forecast_proportions")
    y_incoherent = np.array([20.0, 3.0, 7.0])  # Total=20, proportions 3:7 (30% and 70%)
    y_reconciled = td.reconcile(y_incoherent)

    assert y_reconciled[0] == 20.0
    assert y_reconciled[1] == pytest.approx(6.0)
    assert y_reconciled[2] == pytest.approx(14.0)

    max_err, _ = coherence_error(y_reconciled, simple_summing_matrix.matrix, k=2)
    assert max_err < 1e-6
