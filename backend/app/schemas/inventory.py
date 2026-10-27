"""Pydantic schemas for inventory simulation and replenishment policies."""

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class InventorySimRequest(BaseModel):
    sku_id: str = Field(default="SKU_001")
    store_id: str = Field(default="Store_01")
    lead_time_days: int = Field(default=5, ge=1, le=21)
    review_period_days: int = Field(default=7, ge=1, le=14)
    target_service_level: float = Field(default=0.95, ge=0.80, le=0.99)
    holding_cost_daily: float = Field(default=0.03, ge=0.001, le=1.0)
    stockout_penalty: float = Field(default=12.50, ge=1.0, le=100.0)
    ordering_cost: float = Field(default=15.0, ge=0.0, le=200.0)


class DailyInventoryStepResponse(BaseModel):
    day_idx: int
    date: str
    starting_stock: float
    orders_arrived: float
    actual_demand: float
    fulfilled_units: float
    lost_sales: float
    ending_stock: float
    pipeline_stock: float
    order_placed: bool
    order_quantity: float
    holding_cost: float
    stockout_cost: float
    total_cost: float


class PolicySummaryResponse(BaseModel):
    policy: str
    total_demand: float
    fulfilled_units: float
    lost_sales: float
    fill_rate_pct: float
    stockout_days: int
    orders_placed: int
    holding_cost: float
    stockout_cost: float
    ordering_cost: float
    total_cost: float


class InventorySimResponse(BaseModel):
    sku_id: str
    store_id: str
    horizon_days: int
    policies_summary: List[PolicySummaryResponse]
    daily_trajectory: List[DailyInventoryStepResponse]
