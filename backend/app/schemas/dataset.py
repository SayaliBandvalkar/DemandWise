"""Pydantic schemas for datasets and data validation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GenerateDemoRequest(BaseModel):
    num_skus: int = Field(default=12, ge=2, le=50)
    num_stores: int = Field(default=4, ge=1, le=20)
    num_regions: int = Field(default=2, ge=1, le=10)
    random_seed: int = Field(default=42)


class DatasetSummaryResponse(BaseModel):
    name: str
    file_path: str
    total_records: int
    num_skus: int
    num_stores: int
    num_categories: int
    num_regions: int
    date_min: str
    date_max: str
    zero_demand_percentage: float
    total_revenue: float
    total_units: float


class DataQualityResponse(BaseModel):
    is_valid: bool
    total_records: int
    num_skus: int
    num_stores: int
    num_categories: int
    num_regions: int
    missing_dates_count: int
    duplicate_rows_count: int
    negative_quantity_count: int
    zero_demand_percentage: float
    missing_values: Dict[str, int]
    issues: List[Dict[str, Any]]
