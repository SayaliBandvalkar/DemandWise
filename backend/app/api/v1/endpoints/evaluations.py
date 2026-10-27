"""Evaluation metrics and benchmark results API endpoints."""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter

from backend.app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/benchmark", response_model=Dict[str, Any])
def get_benchmark_report():
    """Retrieve full master benchmark and ablation results across models and hierarchy tiers."""
    return AnalyticsService.get_benchmark_results()
