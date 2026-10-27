"""Pydantic schemas for hierarchy and Summing Matrix S."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel


class HierarchySummaryResponse(BaseModel):
    m_total_series: int
    k_bottom_series: int
    levels: List[str]
    regions: List[str]
    stores: List[str]
    categories: List[str]
    bottom_series: List[str]
    all_series: List[str]
    level_map: Dict[str, str]


class SummingMatrixResponse(BaseModel):
    shape: List[int]  # [m, k]
    series_names: List[str]
    bottom_names: List[str]
    # Matrix sparse representation: list of [row, col] where value is 1.0
    non_zero_coordinates: List[List[int]]
