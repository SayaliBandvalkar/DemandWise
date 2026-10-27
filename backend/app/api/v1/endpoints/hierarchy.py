"""Hierarchy and Summing Matrix S API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter

from backend.app.schemas.hierarchy import (
    HierarchySummaryResponse,
    SummingMatrixResponse,
)
from backend.app.services.data_service import DataService

router = APIRouter()


@router.get("", response_model=HierarchySummaryResponse)
def get_hierarchy_summary():
    """Retrieve the multi-echelon hierarchy topology."""
    tree, _ = DataService.get_hierarchy_tree()

    return HierarchySummaryResponse(
        m_total_series=tree.m,
        k_bottom_series=tree.k,
        levels=["Total", "Region", "Store", "Category", "Bottom (SKU x Store)"],
        regions=tree.regions,
        stores=tree.stores,
        categories=tree.categories,
        bottom_series=tree.bottom_series,
        all_series=tree.all_series,
        level_map=tree.level_map,
    )


@router.get("/summing-matrix", response_model=SummingMatrixResponse)
def get_summing_matrix():
    """Retrieve structural Summing Matrix S dimensions and non-zero coordinate representation."""
    tree, _ = DataService.get_hierarchy_tree()
    S = tree.summing_matrix.matrix

    # Find non-zero coordinates: list of [row, col]
    rows, cols = S.nonzero()
    coords = [[int(r), int(c)] for r, c in zip(rows, cols)]

    return SummingMatrixResponse(
        shape=[int(S.shape[0]), int(S.shape[1])],
        series_names=tree.all_series,
        bottom_names=tree.bottom_series,
        non_zero_coordinates=coords,
    )
