# DemandWise — User Guide & Operational Manual

## 1. Quick Start Guide for Windows Users

DemandWise is built to run natively on Windows 11 with PowerShell and Python 3.12.

### Step 1: Open PowerShell and Navigate to Workspace
```powershell
cd D:\demandwise
```

### Step 2: Activate the Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If script execution is disabled on your system, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Run the Complete Automated Pipeline
```powershell
python scripts/run_pipeline.py
```
This single command will:
1. Verify the deterministic retail hierarchy dataset (`data/sample/retail_hierarchy.csv`).
2. Run schema diagnostics and check 100% hierarchy integrity.
3. Train all 5 forecasting models across all 59 hierarchical series.
4. Execute Bottom-Up, Top-Down, and MinT reconciliation.
5. Calibrate prediction intervals using Split Conformal Prediction.
6. Simulate inventory replenishment policies and record all results.

### Step 4: Launch the Interactive Enterprise Dashboard
```powershell
streamlit run app.py
```
Your default web browser will automatically open to `http://localhost:8501`.

---

## 2. Navigating the 10 Dashboard Modules

1. **Executive Overview:** High-level summary of total sales, gross margins, fill rate, and enterprise demand dynamics.
2. **Data & Hierarchy Explorer:** Interactive visualization of the Summing Matrix $S \in \{0, 1\}^{59 \times 48}$ and product-store topology.
3. **Forecast Studio:** Select any series in the business hierarchy, choose a forecasting algorithm, and generate real-time multi-step predictions.
4. **Reconciliation Lab:** Inspect cross-tier coherence discrepancies and observe how Bottom-Up reconciliation eliminates 112+ units of error.
5. **Uncertainty & Calibration:** View 80% and 95% prediction intervals; observe why Conformal Prediction achieves 95.5% coverage while residual bootstrap fails.
6. **Inventory Simulator:** Adjust Lead Time and Service Level sliders to see simulated replenishment orders, stockouts, and total costs over time.
7. **Model Evaluation:** Direct comparative matrix of MASE, RMSSE, MAE, RMSE, and WAPE across all models.
8. **Experiments & Monitoring:** Track Population Stability Index (PSI) to detect distribution drift and stress-test under zero-inflation demand shocks.
9. **Audit Trail:** Inspect immutable SQLite logs with cryptographic hashes recording system operations.
10. **Settings & Documentation:** Full literature citations, mathematical proofs, and deliverable ZIP status.

---

## 3. Running Automated Pytest Verification
```powershell
pytest tests/ -v
```
All 25 unit and integration tests will execute and confirm 100% pass rates.

---

## 4. Packaging the Final Deliverable ZIP
```powershell
python scripts/package_zip.py
```
This updates `DemandWise_MDS07_Final.zip` containing all code, tests, documentation, sample data, and verified benchmark outputs.
