"""Data drift monitoring and audit logging endpoints."""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Query

from backend.app.schemas.monitoring import AuditLogRecordResponse, DriftResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/drift", response_model=DriftResponse)
def get_data_drift(series_name: str = Query(default="Total")):
    """Compute Population Stability Index (PSI) and tracking signal bias drift."""
    return AnalyticsService.evaluate_drift(series_name=series_name)


@router.get("/audit", response_model=List[AuditLogRecordResponse])
def get_audit_trail(limit: int = Query(default=50, ge=1, le=200)):
    """Fetch immutable SQLite audit logs with SHA-256 integrity verification."""
    return AnalyticsService.get_audit_logs(limit=limit)
