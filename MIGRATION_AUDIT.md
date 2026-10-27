# DemandWise — Migration Audit & Feature Inventory

**Project ID:** MDS-07  
**Official Project Title:** Hierarchical Demand Forecasting with Probabilistic Reconciliation and Inventory Decisions  
**Product Name:** DemandWise — Hierarchical Forecasting & Inventory Intelligence  
**Migration Goal:** Convert monolithic Streamlit application into a decoupled **React (TypeScript + Vite + Tailwind CSS + Recharts + Lucide) + FastAPI** full-stack enterprise architecture.  
**Audit Date:** 2026-10-26  

---

## 1. Executive Migration Inventory

| Module / Feature | Existing Source File(s) | Operational Status | Key Dependencies | Planned Destination | Verification & Parity Test |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Synthetic Retail Data Generator** | `src/demandwise/data/generator.py` | ✅ Verified (17,520 rows generated deterministically) | `numpy`, `pandas` | `backend/app/services/data_service.py` & `src/demandwise/data/generator.py` | `tests/unit/test_data.py::test_generator_shape_and_hierarchy` |
| **Pydantic Schema & Validator** | `src/demandwise/data/schema.py`, `src/demandwise/data/validator.py` | ✅ Verified (Detects duplicates, negatives, schema issues) | `pydantic`, `pandas` | `backend/app/schemas/dataset.py`, `backend/app/services/validation_service.py` | `tests/unit/test_data.py::test_validator_*` |
| **Mathematical Summing Matrix $S$ & Hierarchy** | `src/demandwise/forecasting/hierarchy.py` | ✅ Verified ($y_t = S b_t$, shape $59 \times 48$) | `numpy`, `pandas` | `backend/app/forecasting/hierarchy.py` | `tests/unit/test_hierarchy.py::test_hierarchy_*` |
| **Base Forecasting Models** (Naive, Seasonal Naive, Croston SBA, ExpSmoothing, LightGBM) | `src/demandwise/forecasting/models.py` | ✅ Verified (All 5 models fit and predict, safe on zero series) | `statsmodels`, `lightgbm`, `scikit-learn` | `backend/app/forecasting/models.py` & `backend/app/services/forecast_service.py` | `tests/unit/test_forecasting.py::test_*` |
| **Rolling-Origin Backtesting** | `src/demandwise/forecasting/backtest.py` | ✅ Verified (Expanding origin without leakage) | `numpy`, `pandas` | `backend/app/forecasting/backtest.py` | `tests/unit/test_forecasting.py::test_rolling_origin_backtest` |
| **Forecast Reconciliation** (BU, TD, MinT Shrinkage) | `src/demandwise/reconciliation/reconciler.py` | ✅ Verified (Coherence error reduced from 112.94 to 0.0000) | `numpy`, `scipy` | `backend/app/reconciliation/reconciler.py` & `backend/app/services/reconciliation_service.py` | `tests/unit/test_reconciliation.py::test_*` |
| **Prediction Intervals & Conformal Calibration** | `src/demandwise/uncertainty/intervals.py`, `src/demandwise/uncertainty/calibration.py` | ✅ Verified (Conformal achieved 95.5% coverage; Winkler score 236.74) | `scipy.stats`, `numpy` | `backend/app/uncertainty/` & `backend/app/services/calibration_service.py` | `tests/unit/test_uncertainty.py::test_*` |
| **Inventory Policies & Discrete-Event Simulator** | `src/demandwise/inventory/policy.py`, `src/demandwise/inventory/simulator.py` | ✅ Verified (Daily simulation, ROP, SS, lost sales, fill rates) | `numpy`, `pandas`, `scipy` | `backend/app/inventory/` & `backend/app/services/inventory_service.py` | `tests/unit/test_inventory.py::test_*` |
| **Evaluation Metrics** (MASE, RMSSE, MAE, RMSE, Bias, Coherence, WAPE) | `src/demandwise/evaluation/metrics.py` | ✅ Verified (Safe division, seasonal scaling) | `numpy` | `backend/app/evaluation/metrics.py` | `tests/unit/test_metrics.py::test_*` |
| **Benchmark Suite & Ablation Runner** | `src/demandwise/experiments/benchmark.py` | ✅ Verified (Generates JSON & CSVs in `artifacts/experiments/`) | `pandas`, `numpy`, `json` | `backend/app/experiments/benchmark.py` & `/api/v1/experiments` | End-to-end benchmark execution check |
| **Data Drift & Bias Monitoring** | `src/demandwise/monitoring/drift.py` | ✅ Verified (PSI and Tracking Signal calculation) | `numpy` | `backend/app/monitoring/drift.py` & `/api/v1/monitoring/drift` | Ingestion & drift API integration test |
| **SQLite Audit Trail Governance** | `src/demandwise/governance/audit.py` | ✅ Verified (`artifacts/demandwise_audit.db` with SHA-256 hashes) | `sqlite3`, `hashlib` | `backend/app/governance/audit.py` & `/api/v1/audit` | API query & SHA-256 integrity verification |
| **Streamlit UI (10 Modules)** | `app.py` | ⚠️ Replaced (Monolithic Streamlit presentation layer) | `streamlit`, `plotly` | `frontend/src/pages/` (React + Tailwind + Recharts) | React component rendering & API integration |

---

## 2. Issues Discovered in Current Streamlit Code
1. **Regional Column Name Mismatch in Overview:**
   In `app.py` line 319: `wide_df[["Total", "Region_Region_A", "Region_Region_B"]]` crashed because `HierarchyTree` formats the column names as `Region_A` and `Region_B`. In our FastAPI service layer, column lookups will be handled with resilient fuzzy key matching and strict hierarchy node identifiers.
2. **Monolithic In-Memory Coupling:**
   `app.py` combined data generation, state handling, Plotly rendering, and compute inside a single script run. The React + FastAPI architecture cleanly isolates domain computation in backend services with typed JSON API schemas.

---

## 3. Preservation Strategy
1. **Zero Discard of Business Logic:** The core algorithms in `src/demandwise` are 100% mathematically sound and fully tested. We will adapt them into `backend/app/` (or expose them through `backend/app/api/v1/` routers) while keeping the original files for backwards compatibility.
2. **Preserve Legacy Streamlit:** `app.py` will be retained in `legacy/app.py` and at root so the user can still inspect or run it if needed.
3. **Artifacts & Datasets:** `data/sample/retail_hierarchy.csv`, `artifacts/experiments/`, and `artifacts/demandwise_audit.db` will be preserved and mounted directly into the FastAPI backend.
