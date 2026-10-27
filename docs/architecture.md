# DemandWise — System Architecture & Data Flow

## 1. High-Level System Architecture

DemandWise is designed around a modular, decoupled architecture where each stage of the forecasting-reconciliation-inventory pipeline operates with strict mathematical interfaces and immutability guarantees.

```
                    +--------------------------------+
                    |   Transactional Retail Data    |
                    | (CSV / Database / Synthetic)   |
                    +---------------+----------------+
                                    |
                                    v
                    +--------------------------------+
                    |    Pydantic Schema Validator   |
                    |  - Column presence & types     |
                    |  - Negative & NaN detection    |
                    |  - Hierarchy consistency check |
                    +---------------+----------------+
                                    |
                                    v
                    +--------------------------------+
                    |  Hierarchy Engine & Matrix S   |
                    |    y_t = S * b_t in R^m        |
                    +---------------+----------------+
                                    |
         +--------------------------+--------------------------+
         |                                                     |
         v                                                     v
+-------------------------------+             +-------------------------------+
|     Base Forecasters          |             |   Uncertainty Engine          |
|  - Naive & Seasonal Naive     |             |  - Residual Bootstrap Paths   |
|  - Croston's SBA              |             |  - Split Conformal Prediction |
|  - Holt-Winters Exp Smoothing |             |  - 80% & 95% Prediction Bounds|
|  - LightGBM Regressor (Lags)  |             +---------------+---------------+
+---------------+---------------+                             |
                |                                             |
                v                                             |
+-------------------------------+                             |
|  Reconciliation Orchestrator  |                             |
|  - Bottom-Up (BU)             |                             |
|  - Top-Down (TD Proportions)  |                             |
|  - MinT Shrinkage (W_shrink)  |                             |
+---------------+---------------+                             |
                |                                             |
                +----------------------+----------------------+
                                       |
                                       v
                    +--------------------------------+
                    |  Discrete-Event Inventory Sim  |
                    |  - Lead-time pipeline queue    |
                    |  - (s, S) Replenishment policy |
                    |  - Lost sales & stockout costs |
                    |  - Holding & ordering costs    |
                    +---------------+----------------+
                                    |
         +--------------------------+--------------------------+
         |                                                     |
         v                                                     v
+-------------------------------+             +-------------------------------+
|  Streamlit Enterprise UI      |             |   MLOps & Compliance          |
|  - 10 Analytic Modules        |             |  - SQLite Audit Logger        |
|  - Plotly Interactive Visuals |             |  - PSI Data Drift Detector    |
|  - Scenario Tuning Sliders    |             |  - Tracking Signal Alerts     |
+-------------------------------+             +-------------------------------+
```

---

## 2. Component Specifications

### 2.1 Ingestion & Hierarchy Module (`demandwise.data`, `demandwise.forecasting.hierarchy`)
- Translates flat tabular transaction tables into structured multidimensional arrays.
- Generates the structural Summing Matrix $S \in \{0, 1\}^{m \times k}$ using graph traversal of the entity hierarchy (SKU $\to$ Category, Store $\to$ Region, Region/Category $\to$ Total).
- Implements linear projection $Y = B S^T$ to aggregate all temporal series across the full hierarchy without loss of fidelity.

### 2.2 Base Forecasting Engine (`demandwise.forecasting.models`)
- Implements standard scikit-learn/statsmodels compatible interfaces (`fit`, `predict`, `fit_predict`).
- Feature engineering pipeline: Autoregressive lags ($t-1, \dots, t-14$), rolling moving averages (7-day, 14-day), calendar features (day of week, weekend indicator, month).
- All lag operations are strictly shifted by 1 period to prevent target leakage.

### 2.3 Reconciliation Layer (`demandwise.reconciliation.reconciler`)
- Linear projection operator: $\tilde{y} = S P \hat{y}$.
- Computes sample covariance of in-sample residuals $W = \frac{1}{T} e e^T$.
- Implements Ledoit-Wolf shrinkage towards diagonal target to ensure numerical stability and positive definiteness even when $m > T$.

### 2.4 Uncertainty & Conformal Calibration (`demandwise.uncertainty`)
- Provides distribution-free prediction intervals via Split Conformal Prediction.
- Solves finite-sample coverage guarantee: $P(Y_{t+h} \in C(X_{t+h})) \ge 1 - \alpha$.
- Calculates empirical coverage rates and Winkler interval penalty scores.

### 2.5 Inventory Decision Simulator (`demandwise.inventory`)
- Discrete-time day-by-day operational simulation.
- Tracks pipeline orders subject to deterministic lead time $L$.
- Records stockouts as lost sales with margin penalties, computing fill rates and total relevant inventory cost ($TC = \text{Holding} + \text{Stockout} + \text{Ordering}$).

### 2.6 Governance & Audit Trail (`demandwise.governance.audit`)
- Local SQLite database storing SHA-256 hashed event records.
- Ensures auditability for corporate model governance and regulatory compliance.
