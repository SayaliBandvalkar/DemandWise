"""Pydantic schemas for probabilistic uncertainty and calibration."""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class CalibrationRequest(BaseModel):
    series_name: str = Field(default="Total")
    horizon: int = Field(default=14, ge=7, le=28)


class CalibrationMetricRow(BaseModel):
    method: str
    nominal_level: float
    empirical_coverage: float
    coverage_error: float
    mean_width: float
    winkler_score: float


class IntervalPoint(BaseModel):
    date: str
    actual: float
    point_forecast: float
    lower_80: float
    upper_80: float
    lower_95: float
    upper_95: float


class CalibrationResponse(BaseModel):
    series_name: str
    horizon: int
    summary_metrics: List[CalibrationMetricRow]
    conformal_intervals: List[IntervalPoint]
    bootstrap_intervals: List[IntervalPoint]
