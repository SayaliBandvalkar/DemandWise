"""Inventory replenishment policies and optimization models.

Implements:
1. Baseline Policy: Rolling historical mean with classical normal safety stock.
2. Forecast-Driven Policy: Point forecast over lead-time + review period with residual variance buffer.
3. Uncertainty-Aware Policy: Probabilistic prediction interval quantile-driven safety stock with asymmetric lost-sales protection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import numpy as np
import scipy.stats as stats


@dataclass
class InventoryParameters:
    """Operational parameters and cost coefficients for an inventory SKU."""

    sku_id: str
    store_id: str
    unit_cost: float = 10.0
    unit_price: float = 15.0
    lead_time_days: int = 5
    review_period_days: int = 7
    target_service_level: float = 0.95
    holding_cost_daily: float = 0.03  # Holding cost per unit per day
    stockout_penalty: float = 12.50  # Penalty per lost unit (margin + goodwill)
    ordering_cost: float = 15.0  # Fixed cost per replenishment order
    min_order_quantity: float = 1.0  # MOQ

    def __post_init__(self):
        # Auto-calibrate holding cost and stockout penalty if default
        if self.unit_cost > 0 and self.holding_cost_daily == 0.03:
            # 20% annual holding cost / 365
            self.holding_cost_daily = max(0.005, (0.20 * self.unit_cost) / 365.0)
        if self.unit_price > self.unit_cost and self.stockout_penalty == 12.50:
            margin = self.unit_price - self.unit_cost
            self.stockout_penalty = max(1.0, 2.5 * margin)


@dataclass
class OrderDecision:
    """Replenishment decision generated at an inventory review point."""

    inventory_on_hand: float
    pipeline_orders: float
    inventory_position: float
    expected_ltd: float  # Expected lead-time demand
    safety_stock: float
    reorder_point: float
    order_up_to_level: float
    order_quantity: float
    order_placed: bool


class BaselineInventoryPolicy:
    """Classic (s, S) policy driven by rolling historical demand average."""

    def __init__(self, params: InventoryParameters):
        self.params = params

    def evaluate(
        self,
        current_stock: float,
        pipeline_stock: float,
        historical_demand: np.ndarray,
    ) -> OrderDecision:
        L = self.params.lead_time_days
        R = self.params.review_period_days
        alpha = self.params.target_service_level

        # Historical mean and standard deviation
        recent = historical_demand[-30:] if len(historical_demand) >= 30 else historical_demand
        mean_d = float(np.mean(recent)) if len(recent) > 0 else 5.0
        std_d = float(np.std(recent)) if len(recent) > 1 else 1.5

        # Protection interval: Lead time + Review period
        protection_days = L + R
        expected_ltd = mean_d * protection_days
        z = float(stats.norm.ppf(alpha))
        safety_stock = z * std_d * np.sqrt(protection_days)

        order_up_to = expected_ltd + safety_stock
        reorder_point = mean_d * L + z * std_d * np.sqrt(L)

        inv_position = current_stock + pipeline_stock
        order_qty = 0.0
        placed = False

        if inv_position <= reorder_point:
            raw_qty = order_up_to - inv_position
            order_qty = max(self.params.min_order_quantity, np.ceil(raw_qty))
            placed = True

        return OrderDecision(
            inventory_on_hand=current_stock,
            pipeline_orders=pipeline_stock,
            inventory_position=inv_position,
            expected_ltd=round(expected_ltd, 2),
            safety_stock=round(safety_stock, 2),
            reorder_point=round(reorder_point, 2),
            order_up_to_level=round(order_up_to, 2),
            order_quantity=float(order_qty),
            order_placed=placed,
        )


class ForecastDrivenPolicy:
    """Dynamic (s, S) policy driven by forward-looking point forecasts."""

    def __init__(self, params: InventoryParameters):
        self.params = params

    def evaluate(
        self,
        current_stock: float,
        pipeline_stock: float,
        point_forecasts: np.ndarray,
        residual_std: float,
    ) -> OrderDecision:
        L = self.params.lead_time_days
        R = self.params.review_period_days
        alpha = self.params.target_service_level
        protection_days = L + R

        # Sum expected forecast over protection horizon
        if len(point_forecasts) >= protection_days:
            expected_ltd = float(np.sum(point_forecasts[:protection_days]))
            lead_time_forecast = float(np.sum(point_forecasts[:L]))
        else:
            daily_avg = float(np.mean(point_forecasts)) if len(point_forecasts) > 0 else 5.0
            expected_ltd = daily_avg * protection_days
            lead_time_forecast = daily_avg * L

        z = float(stats.norm.ppf(alpha))
        safety_stock = z * max(0.5, residual_std) * np.sqrt(protection_days)

        order_up_to = expected_ltd + safety_stock
        reorder_point = lead_time_forecast + z * max(0.5, residual_std) * np.sqrt(L)

        inv_position = current_stock + pipeline_stock
        order_qty = 0.0
        placed = False

        if inv_position <= reorder_point:
            raw_qty = order_up_to - inv_position
            order_qty = max(self.params.min_order_quantity, np.ceil(raw_qty))
            placed = True

        return OrderDecision(
            inventory_on_hand=current_stock,
            pipeline_orders=pipeline_stock,
            inventory_position=inv_position,
            expected_ltd=round(expected_ltd, 2),
            safety_stock=round(safety_stock, 2),
            reorder_point=round(reorder_point, 2),
            order_up_to_level=round(order_up_to, 2),
            order_quantity=float(order_qty),
            order_placed=placed,
        )


class UncertaintyAwarePolicy:
    """Probabilistic prediction-interval driven policy."""

    def __init__(self, params: InventoryParameters):
        self.params = params

    def evaluate(
        self,
        current_stock: float,
        pipeline_stock: float,
        point_forecasts: np.ndarray,
        upper_interval: np.ndarray,
    ) -> OrderDecision:
        """Sizes safety stock directly from the calibrated upper prediction interval."""
        L = self.params.lead_time_days
        R = self.params.review_period_days
        protection_days = L + R

        if len(point_forecasts) >= protection_days:
            expected_mean = float(np.sum(point_forecasts[:protection_days]))
            expected_upper = float(np.sum(upper_interval[:protection_days]))
            ltd_mean = float(np.sum(point_forecasts[:L]))
            ltd_upper = float(np.sum(upper_interval[:L]))
        else:
            mean_pt = float(np.mean(point_forecasts)) if len(point_forecasts) > 0 else 5.0
            mean_up = float(np.mean(upper_interval)) if len(upper_interval) > 0 else 7.5
            expected_mean = mean_pt * protection_days
            expected_upper = mean_up * protection_days
            ltd_mean = mean_pt * L
            ltd_upper = mean_up * L

        # Safety stock derived from upper quantile spread
        safety_stock = max(1.0, expected_upper - expected_mean)
        order_up_to = expected_upper
        reorder_point = ltd_upper

        inv_position = current_stock + pipeline_stock
        order_qty = 0.0
        placed = False

        if inv_position <= reorder_point:
            raw_qty = order_up_to - inv_position
            order_qty = max(self.params.min_order_quantity, np.ceil(raw_qty))
            placed = True

        return OrderDecision(
            inventory_on_hand=current_stock,
            pipeline_orders=pipeline_stock,
            inventory_position=inv_position,
            expected_ltd=round(expected_mean, 2),
            safety_stock=round(safety_stock, 2),
            reorder_point=round(reorder_point, 2),
            order_up_to_level=round(order_up_to, 2),
            order_quantity=float(order_qty),
            order_placed=placed,
        )
