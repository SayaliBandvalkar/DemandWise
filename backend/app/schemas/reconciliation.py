"""Pydantic schemas for forecast reconciliation and coherence."""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ReconciliationRequest(BaseModel):
    base_model_name: str = Field(default="lightgbm")
    horizon: int = Field(default=14, ge=7, le=28)


class ReconciliationMethodSummary(BaseModel):
    method: str
    is_coherent: bool
    max_coherence_error: float
    mean_coherence_error: float
    total_series_mae: float
    avg_bottom_mae: float
    total_wape_pct: float


class ReconciliationResponse(BaseModel):
    horizon: int
    base_model: str
    methods: List[ReconciliationMethodSummary]
    top_level_comparison: List[Dict[str, Any]]
