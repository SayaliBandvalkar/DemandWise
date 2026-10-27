"""Unit tests for forecasting algorithms and rolling backtesting."""

import pytest
import numpy as np
import pandas as pd

from demandwise.forecasting.models import (
    CrostonForecaster,
    ExponentialSmoothingForecaster,
    LightGBMForecaster,
    NaiveForecaster,
    SeasonalNaiveForecaster,
)
from demandwise.forecasting.backtest import RollingOriginBacktest


@pytest.fixture
def standard_series():
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    vals = 10.0 + np.sin(np.arange(60) * (2 * np.pi / 7)) * 4.0 + np.random.normal(0, 0.5, 60)
    return pd.Series(vals, index=dates, name="test_series")


@pytest.fixture
def zero_inflated_series():
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    vals = np.zeros(50)
    vals[[5, 12, 19, 28, 40]] = [4.0, 7.0, 3.0, 8.0, 5.0]
    return pd.Series(vals, index=dates, name="intermittent_series")


def test_naive_forecaster(standard_series):
    model = NaiveForecaster()
    model.fit(standard_series)
    preds = model.predict(horizon=7)
    assert len(preds) == 7
    assert np.all(preds == standard_series.iloc[-1])


def test_seasonal_naive_forecaster(standard_series):
    model = SeasonalNaiveForecaster(seasonality=7)
    model.fit(standard_series)
    preds = model.predict(horizon=7)
    assert len(preds) == 7
    np.testing.assert_allclose(preds, standard_series.values[-7:])


def test_croston_sba(zero_inflated_series):
    model = CrostonForecaster(method="sba")
    model.fit(zero_inflated_series)
    preds = model.predict(horizon=14)
    assert len(preds) == 14
    assert np.all(preds > 0.0)
    assert model.forecast_rate > 0.0


def test_all_zero_series_safety():
    """Verify that an all-zero series does not cause division by zero or crashes."""
    dates = pd.date_range("2023-01-01", periods=30, freq="D")
    zeros = pd.Series(np.zeros(30), index=dates)

    for cls in [NaiveForecaster, SeasonalNaiveForecaster, CrostonForecaster, LightGBMForecaster]:
        m = cls()
        m.fit(zeros)
        preds = m.predict(7)
        assert len(preds) == 7
        assert np.all(preds >= 0.0)


def test_rolling_origin_backtest(standard_series):
    backtest = RollingOriginBacktest(horizon=7, num_origins=2, step_size=7)
    res = backtest.run(standard_series, NaiveForecaster)
    assert len(res.windows) == 2
    assert len(res.actuals) == 2
    assert len(res.forecasts) == 2
    assert len(res.forecasts[0]) == 7
