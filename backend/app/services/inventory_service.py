"""Inventory simulation service executing daily replenishment decisions."""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
import pandas as pd

from backend.app.schemas.inventory import (
    DailyInventoryStepResponse,
    InventorySimResponse,
    PolicySummaryResponse,
)
from backend.app.services.data_service import DataService, audit_logger
from demandwise.inventory.policy import InventoryParameters
from demandwise.inventory.simulator import InventorySimulator
from demandwise.uncertainty.intervals import calculate_prediction_intervals


class InventoryService:
    """Orchestrates discrete-event inventory replenishment simulations."""

    @classmethod
    def simulate_policies(
        cls,
        sku_id: str = "SKU_001",
        store_id: str = "Store_01",
        lead_time_days: int = 5,
        review_period_days: int = 7,
        target_service_level: float = 0.95,
        holding_cost_daily: float = 0.03,
        stockout_penalty: float = 12.50,
        ordering_cost: float = 15.0,
        horizon: int = 14,
    ) -> InventorySimResponse:
        tree, wide_df = DataService.get_hierarchy_tree()

        # Target bottom series identifier: e.g. "SKU_001_Store_01"
        target_series = f"{sku_id}_{store_id}"
        if target_series not in wide_df.columns:
            target_series = tree.bottom_series[0]
            parts = target_series.split("_")
            sku_id = f"{parts[0]}_{parts[1]}"
            store_id = f"{parts[2]}_{parts[3]}" if len(parts) >= 4 else "Store_01"

        actual_demand = wide_df[target_series].iloc[-horizon:].values
        dates = [d.strftime("%Y-%m-%d") for d in wide_df.index[-horizon:]]

        # Forecast points and calibrated upper bounds
        mean_dem = float(np.mean(actual_demand))
        pt_fc = np.full(horizon, max(1.0, mean_dem))
        boot_ints = calculate_prediction_intervals(
            pt_fc,
            np.array([1.5, -1.0, 2.0, -0.5]),
            [target_service_level],
        )
        upper_fc = boot_ints[target_service_level].upper_bound

        params = InventoryParameters(
            sku_id=sku_id,
            store_id=store_id,
            lead_time_days=lead_time_days,
            review_period_days=review_period_days,
            target_service_level=target_service_level,
            holding_cost_daily=holding_cost_daily,
            stockout_penalty=stockout_penalty,
            ordering_cost=ordering_cost,
        )

        sim = InventorySimulator(params)
        report = sim.compare_policies(
            actual_demand=actual_demand,
            point_forecasts=pt_fc,
            upper_intervals=upper_fc,
            dates=dates,
        )

        policy_summaries: List[PolicySummaryResponse] = []
        for pol_name, trace in report.traces.items():
            policy_summaries.append(
                PolicySummaryResponse(
                    policy=pol_name.replace("_", " ").title(),
                    total_demand=trace.total_demand,
                    fulfilled_units=trace.total_fulfilled,
                    lost_sales=trace.total_lost_sales,
                    fill_rate_pct=round(trace.fill_rate * 100.0, 2),
                    stockout_days=trace.stockout_days,
                    orders_placed=trace.num_orders_placed,
                    holding_cost=trace.total_holding_cost,
                    stockout_cost=trace.total_stockout_cost,
                    ordering_cost=trace.total_ordering_cost,
                    total_cost=trace.total_cost,
                )
            )

        # Get daily trajectory for the Uncertainty-Aware policy
        unc_trace = report.traces["uncertainty_aware"]
        daily_steps: List[DailyInventoryStepResponse] = []
        for s in unc_trace.steps:
            daily_steps.append(
                DailyInventoryStepResponse(
                    day_idx=s.day_idx,
                    date=s.date if s.date else f"Day {s.day_idx+1}",
                    starting_stock=s.starting_stock,
                    orders_arrived=s.orders_arrived,
                    actual_demand=s.actual_demand,
                    fulfilled_units=s.fulfilled_units,
                    lost_sales=s.lost_sales,
                    ending_stock=s.ending_stock,
                    pipeline_stock=s.pipeline_stock,
                    order_placed=s.order_placed,
                    order_quantity=s.order_quantity,
                    holding_cost=s.holding_cost,
                    stockout_cost=s.stockout_cost,
                    total_cost=s.total_cost,
                )
            )

        audit_logger.log_event(
            event_type="INVENTORY_RUN",
            action=f"Simulated inventory replenishment for {sku_id} at {store_id}",
            details={"lead_time": lead_time_days, "service_level": target_service_level},
        )

        return InventorySimResponse(
            sku_id=sku_id,
            store_id=store_id,
            horizon_days=horizon,
            policies_summary=policy_summaries,
            daily_trajectory=daily_steps,
        )
