"""Integration test verifying end-to-end DemandWise pipeline flow."""

import os
import pytest
import numpy as np

from demandwise.data.generator import DatasetConfig, RetailDataGenerator
from demandwise.data.validator import RetailDataValidator
from demandwise.forecasting.hierarchy import HierarchyTree
from demandwise.forecasting.models import LightGBMForecaster
from demandwise.governance.audit import AuditLogger
from demandwise.inventory.policy import InventoryParameters
from demandwise.inventory.simulator import InventorySimulator
from demandwise.reconciliation.reconciler import ForecastReconciler
from demandwise.uncertainty.intervals import calculate_prediction_intervals


def test_full_pipeline_execution(tmp_path):
    """End-to-end pipeline test across all modules."""
    # 1. Generate small dataset
    cfg = DatasetConfig(
        start_date="2023-01-01",
        end_date="2023-02-15",
        num_skus=3,
        num_stores=2,
        num_regions=2,
        random_seed=42,
    )
    gen = RetailDataGenerator(cfg)
    df = gen.generate()

    # 2. Validate
    validator = RetailDataValidator()
    val_res = validator.validate(df)
    assert val_res.is_valid is True

    # 3. Hierarchy & Summing Matrix
    tree = HierarchyTree(df)
    wide_df = tree.aggregate_time_series(df)
    assert len(wide_df.columns) == tree.m

    # 4. Fit forecaster on bottom series
    horizon = 7
    bottom_name = tree.bottom_series[0]
    train_series = wide_df[bottom_name].iloc[:-horizon]
    test_actuals = wide_df[bottom_name].iloc[-horizon:].values

    model = LightGBMForecaster()
    model.fit(train_series)
    pt_forecast = model.predict(horizon)
    assert len(pt_forecast) == horizon

    # 5. Prediction intervals
    intervals = calculate_prediction_intervals(
        point_forecast=pt_forecast,
        residuals=model.residuals if model.residuals is not None else np.array([1.0]),
        confidence_levels=[0.95],
    )
    assert 0.95 in intervals
    upper_bounds = intervals[0.95].upper_bound

    # 6. Inventory simulation
    params = InventoryParameters(
        sku_id=bottom_name.split("_")[0] + "_" + bottom_name.split("_")[1],
        store_id="Store_01",
        lead_time_days=3,
    )
    sim = InventorySimulator(params)
    trace = sim.simulate(
        actual_demand=test_actuals,
        point_forecasts=pt_forecast,
        upper_intervals=upper_bounds,
    )
    assert trace.fill_rate >= 0.0

    # 7. Audit logging to temporary DB
    db_file = str(tmp_path / "test_audit.db")
    logger = AuditLogger(db_path=db_file)
    rec = logger.log_event("PIPELINE_TEST", "Integration test completed", {"status": "OK"})
    assert rec.status == "SUCCESS"
    logs = logger.get_recent_logs(limit=5)
    assert len(logs) == 1
