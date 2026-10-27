"""Forecasting algorithms for hierarchical retail demand.

Provides standard interfaces and implementations for:
1. Naive Forecaster
2. Seasonal Naive Forecaster (weekly seasonality m=7)
3. Croston's Method & Syntetos-Boylan Approximation (SBA) for intermittent demand
4. Statistical Exponential Smoothing (Holt-Winters / Simple Exp Smoothing)
5. Gradient Boosted Machine Forecaster (LightGBM with feature engineering and Ridge fallback)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import Ridge

# Graceful import of LightGBM
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


class BaseForecaster(ABC):
    """Abstract base class for demand forecasting models."""

    def __init__(self, name: str):
        self.name = name
        self.fitted: bool = False
        self.residuals: Optional[np.ndarray] = None
        self.last_train_timestamp: Optional[pd.Timestamp] = None

    @abstractmethod
    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> BaseForecaster:
        """Fit the forecasting model on training series y and optional features X."""
        pass

    @abstractmethod
    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> np.ndarray:
        """Generate point forecasts for the specified horizon."""
        pass

    def fit_predict(
        self, y: pd.Series, horizon: int, X: Optional[pd.DataFrame] = None, X_future: Optional[pd.DataFrame] = None
    ) -> np.ndarray:
        """Convenience method to fit and predict in one call."""
        self.fit(y, X)
        return self.predict(horizon, X_future)


class NaiveForecaster(BaseForecaster):
    """Naive Forecaster: projects the last observed non-null value forward."""

    def __init__(self):
        super().__init__("Naive")
        self.last_value: float = 0.0

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> NaiveForecaster:
        if len(y) == 0:
            self.last_value = 0.0
            self.residuals = np.array([0.0])
        else:
            y_clean = y.dropna()
            self.last_value = float(y_clean.iloc[-1]) if len(y_clean) > 0 else 0.0
            # 1-step ahead in-sample residuals: e_t = y_t - y_{t-1}
            diffs = y_clean.diff().dropna().values
            self.residuals = diffs if len(diffs) > 0 else np.array([0.0])

        self.fitted = True
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> np.ndarray:
        return np.full(horizon, max(0.0, self.last_value))


class SeasonalNaiveForecaster(BaseForecaster):
    """Seasonal Naive Forecaster: projects the value from m periods ago (default m=7)."""

    def __init__(self, seasonality: int = 7):
        super().__init__(f"SeasonalNaive_m{seasonality}")
        self.seasonality = seasonality
        self.history: Optional[np.ndarray] = None

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> SeasonalNaiveForecaster:
        y_clean = y.dropna().values
        if len(y_clean) == 0:
            self.history = np.zeros(self.seasonality)
            self.residuals = np.array([0.0])
        else:
            self.history = y_clean
            if len(y_clean) > self.seasonality:
                in_sample_pred = y_clean[:-self.seasonality]
                actuals = y_clean[self.seasonality:]
                self.residuals = actuals - in_sample_pred
            else:
                self.residuals = np.array([0.0])

        self.fitted = True
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> np.ndarray:
        if self.history is None or len(self.history) == 0:
            return np.zeros(horizon)

        m = self.seasonality
        n = len(self.history)
        preds = np.zeros(horizon)
        for h in range(horizon):
            idx = n - m + (h % m)
            if idx >= 0 and idx < n:
                preds[h] = self.history[idx]
            else:
                preds[h] = self.history[-1]
        return np.maximum(0.0, preds)


class CrostonForecaster(BaseForecaster):
    """Croston's Method & Syntetos-Boylan Approximation (SBA) for intermittent demand.

    Decomposes intermittent series into demand size z_t and inter-arrival time p_t.
    """

    def __init__(self, alpha: float = 0.1, method: str = "sba"):
        super().__init__(f"Croston_{method.upper()}")
        self.alpha = alpha
        self.method = method.lower()  # 'classic' or 'sba'
        self.forecast_rate: float = 0.0

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> CrostonForecaster:
        vals = y.dropna().values
        non_zero_idx = np.where(vals > 0)[0]

        if len(non_zero_idx) == 0:
            self.forecast_rate = 0.0
            self.residuals = np.zeros(len(vals)) if len(vals) > 0 else np.array([0.0])
            self.fitted = True
            return self

        # Initialize demand size and inter-demand intervals
        demand_sizes = vals[non_zero_idx]
        intervals = np.diff(np.insert(non_zero_idx, 0, 0))
        intervals[0] = max(1, non_zero_idx[0] + 1)

        # Exponential smoothing on sizes and intervals
        z = float(demand_sizes[0])
        p = float(intervals[0])

        for i in range(1, len(demand_sizes)):
            z = self.alpha * demand_sizes[i] + (1 - self.alpha) * z
            p = self.alpha * intervals[i] + (1 - self.alpha) * p

        # Prevent division by zero
        p = max(1.0, p)

        if self.method == "sba":
            # Syntetos-Boylan Approximation correction factor: (1 - alpha/2)
            self.forecast_rate = (1.0 - (self.alpha / 2.0)) * (z / p)
        else:
            self.forecast_rate = z / p

        # In-sample residuals
        self.residuals = vals - self.forecast_rate
        self.fitted = True
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> np.ndarray:
        return np.full(horizon, max(0.0, self.forecast_rate))


class ExponentialSmoothingForecaster(BaseForecaster):
    """Holt-Winters / Exponential Smoothing with automatic fallback."""

    def __init__(self, seasonal_periods: int = 7):
        super().__init__("ExponentialSmoothing")
        self.seasonal_periods = seasonal_periods
        self.model = None
        self.last_pred: float = 0.0

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> ExponentialSmoothingForecaster:
        y_clean = y.dropna()
        if len(y_clean) < 2 * self.seasonal_periods:
            # Insufficient history for seasonal Holt-Winters; fallback to Simple Exponential Smoothing
            try:
                fit_model = ExponentialSmoothing(
                    y_clean, trend="add", seasonal=None, initialization_method="estimated"
                ).fit()
                self.model = fit_model
                self.residuals = fit_model.resid.values
            except Exception:
                self.last_pred = float(y_clean.mean()) if len(y_clean) > 0 else 0.0
                self.residuals = (y_clean - self.last_pred).values if len(y_clean) > 0 else np.array([0.0])
        else:
            # Full Holt-Winters additive model
            try:
                fit_model = ExponentialSmoothing(
                    y_clean,
                    trend="add",
                    seasonal="add",
                    seasonal_periods=self.seasonal_periods,
                    initialization_method="estimated",
                ).fit()
                self.model = fit_model
                self.residuals = fit_model.resid.values
            except Exception:
                try:
                    fit_model = ExponentialSmoothing(y_clean, trend="add", seasonal=None).fit()
                    self.model = fit_model
                    self.residuals = fit_model.resid.values
                except Exception:
                    self.last_pred = float(y_clean.mean())
                    self.residuals = (y_clean - self.last_pred).values

        self.fitted = True
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> np.ndarray:
        if self.model is not None:
            try:
                preds = self.model.forecast(horizon).values
                return np.maximum(0.0, preds)
            except Exception:
                pass
        return np.full(horizon, max(0.0, self.last_pred))


class LightGBMForecaster(BaseForecaster):
    """Machine learning autoregressive forecaster with calendar and lag feature engineering."""

    def __init__(self, max_lags: int = 14, rolling_windows: List[int] = None):
        super().__init__("LightGBM")
        self.max_lags = max_lags
        self.rolling_windows = rolling_windows or [7, 14]
        self.model = None
        self.feature_names: List[str] = []
        self.recent_history: Optional[np.ndarray] = None
        self.use_fallback: bool = not HAS_LIGHTGBM

    def _create_features(
        self, y: pd.Series, X_exog: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Generate lag, rolling, and calendar features strictly without lookahead bias."""
        df = pd.DataFrame({"target": y})
        dates = pd.to_datetime(y.index) if isinstance(y.index, pd.DatetimeIndex) else pd.date_range("2023-01-01", periods=len(y))

        # Calendar features
        df["dayofweek"] = dates.dayofweek
        df["month"] = dates.month
        df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)

        # Lag features: y_{t-1}, y_{t-2}, ..., y_{t-max_lags}
        for lag in range(1, self.max_lags + 1):
            df[f"lag_{lag}"] = df["target"].shift(lag)

        # Rolling statistics (shifted by 1 to prevent target leakage)
        for w in self.rolling_windows:
            df[f"rolling_mean_{w}"] = df["target"].shift(1).rolling(w).mean()
            df[f"rolling_std_{w}"] = df["target"].shift(1).rolling(w).std().fillna(0.0)

        # Exogenous features if provided
        if X_exog is not None:
            for col in X_exog.columns:
                df[f"exog_{col}"] = X_exog[col].values

        # Drop rows where lag features are NaN
        df_valid = df.dropna()
        X = df_valid.drop(columns=["target"])
        y_target = df_valid["target"]
        return X, y_target

    def fit(self, y: pd.Series, X: Optional[pd.DataFrame] = None) -> LightGBMForecaster:
        y_clean = y.dropna()
        self.recent_history = y_clean.values

        if len(y_clean) <= self.max_lags + 7:
            # Fallback to mean if series is too short
            self.model = Ridge(alpha=1.0)
            self.use_fallback = True
            self.residuals = np.array([0.0])
            self.fitted = True
            return self

        X_train, y_train = self._create_features(y_clean, X)
        self.feature_names = X_train.columns.tolist()

        if HAS_LIGHTGBM and not self.use_fallback:
            try:
                lgb_params = {
                    "objective": "regression",
                    "metric": "rmse",
                    "learning_rate": 0.05,
                    "num_leaves": 15,
                    "min_child_samples": 5,
                    "verbose": -1,
                    "random_state": 42,
                    "n_estimators": 60,
                }
                self.model = lgb.LGBMRegressor(**lgb_params)
                self.model.fit(X_train, y_train)
                preds = self.model.predict(X_train)
                self.residuals = (y_train.values - preds)
            except Exception:
                self.use_fallback = True
                self.model = Ridge(alpha=1.0)
                self.model.fit(X_train, y_train)
                self.residuals = (y_train.values - self.model.predict(X_train))
        else:
            self.use_fallback = True
            self.model = Ridge(alpha=1.0)
            self.model.fit(X_train, y_train)
            self.residuals = (y_train.values - self.model.predict(X_train))

        self.fitted = True
        return self

    def predict(self, horizon: int, X_future: Optional[pd.DataFrame] = None) -> np.ndarray:
        if self.model is None or self.recent_history is None or len(self.recent_history) == 0:
            return np.zeros(horizon)

        # Autoregressive multi-step recursive forecasting
        history_buffer = list(self.recent_history)
        preds = []

        for step in range(horizon):
            feat_dict = {}
            # Lags
            for lag in range(1, self.max_lags + 1):
                feat_dict[f"lag_{lag}"] = history_buffer[-lag] if len(history_buffer) >= lag else history_buffer[-1]

            # Rolling stats
            for w in self.rolling_windows:
                recent_w = history_buffer[-w:] if len(history_buffer) >= w else history_buffer
                feat_dict[f"rolling_mean_{w}"] = float(np.mean(recent_w))
                feat_dict[f"rolling_std_{w}"] = float(np.std(recent_w))

            # Calendar features
            # Approximate date step
            feat_dict["dayofweek"] = (len(history_buffer) + step) % 7
            feat_dict["month"] = 6  # nominal mid-year
            feat_dict["is_weekend"] = 1 if feat_dict["dayofweek"] >= 5 else 0

            # Exogenous if available
            if X_future is not None and step < len(X_future):
                for col in X_future.columns:
                    feat_dict[f"exog_{col}"] = X_future.iloc[step][col]
            else:
                for f in self.feature_names:
                    if f.startswith("exog_") and f not in feat_dict:
                        feat_dict[f] = 0.0

            # Match exact feature column ordering
            row_vals = [feat_dict.get(f, 0.0) for f in self.feature_names]
            X_step = pd.DataFrame([row_vals], columns=self.feature_names)

            step_pred = float(self.model.predict(X_step)[0])
            step_pred = max(0.0, step_pred)
            preds.append(step_pred)
            history_buffer.append(step_pred)

        return np.array(preds)


def get_available_forecasters() -> Dict[str, Type[BaseForecaster]]:
    """Return dictionary of all registered forecasting models."""
    return {
        "naive": NaiveForecaster,
        "seasonal_naive": SeasonalNaiveForecaster,
        "croston": CrostonForecaster,
        "exponential_smoothing": ExponentialSmoothingForecaster,
        "lightgbm": LightGBMForecaster,
    }
