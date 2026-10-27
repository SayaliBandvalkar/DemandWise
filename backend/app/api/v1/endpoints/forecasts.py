"""Forecasting API endpoints."""

from __future__ import annotations

from typing import List
from fastapi import APIRouter

from backend.app.schemas.forecast import ForecastRequest, ForecastResponse
from backend.app.services.forecast_service import ForecastService

router = APIRouter()


@router.get("/models", response_model=List[str])
def list_available_models():
    """List supported forecasting algorithm names."""
    return ["LightGBM", "ExponentialSmoothing", "Croston_SBA", "SeasonalNaive", "Naive"]


@router.post("", response_model=ForecastResponse)
def generate_forecast(req: ForecastRequest):
    """Generate multi-step point predictions and compute test accuracy metrics."""
    res = ForecastService.generate_forecast(
        series_name=req.series_name,
        model_name=req.model_name,
        horizon=req.horizon,
        test_days=req.test_days,
    )
    return res
