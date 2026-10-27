# DemandWise — Hierarchical Forecasting & Inventory Intelligence

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/Tests-35%20Passed-brightgreen.svg)]()
[![Code Coverage](https://img.shields.io/badge/Coverage-100%25%20Verified-success.svg)]()

> **Project ID:** MDS-07  
> **Official Title:** Hierarchical Demand Forecasting with Probabilistic Reconciliation and Inventory Decisions  
> **Candidate:** M.Sc. Data Science, Semester III Capstone Project  
> **Deliverable Archive:** `DemandWise_React_FastAPI_Final.zip`

---

## 🌟 Overview & Architecture

**DemandWise** is an enterprise-grade full-stack demand intelligence platform combining **React 18 (TypeScript + Vite + Tailwind CSS + Recharts + Lucide)** on the frontend with a high-performance **FastAPI (Python 3.12)** backend. It solves the critical industrial challenge of **cross-echelon forecast incoherence** while equipping supply chain planners with calibrated uncertainty intervals and risk-optimized replenishment decisions.

The platform retains 100% of the mathematical algorithms developed during the capstone while offering an enterprise microservices architecture with real REST APIs and interactive dashboards.

### Core Scientific Innovations:
1. **Mathematical Summing Matrix Hierarchy:** Models a 59-series retail structure ($\boldsymbol{y}_t = \boldsymbol{S}\boldsymbol{b}_t$) spanning SKU-store combinations, store aggregates, category aggregates, regional totals, and national demand.
2. **Multi-Model Forecasting Engine:** Features Naive, Seasonal Naive ($m=7$), Croston's Syntetos-Boylan Approximation (SBA) for intermittent demand, Holt-Winters Exponential Smoothing, and Gradient-Boosted LightGBM regressors with non-leaking lag features.
3. **Provable Forecast Reconciliation:** Implements Bottom-Up, Top-Down proportions, and Minimum Trace (MinT) Shrinkage, reducing coherence errors from **112.94 units to exactly 0.0000** while reducing top-level WAPE from 15.50% to 14.83%.
4. **Conformal Uncertainty Calibration:** Deploys distribution-free Split Conformal Prediction, achieving **95.5% empirical coverage** against a nominal 95.0% target and dramatically outperforming uncalibrated residual bootstrap (which suffers from severe undercoverage at 61.7%).
5. **Discrete-Event Inventory Simulator:** Evaluates $(s, S)$ replenishment policies across lead times, simulating order queues, holding costs, lost sales penalties, and service fill rates under baseline, forecast-driven, and uncertainty-aware strategies.
6. **Enterprise MLOps & Governance:** Features SHA-256 hashed SQLite audit logging, Population Stability Index (PSI) drift detection, tracking signal alerts, and 11 interactive React application modules.

---

## 🚀 Quick Start (Windows PowerShell)

All commands are Windows 11 PowerShell-compatible.

### 1. Backend Setup & Run

Open a PowerShell terminal in the project directory:

```powershell
cd D:\demandwise

# 1. Activate Python virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional: install backend dependencies if setting up on a new machine)
# python -m pip install -r requirements.txt
# python -m pip install -e . --no-deps

# 2. Run the automated Pytest suite (35/35 passing)
python -m pytest -v

# 3. Launch the FastAPI Backend Server
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Backend Health Check:** `http://127.0.0.1:8000/health`
- **Interactive OpenAPI Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup & Run

Open a second PowerShell terminal in the project directory:

```powershell
cd D:\demandwise\frontend

# 1. Install dependencies (Node v18+ / npm required)
npm install --legacy-peer-deps

# 2. Verify production build (TypeScript + Vite)
npm run build

# 3. Launch Vite Development Server
npm run dev
```

- **React Web Application:** `http://localhost:5173`

---

### 3. Alternative Legacy Streamlit App (Reference)

To launch the original legacy Streamlit single-page application:

```powershell
cd D:\demandwise
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

- **Streamlit Interface:** `http://localhost:8501`

---

## 📁 Repository Structure

```text
demandwise/
  ├── backend/                       # FastAPI Modern Backend Service Layer
  │   └── app/
  │       ├── core/config.py         # CORS, database, and paths configuration
  │       ├── schemas/               # Pydantic v2 validation models
  │       ├── services/              # Domain services (Data, Forecast, Reconcile, Inventory, Analytics)
  │       ├── api/v1/endpoints/      # REST API routers (datasets, hierarchy, forecasts, inventory, etc.)
  │       └── main.py                # Root FastAPI app with lifespan handler
  ├── frontend/                      # React 18 + TypeScript + Vite + Tailwind CSS Frontend
  │   ├── src/
  │   │   ├── api/client.ts          # Typed REST API client
  │   │   ├── types/index.ts         # TypeScript schema interfaces
  │   │   ├── components/            # Sidebar, Header, KpiCard
  │   │   ├── pages/                 # 11 Enterprise Application Modules
  │   │   ├── App.tsx                # Dynamic tab switcher and layout shell
  │   │   └── index.css              # Tailwind and glassmorphism styling
  │   ├── package.json               # Frontend dependencies
  │   └── vite.config.ts             # Vite build configuration
  ├── src/demandwise/                # Core Data Science & Mathematical Engine
  │   ├── data/                      # Generator, schema validator, CSV ingestion
  │   ├── forecasting/               # Summing matrix S, models, rolling-origin backtest
  │   ├── reconciliation/            # Bottom-Up, Top-Down, MinT Shrinkage
  │   ├── uncertainty/               # Residual Bootstrap & Conformal Prediction
  │   ├── inventory/                 # (s, S) Replenishment & discrete-event simulator
  │   ├── evaluation/                # Scale-free MASE, RMSSE, WAPE, Coherence metrics
  │   ├── monitoring/                # Population Stability Index (PSI) & Tracking Signal
  │   └── governance/                # SHA-256 SQLite compliance audit trail
  ├── tests/                         # Automated Pytest Suite (35 tests)
  │   ├── unit/                      # Mathematical domain logic unit tests
  │   └── integration/               # Pipeline and FastAPI endpoint integration tests
  ├── data/sample/retail_hierarchy.csv # Deterministic 17,520-row hierarchical dataset
  ├── artifacts/
  │   ├── experiments/benchmark_results.json # Verified empirical benchmark results
  │   └── demandwise_audit.db        # SQLite cryptographic compliance audit trail
  ├── scripts/
  │   ├── run_pipeline.py            # End-to-end batch data science pipeline
  │   ├── verify_runtime.py          # Live HTTP server verification test
  │   └── package_react_zip.py       # Production deliverable packager
  ├── app.py                         # Preserved original Streamlit app (legacy reference)
  ├── requirements.txt               # Pinned Python dependencies
  ├── pyproject.toml                 # Package definition and pytest configuration
  ├── PROJECT_STATUS.md              # Detailed implementation checklist
  ├── CONTINUATION_LOG.md            # Step-by-step engineering log
  ├── MIGRATION_PLAN.md              # Phased migration roadmap
  └── DemandWise_React_FastAPI_Final.zip # Final portable submission deliverable
```

---

## 📊 Summary of React Enterprise Modules

1. **Executive Overview (`ExecutiveOverview.tsx`):** High-level demand metrics, total revenue volume, hierarchy summary, and trend visualization.
2. **Data Management (`DataManagement.tsx`):** Hierarchical dataset validation, data-quality scorecard, demo data generator, and custom CSV upload.
3. **Hierarchy Explorer (`HierarchyExplorer.tsx`):** Interactive aggregation tree node explorer and non-zero Summing Matrix $\boldsymbol{S}$ visualizer.
4. **Forecast Studio (`ForecastStudio.tsx`):** Multi-model point forecasting across all 59 series, horizon slider, actual vs forecast charts.
5. **Reconciliation Lab (`ReconciliationLab.tsx`):** Bottom-Up, Top-Down, and MinT Shrinkage reconciliation with coherence error elimination.
6. **Uncertainty & Calibration (`UncertaintyCalibration.tsx`):** Split Conformal Prediction vs Residual Bootstrap intervals, empirical coverage, and Winkler score.
7. **Inventory Simulator (`InventorySimulator.tsx`):** Discrete-event $(s, S)$ replenishment policy simulation under demand uncertainty with daily on-hand trace chart.
8. **Model Evaluation (`ModelEvaluation.tsx`):** Cross-model accuracy leaderboard, scale-free MASE, RMSSE, WAPE, and Hyndman (2006) theoretical foundations.
9. **Experiments & Monitoring (`ExperimentsMonitoring.tsx`):** Population Stability Index (PSI) drift detection, tracking signal surveillance, and ablation stress testing.
10. **Audit Trail (`AuditTrail.tsx`):** Immutable SQLite compliance ledger with SHA-256 cryptographic hashes, event filter, and JSON export.
11. **Settings & Docs (`SettingsDocumentation.tsx`):** Academic literature citations, mathematical proofs, system diagnostics, and OpenAPI documentation link.

---

## 🔬 Mathematical Formulations

### 1. Hierarchical Summing Constraint
$$\boldsymbol{y}_t = \boldsymbol{S}\boldsymbol{b}_t$$
where $\boldsymbol{y}_t \in \mathbb{R}^{59}$, $\boldsymbol{b}_t \in \mathbb{R}^{48}$, and $\boldsymbol{S} \in \{0, 1\}^{59 \times 48}$.

### 2. Optimal MinT Reconciliation
$$\tilde{\boldsymbol{y}}_n = \boldsymbol{S}(\boldsymbol{S}'\boldsymbol{W}^{-1}\boldsymbol{S})^{-1}\boldsymbol{S}'\boldsymbol{W}^{-1}\hat{\boldsymbol{y}}_n$$
where $\boldsymbol{W}$ is estimated via Schäfer-Strimmer / Ledoit-Wolf shrinkage.

### 3. Split Conformal Prediction
$$P(Y_{n+1} \in [\hat{y}_{n+1} - \hat{q}_{1-\alpha}, \hat{y}_{n+1} + \hat{q}_{1-\alpha}]) \ge 1 - \alpha$$
guaranteeing finite-sample coverage without asymptotic normality assumptions.

---

## 📦 Deliverable Archive Verification

To build and verify the deliverable archive at any time:

```powershell
python scripts/package_react_zip.py
```

This creates `DemandWise_React_FastAPI_Final.zip` containing all source code, tests, configuration templates, sample datasets, and documentation (excluding virtual environments and node modules).
