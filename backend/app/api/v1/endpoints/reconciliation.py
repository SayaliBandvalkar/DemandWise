"""Forecast reconciliation and coherence API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.reconciliation import (
    ReconciliationRequest,
    ReconciliationResponse,
)
from backend.app.services.reconciliation_service import ReconciliationService

router = APIRouter()


@router.post("", response_model=ReconciliationResponse)
def execute_reconciliation(req: ReconciliationRequest):
    """Run Bottom-Up, Top-Down, and MinT Shrinkage reconciliation and measure coherence errors."""
    return ReconciliationService.run_reconciliation(
        base_model_name=req.base_model_name,
        horizon=req.horizon,
    )
