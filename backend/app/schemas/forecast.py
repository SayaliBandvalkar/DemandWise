"""Pydantic schemas for forecasting requests and responses."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    series_name: str = Field(default="Total", description="Target hierarchical series name")
    model_name: str = Field(default="lightgbm", description="Forecasting algorithm")
    horizon: int = Field(default=14, ge=1, le=60)
    test_days: int = Field(default=28, ge=7, le=90)


class PointForecastPoint(BaseModel):
    date: str
    actual: Optional[float] = None
    forecast: float


class ModelAccuracyMetrics(BaseModel):
    mae: float
    rmse: float
    mase: float
    rmsse: float
    bias: float
    norm_bias_pct: float
    wape_pct: float


class ForecastResponse(BaseModel):
    series_name: str
    model_name: str
    horizon: int
    train_end_date: str
    test_start_date: str
    metrics: ModelAccuracyMetrics
    predictions: List[PointForecastPoint]
    historical_tail: List[Dict[str, Any]]
