"""Pydantic schemas for monitoring, drift detection, and audit logging."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DriftResponse(BaseModel):
    series_name: str
    psi_value: float
    psi_alert_level: str  # 'STABLE', 'MODERATE', 'SIGNIFICANT'
    max_tracking_signal: float
    tracking_signal_alert: bool
    summary: str


class AuditLogRecordResponse(BaseModel):
    id: int
    timestamp: str
    event_type: str
    action: str
    status: str
    actor: str
    details: Dict[str, Any]
    record_hash: str
