"""Master API v1 router mounting all functional domain endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    datasets,
    evaluations,
    forecasts,
    hierarchy,
    inventory,
    monitoring,
    reconciliation,
    uncertainty,
)

api_router = APIRouter()

api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets & Data Quality"])
api_router.include_router(hierarchy.router, prefix="/hierarchy", tags=["Hierarchy & Summing Matrix"])
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["Forecasting Studio"])
api_router.include_router(reconciliation.router, prefix="/reconciliation", tags=["Forecast Reconciliation"])
api_router.include_router(uncertainty.router, prefix="/calibration", tags=["Uncertainty & Calibration"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory Decision Simulator"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Model Evaluation & Benchmarks"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring, Drift & Audit"])
