"""Inventory decision simulation API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas.inventory import InventorySimRequest, InventorySimResponse
from backend.app.services.inventory_service import InventoryService

router = APIRouter()


@router.post("/simulations", response_model=InventorySimResponse)
def simulate_inventory_policies(req: InventorySimRequest):
    """Run discrete-event simulation comparing Baseline vs Forecast-Driven vs Uncertainty-Aware policies."""
    return InventoryService.simulate_policies(
        sku_id=req.sku_id,
        store_id=req.store_id,
        lead_time_days=req.lead_time_days,
        review_period_days=req.review_period_days,
        target_service_level=req.target_service_level,
        holding_cost_daily=req.holding_cost_daily,
        stockout_penalty=req.stockout_penalty,
        ordering_cost=req.ordering_cost,
    )
