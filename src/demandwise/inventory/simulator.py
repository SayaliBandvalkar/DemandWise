"""Discrete-event inventory simulator across time horizons.

Simulates daily inventory transitions:
- Lead-time pipeline order arrivals
- Customer demand fulfillment
- Stockouts and lost sales
- End-of-day holding cost accumulation
- Stockout penalties and order placement costs
- Fill rate / service level evaluation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from demandwise.inventory.policy import (
    BaselineInventoryPolicy,
    ForecastDrivenPolicy,
    InventoryParameters,
    OrderDecision,
    UncertaintyAwarePolicy,
)


@dataclass
class DailyInventoryStep:
    """State of an inventory item on a single simulation day."""

    day_idx: int
    date: Optional[str]
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
    order_cost: float
    total_cost: float


@dataclass
class SimulationTrace:
    """Full execution trajectory of an inventory simulation run."""

    policy_name: str
    steps: List[DailyInventoryStep]
    total_demand: float
    total_fulfilled: float
    total_lost_sales: float
    fill_rate: float
    total_holding_cost: float
    total_stockout_cost: float
    total_ordering_cost: float
    total_cost: float
    num_orders_placed: int
    stockout_days: int

    def to_dataframe(self) -> pd.DataFrame:
        """Convert daily simulation steps to DataFrame."""
        return pd.DataFrame([step.__dict__ for step in self.steps])


@dataclass
class PolicyComparisonReport:
    """Comparative evaluation across multiple inventory replenishment policies."""

    sku_id: str
    store_id: str
    horizon_days: int
    traces: Dict[str, SimulationTrace]

    def summary_table(self) -> pd.DataFrame:
        """Return a structured comparative metrics table."""
        rows = []
        for policy, trace in self.traces.items():
            rows.append(
                {
                    "Policy": policy,
                    "Total Demand": round(trace.total_demand, 1),
                    "Fulfilled Units": round(trace.total_fulfilled, 1),
                    "Lost Sales": round(trace.total_lost_sales, 1),
                    "Fill Rate (%)": round(trace.fill_rate * 100.0, 2),
                    "Stockout Days": trace.stockout_days,
                    "Orders Placed": trace.num_orders_placed,
                    "Holding Cost ($)": round(trace.total_holding_cost, 2),
                    "Stockout Cost ($)": round(trace.total_stockout_cost, 2),
                    "Ordering Cost ($)": round(trace.total_ordering_cost, 2),
                    "Total Cost ($)": round(trace.total_cost, 2),
                }
            )
        return pd.DataFrame(rows)


class InventorySimulator:
    """Executes time-stepped simulation of retail inventory operations."""

    def __init__(self, params: InventoryParameters):
        self.params = params

    def simulate(
        self,
        actual_demand: np.ndarray,
        point_forecasts: np.ndarray,
        upper_intervals: np.ndarray,
        policy_type: str = "forecast_driven",
        initial_stock: Optional[float] = None,
        dates: Optional[List[str]] = None,
    ) -> SimulationTrace:
        """Simulate inventory over test horizon using the selected policy."""
        n_days = len(actual_demand)
        L = self.params.lead_time_days
        R = self.params.review_period_days

        # Initialize policies
        baseline_pol = BaselineInventoryPolicy(self.params)
        forecast_pol = ForecastDrivenPolicy(self.params)
        uncertainty_pol = UncertaintyAwarePolicy(self.params)

        # Initial stock: default to ~10 days of average demand
        if initial_stock is None:
            avg_d = float(np.mean(actual_demand)) if len(actual_demand) > 0 else 5.0
            on_hand = avg_d * (L + 3.0)
        else:
            on_hand = float(initial_stock)

        # Pipeline orders queue: list of (arrival_day, quantity)
        pipeline_orders: List[tuple[int, float]] = []

        steps: List[DailyInventoryStep] = []
        demand_history = list(actual_demand[:max(1, min(14, len(actual_demand)))])

        total_demand = 0.0
        total_fulfilled = 0.0
        total_lost = 0.0
        total_holding = 0.0
        total_stockout = 0.0
        total_order_cost = 0.0
        orders_placed_count = 0
        stockout_days_count = 0

        for t in range(n_days):
            date_str = dates[t] if dates is not None and t < len(dates) else f"Day_{t+1}"
            starting_stock = on_hand

            # 1. Receive pipeline orders that arrive on day t
            arrived_qty = 0.0
            remaining_pipeline = []
            for arr_day, qty in pipeline_orders:
                if arr_day == t:
                    arrived_qty += qty
                else:
                    remaining_pipeline.append((arr_day, qty))
            pipeline_orders = remaining_pipeline

            on_hand += arrived_qty
            avail_stock = on_hand

            # 2. Demand fulfillment
            dem = float(actual_demand[t])
            total_demand += dem
            demand_history.append(dem)

            if avail_stock >= dem:
                fulfilled = dem
                lost = 0.0
                on_hand = avail_stock - dem
            else:
                fulfilled = avail_stock
                lost = dem - avail_stock
                on_hand = 0.0
                stockout_days_count += 1

            total_fulfilled += fulfilled
            total_lost += lost

            # 3. Calculate daily costs
            daily_holding = on_hand * self.params.holding_cost_daily
            daily_stockout = lost * self.params.stockout_penalty
            total_holding += daily_holding
            total_stockout += daily_stockout

            # 4. Replenishment policy evaluation on review days
            order_placed = False
            order_qty = 0.0
            daily_order_cost = 0.0

            pipeline_stock = sum(qty for _, qty in pipeline_orders)

            if t % R == 0:
                if policy_type == "baseline":
                    dec = baseline_pol.evaluate(on_hand, pipeline_stock, np.array(demand_history))
                elif policy_type == "uncertainty_aware":
                    rem_pts = point_forecasts[t:] if t < len(point_forecasts) else point_forecasts
                    rem_ups = upper_intervals[t:] if t < len(upper_intervals) else upper_intervals
                    dec = uncertainty_pol.evaluate(on_hand, pipeline_stock, rem_pts, rem_ups)
                else:  # 'forecast_driven'
                    rem_pts = point_forecasts[t:] if t < len(point_forecasts) else point_forecasts
                    res_std = float(np.std(actual_demand[:t] - point_forecasts[:t])) if t > 3 else 2.0
                    dec = forecast_pol.evaluate(on_hand, pipeline_stock, rem_pts, res_std)

                if dec.order_placed and dec.order_quantity > 0:
                    order_placed = True
                    order_qty = dec.order_quantity
                    pipeline_orders.append((t + L, order_qty))
                    daily_order_cost = self.params.ordering_cost
                    total_order_cost += daily_order_cost
                    orders_placed_count += 1

            daily_total = daily_holding + daily_stockout + daily_order_cost

            steps.append(
                DailyInventoryStep(
                    day_idx=t,
                    date=date_str,
                    starting_stock=round(starting_stock, 2),
                    orders_arrived=round(arrived_qty, 2),
                    actual_demand=round(dem, 2),
                    fulfilled_units=round(fulfilled, 2),
                    lost_sales=round(lost, 2),
                    ending_stock=round(on_hand, 2),
                    pipeline_stock=round(sum(q for _, q in pipeline_orders), 2),
                    order_placed=order_placed,
                    order_quantity=round(order_qty, 2),
                    holding_cost=round(daily_holding, 2),
                    stockout_cost=round(daily_stockout, 2),
                    order_cost=round(daily_order_cost, 2),
                    total_cost=round(daily_total, 2),
                )
            )

        fill_rate = total_fulfilled / max(1e-8, total_demand)
        grand_total_cost = total_holding + total_stockout + total_order_cost

        return SimulationTrace(
            policy_name=policy_type,
            steps=steps,
            total_demand=round(total_demand, 2),
            total_fulfilled=round(total_fulfilled, 2),
            total_lost_sales=round(total_lost, 2),
            fill_rate=round(fill_rate, 4),
            total_holding_cost=round(total_holding, 2),
            total_stockout_cost=round(total_stockout, 2),
            total_ordering_cost=round(total_order_cost, 2),
            total_cost=round(grand_total_cost, 2),
            num_orders_placed=orders_placed_count,
            stockout_days=stockout_days_count,
        )

    def compare_policies(
        self,
        actual_demand: np.ndarray,
        point_forecasts: np.ndarray,
        upper_intervals: np.ndarray,
        initial_stock: Optional[float] = None,
        dates: Optional[List[str]] = None,
    ) -> PolicyComparisonReport:
        """Run all three replenishment policies on the exact same trajectory and compare."""
        traces = {}
        for pol in ["baseline", "forecast_driven", "uncertainty_aware"]:
            traces[pol] = self.simulate(
                actual_demand=actual_demand,
                point_forecasts=point_forecasts,
                upper_intervals=upper_intervals,
                policy_type=pol,
                initial_stock=initial_stock,
                dates=dates,
            )

        return PolicyComparisonReport(
            sku_id=self.params.sku_id,
            store_id=self.params.store_id,
            horizon_days=len(actual_demand),
            traces=traces,
        )
