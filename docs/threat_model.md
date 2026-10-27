# DemandWise — Threat Model & Risk Register

## 1. Threat Modeling Overview
This threat model assesses security risks, failure modes, and governance controls associated with the **DemandWise** engine in accordance with the STRIDE framework.

---

## 2. STRIDE Threat Analysis

| Threat Category | Potential Attack / Failure Vector | Impact Severity | DemandWise Mitigation Control |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Unauthorized entity submits fraudulent audit logs or bypasses API endpoints. | Medium | SQLite audit logs are appended with SHA-256 record hashes that incorporate timestamps and actor signatures. Local network bind only by default. |
| **Tampering** | Malicious injection of negative demand or corrupted CSV headers into the pipeline. | High | `RetailDataValidator` strictly validates schema constraints, column types, duplicate primary keys, and rejects negative sales quantities prior to ingestion. |
| **Repudiation** | Disputing automated reorder decisions or model adjustments. | Medium | Immutable SQLite audit database logs every model run, reconciliation method selection, and inventory scenario execution. |
| **Information Disclosure** | Leakage of proprietary supplier costs, wholesale pricing, or unit margins. | Medium | No cloud transmission; data remains local. Secrets and credentials are excluded from version control via `.gitignore`. |
| **Denial of Service** | Singular matrix inversion in MinT or exponential recursion causing pipeline freeze. | High | Automatic matrix regularization: Ledoit-Wolf shrinkage, minimum eigenvalue floor, and diagonal pseudo-inverse fallbacks prevent zero-determinant crashes. |
| **Elevation of Privilege** | Arbitrary code execution via serialized model pickle files or upload paths. | Critical | No arbitrary pickled models or exec/eval commands are permitted. Clean dataframes and deterministic algorithms are used exclusively. |

---

## 3. Operational Failure Modes & Fallback Matrix

| Component | Failure Condition | Graceful Fallback Strategy |
| :--- | :--- | :--- |
| **LightGBM** | Insufficient training history ($N < 21$ days) or missing compiler DLLs. | Automatically falls back to L2-regularized Ridge Autoregression with zero service interruption. |
| **Holt-Winters** | Series exhibits zero variance or non-seasonal short length ($N < 14$). | Automatically falls back to Simple Exponential Smoothing (SES) or trailing rolling average. |
| **MinT Reconciliation** | Error covariance matrix $W$ is singular or ill-conditioned. | Falls back to Weighted Least Squares (WLS) diagonal variance or Bottom-Up summing. |
| **Conformal Prediction** | Calibration set is smaller than required quantile coverage cutoff. | Gracefully defaults to empirical sample quantiles with variance scaling. |
