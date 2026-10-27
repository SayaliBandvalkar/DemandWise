# DemandWise — React + FastAPI Migration Plan

## 1. Migration Goals & Target Architecture
Migrate the Streamlit single-page application into an enterprise-grade decoupled full-stack application:
- **Backend:** FastAPI (Python 3.12) with Pydantic v2 schemas, REST endpoints under `/api/v1`, CORS for local frontend, structured logging, SQLite audit persistence, and direct integration with existing forecasting/inventory engines.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React icons, Recharts for interactive charts, responsive desktop & mobile layouts.
- **Color Palette:** Navy/Deep Blue (`#07101E`, `#0A192F`, `#0F2744`) with vibrant Cyan (`#00E5FF`, `#00B4D8`) and Emerald Green accents.

---

## 2. Phased Migration Execution Tracking

### Phase 1: Audit & Preservation (Completed)
- [x] Full code audit of existing `src/demandwise` and `app.py`.
- [x] Verified initial 25/25 automated tests pass.
- [x] Created `DemandWise_Streamlit_Backup.zip` backup archive.
- [x] Documented architectural baseline in `MIGRATION_AUDIT.md`.

### Phase 2: Backend Architecture & REST API Service Layer (Completed)
- [x] Structured `backend/` directory with clean separation of concerns:
  - `backend/app/core/config.py`: Central settings with CORS origins and database paths.
  - `backend/app/schemas/`: Pydantic models for datasets, hierarchy, forecasts, reconciliation, uncertainty, inventory, monitoring.
  - `backend/app/services/`:
    - `data_service.py` (dataset loading, generation, validation, hierarchy access)
    - `forecast_service.py` (point forecasters, backtest, MASE/WAPE metrics)
    - `reconciliation_service.py` (BU, TD, MinT Shrinkage, coherence validation)
    - `calibration_service.py` (Conformal Prediction vs Residual Bootstrap, Winkler score)
    - `inventory_service.py` (discrete-event $(s, S)$ inventory simulator across 3 policies)
    - `analytics_service.py` (benchmarks, drift detection, SQLite audit logs)
  - `backend/app/api/v1/endpoints/`:
    - `datasets.py` (`/datasets`, `/upload`, `/generate-demo`, `/quality`)
    - `hierarchy.py` (`/hierarchy`, summing matrix $S$, aggregation tree)
    - `forecasts.py` (`/forecasts`, `/models`)
    - `reconciliation.py` (`/reconciliation`)
    - `uncertainty.py` (`/calibration/evaluate`)
    - `inventory.py` (`/inventory/simulations`)
    - `evaluations.py` (`/evaluations/benchmark`)
    - `monitoring.py` (`/monitoring/drift`, `/monitoring/audit`)
  - `backend/app/main.py`: FastAPI root application with modern `lifespan` handler, CORS, and `/docs`.
- [x] Expanded Pytest suite to 35/35 passing integration and unit tests.
- [x] Validated live Uvicorn runtime via `scripts/verify_runtime.py`.

### Phase 3: Frontend Scaffolding with Vite + React + Tailwind (Completed)
- [x] Initialized `frontend/` using Vite + React 18 + TypeScript.
- [x] Configured Tailwind CSS with Deep Navy & Cyan design tokens (`tailwind.config.js`, `index.css`).
- [x] Installed frontend dependencies: `lucide-react`, `recharts`, `react-is`, `clsx`, `tailwind-merge`.
- [x] Created typed API client (`frontend/src/api/client.ts`) and TypeScript interfaces (`frontend/src/types/index.ts`).

### Phase 4: Frontend UI Pages & Components (Completed)
- [x] **Shell & Navigation:**
  - `Sidebar.tsx`: 11 navigation tabs, project badge, backend status pill.
  - `Header.tsx`: Dynamic title, subtitle, active dataset pill, coherence indicator.
  - `KpiCard.tsx`: Reusable metric card with trend badges.
- [x] **11 Enterprise Pages (`frontend/src/pages/`):**
  - [x] `ExecutiveOverview.tsx`: Multi-tier KPIs, revenue volume, trend charts.
  - [x] `DataManagement.tsx`: Dataset validation, quality report, demo data generator, CSV upload.
  - [x] `HierarchyExplorer.tsx`: Interactive tree node explorer and Summing Matrix $S$ visualizer.
  - [x] `ForecastStudio.tsx`: Point forecasting, horizon slider, actual vs forecast chart.
  - [x] `ReconciliationLab.tsx`: Coherence check, error elimination, reconciliation comparison.
  - [x] `UncertaintyCalibration.tsx`: Conformal vs Bootstrap intervals, empirical coverage, Winkler score.
  - [x] `InventorySimulator.tsx`: Parameter sliders ($L$, $R$, $\alpha$), 3-policy comparison, daily trace chart.
  - [x] `ModelEvaluation.tsx`: Cross-model accuracy leaderboard, scale-free MASE/RMSSE, Hyndman theory.
  - [x] `ExperimentsMonitoring.tsx`: Population Stability Index (PSI) drift gauge, tracking signal surveillance, ablation stress tests.
  - [x] `AuditTrail.tsx`: Immutable SQLite compliance ledger, SHA-256 hashes, event filter, JSON export.
  - [x] `SettingsDocumentation.tsx`: Academic citations, mathematical proofs, OpenAPI documentation link.
- [x] Wired all pages into `App.tsx` with dynamic tab switching.

### Phase 5: Verification, Packaging & Deliverables (Completed)
- [x] Executed `npm run build` with **0 TypeScript and 0 CSS errors**.
- [x] Executed Pytest suite with **35/35 tests passing**.
- [x] Verified live runtime endpoints using `scripts/verify_runtime.py`.
- [x] Packaged clean deliverable archive: `DemandWise_React_FastAPI_Final.zip`.
- [x] Verified ZIP integrity, file structure, and contents.
- [x] Updated all project documentation (`README.md`, `PROJECT_STATUS.md`, `CONTINUATION_LOG.md`).
