"""Probabilistic uncertainty and interval calibration API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.uncertainty import CalibrationRequest, CalibrationResponse
from backend.app.services.calibration_service import CalibrationService

router = APIRouter()


@router.post("/evaluate", response_model=CalibrationResponse)
def evaluate_intervals(req: CalibrationRequest):
    """Compute Prediction Intervals (Conformal vs Bootstrap) and evaluate empirical coverage and Winkler scores."""
    return CalibrationService.evaluate_calibration(
        series_name=req.series_name,
        horizon=req.horizon,
    )
