"""FastAPI REST interface for DemandWise forecasting and inventory services."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from demandwise.data.generator import DatasetConfig, RetailDataGenerator
from demandwise.data.validator import RetailDataValidator
from demandwise.forecasting.hierarchy import HierarchyTree
from demandwise.forecasting.models import get_available_forecasters
from demandwise.governance.audit import AuditLogger
from demandwise.inventory.policy import InventoryParameters
from demandwise.inventory.simulator import InventorySimulator
from demandwise.reconciliation.reconciler import ForecastReconciler

app = FastAPI(
    title="DemandWise API",
    description="Hierarchical Demand Forecasting & Inventory Intelligence Engine (Project MDS-07)",
    version="1.0.0",
)

audit_logger = AuditLogger()


class ForecastRequest(BaseModel):
    series_values: List[float]
    horizon: int = Field(default=14, ge=1, le=90)
    model_name: str = Field(default="lightgbm")


class ForecastResponse(BaseModel):
    model_name: str
    horizon: int
    forecasts: List[float]
    in_sample_residuals_std: float


class InventorySimRequest(BaseModel):
    sku_id: str = "SKU_001"
    store_id: str = "Store_01"
    demand_history: List[float]
    forecast_values: List[float]
    lead_time_days: int = 5
    review_period_days: int = 7
    target_service_level: float = 0.95


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "DemandWise Engine", "version": "1.0.0"}


@app.post("/forecast", response_model=ForecastResponse)
def generate_forecast(req: ForecastRequest):
    """Generate multi-step point forecast for a supplied univariate series."""
    forecasters = get_available_forecasters()
    model_cls = forecasters.get(req.model_name.lower())
    if not model_cls:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{req.model_name}'. Choose from: {list(forecasters.keys())}",
        )

    series = pd.Series(req.series_values)
    model = model_cls()
    model.fit(series)
    preds = model.predict(req.horizon)
    resids = model.residuals if model.residuals is not None else np.array([0.0])

    audit_logger.log_event(
        event_type="FORECAST_RUN",
        action=f"Generate {req.model_name} forecast",
        details={"horizon": req.horizon, "history_len": len(req.series_values)},
    )

    return ForecastResponse(
        model_name=model.name,
        horizon=req.horizon,
        forecasts=[round(float(p), 2) for p in preds],
        in_sample_residuals_std=round(float(np.std(resids)), 3),
    )


@app.post("/simulate-inventory")
def simulate_inventory(req: InventorySimRequest):
    """Run discrete-event replenishment simulation comparing all three policies."""
    params = InventoryParameters(
        sku_id=req.sku_id,
        store_id=req.store_id,
        lead_time_days=req.lead_time_days,
        review_period_days=req.review_period_days,
        target_service_level=req.target_service_level,
    )
    sim = InventorySimulator(params)

    actuals = np.array(req.demand_history)
    pt_fc = np.array(req.forecast_values)
    upper_fc = pt_fc * 1.35  # Approximate 95% upper bound

    report = sim.compare_policies(
        actual_demand=actuals,
        point_forecasts=pt_fc,
        upper_intervals=upper_fc,
    )

    audit_logger.log_event(
        event_type="INVENTORY_RUN",
        action="Run policy simulation",
        details={"sku": req.sku_id, "store": req.store_id, "horizon": len(actuals)},
    )

    return report.summary_table().to_dict(orient="records")


@app.get("/audit-logs")
def get_audit_logs(limit: int = Query(default=20, ge=1, le=100)):
    """Retrieve recent SQLite audit records."""
    df = audit_logger.get_recent_logs(limit=limit)
    return df.to_dict(orient="records")
