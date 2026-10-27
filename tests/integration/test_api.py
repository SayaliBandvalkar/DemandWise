"""Integration tests for DemandWise FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "/docs"


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "DemandWise" in data["service"]


def test_dataset_summary_endpoint():
    resp = client.get("/api/v1/datasets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] > 0
    assert data["num_skus"] >= 4
    assert data["num_stores"] >= 2


def test_dataset_quality_endpoint():
    resp = client.get("/api/v1/datasets/quality")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["negative_quantity_count"] == 0


def test_hierarchy_endpoints():
    resp = client.get("/api/v1/hierarchy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["m_total_series"] >= 17
    assert data["k_bottom_series"] >= 8

    # Summing matrix
    sm_resp = client.get("/api/v1/hierarchy/summing-matrix")
    assert sm_resp.status_code == 200
    sm_data = sm_resp.json()
    assert len(sm_data["shape"]) == 2
    assert len(sm_data["non_zero_coordinates"]) > 0


def test_forecast_endpoint():
    payload = {
        "series_name": "Total",
        "model_name": "naive",
        "horizon": 7,
        "test_days": 14,
    }
    resp = client.post("/api/v1/forecasts", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["series_name"] == "Total"
    assert data["horizon"] == 7
    assert len(data["predictions"]) == 7
    assert data["metrics"]["mae"] >= 0.0


def test_inventory_simulation_endpoint():
    payload = {
        "sku_id": "SKU_001",
        "store_id": "Store_01",
        "lead_time_days": 3,
        "review_period_days": 5,
        "target_service_level": 0.95,
    }
    resp = client.post("/api/v1/inventory/simulations", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["policies_summary"]) == 3
    assert len(data["daily_trajectory"]) > 0


def test_drift_and_audit_endpoints():
    drift_resp = client.get("/api/v1/monitoring/drift?series_name=Total")
    assert drift_resp.status_code == 200
    assert "psi_value" in drift_resp.json()

    audit_resp = client.get("/api/v1/monitoring/audit?limit=10")
    assert audit_resp.status_code == 200
    assert isinstance(audit_resp.json(), list)


def test_reconciliation_endpoint():
    payload = {
        "base_model_name": "naive",
        "horizon": 7,
    }
    resp = client.post("/api/v1/reconciliation", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["methods"]) >= 3
    # Check bottom_up coherence
    bu = next((m for m in data["methods"] if m["method"] == "bottom_up"), None)
    assert bu is not None
    assert bu["is_coherent"] is True


def test_calibration_endpoint():
    payload = {
        "series_name": "Total",
        "horizon": 7,
    }
    resp = client.post("/api/v1/calibration/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["summary_metrics"]) >= 2
    assert len(data["conformal_intervals"]) == 7


def test_benchmark_endpoint():
    resp = client.get("/api/v1/evaluations/benchmark")
    assert resp.status_code == 200
    data = resp.json()
    assert "models_benchmark" in data
    assert len(data["models_benchmark"]) >= 4

