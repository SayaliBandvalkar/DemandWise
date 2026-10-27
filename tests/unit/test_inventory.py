"""Unit tests for inventory replenishment policies and simulation."""

import pytest
import numpy as np

from demandwise.inventory.policy import (
    BaselineInventoryPolicy,
    ForecastDrivenPolicy,
    InventoryParameters,
    UncertaintyAwarePolicy,
)
from demandwise.inventory.simulator import InventorySimulator


def test_inventory_parameters():
    params = InventoryParameters(
        sku_id="SKU_001",
        store_id="Store_01",
        unit_cost=10.0,
        unit_price=20.0,
        lead_time_days=4,
    )
    assert params.lead_time_days == 4
    # Stockout penalty is 2.5 * margin (2.5 * 10 = 25.0)
    assert params.stockout_penalty == pytest.approx(25.0)


def test_baseline_policy_order_trigger():
    params = InventoryParameters(sku_id="SKU_001", store_id="Store_01", min_order_quantity=5.0)
    policy = BaselineInventoryPolicy(params)

    # When on-hand stock is low (e.g. 2 units), order should be placed
    hist_demand = np.array([10.0] * 30)
    decision = policy.evaluate(current_stock=2.0, pipeline_stock=0.0, historical_demand=hist_demand)
    assert decision.order_placed is True
    assert decision.order_quantity >= 5.0

    # When on-hand stock is high (e.g. 500 units), no order should be placed
    decision_high = policy.evaluate(current_stock=500.0, pipeline_stock=0.0, historical_demand=hist_demand)
    assert decision_high.order_placed is False
    assert decision_high.order_quantity == 0.0


def test_simulator_execution():
    params = InventoryParameters(
        sku_id="SKU_001",
        store_id="Store_01",
        lead_time_days=3,
        review_period_days=5,
    )
    sim = InventorySimulator(params)

    demand = np.array([5.0, 6.0, 7.0, 8.0, 5.0, 6.0, 7.0, 8.0, 6.0, 5.0])
    pt_fc = np.array([6.0] * 10)
    up_fc = np.array([9.0] * 10)

    trace = sim.simulate(
        actual_demand=demand,
        point_forecasts=pt_fc,
        upper_intervals=up_fc,
        policy_type="forecast_driven",
        initial_stock=20.0,
    )

    assert len(trace.steps) == 10
    assert trace.total_demand == pytest.approx(float(np.sum(demand)))
    assert 0.0 <= trace.fill_rate <= 1.0
    assert trace.total_cost >= 0.0
