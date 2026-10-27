# DemandWise — Scholarly Literature Review

## 1. Introduction & Theoretical Foundations
Hierarchical time series forecasting and inventory control are central pillars of industrial data science and supply chain management. This literature review synthesizes key academic contributions across three foundational areas:
1. Hierarchical forecast reconciliation.
2. Intermittent demand modeling.
3. Conformal prediction and probabilistic uncertainty quantification.

---

## 2. Core Literature & Citations

### 2.1 Hierarchical Reconciliation Frameworks
- **Hyndman, R. J., Ahmed, R. A., Athanasopoulos, G., & Shang, H. L. (2011).** Optimal combination forecasts for hierarchical time series. *Computational Statistics & Data Analysis*, 55(9), 2579–2589.
  - *Contribution:* Introduced the mathematical regression formulation of hierarchical reconciliation: $y_t = S \beta_t + \epsilon_t$, proving that optimal reconciliation can be framed as generalized least squares (GLS).
- **Wickramasuriya, S. L., Athanasopoulos, G., & Hyndman, R. J. (2019).** Optimal forecast reconciliation for hierarchical and grouped time series through trace minimization. *Journal of the American Statistical Association*, 114(526), 804–819.
  - *Contribution:* Developed the Minimum Trace (MinT) estimator, demonstrating that minimizing the trace of the reconciled error covariance matrix yields an unbiased, variance-minimizing projection.
- **Panagiotelis, A., Athanasopoulos, G., Gamakumara, P., & Hyndman, R. J. (2021).** Forecast reconciliation: A geometric view with new insights on bias, evaluation, and use of slowly changing hierarchies. *International Journal of Forecasting*, 37(1), 170–183.
  - *Contribution:* Clarified the geometric orthogonal projection interpretation of reconciliation matrices and discussed the preservation of point versus probabilistic forecasts.

### 2.2 Intermittent Demand Modeling
- **Croston, J. D. (1972).** Forecasting for inventory control of intermittent demand. *Operational Research Quarterly*, 289–303.
  - *Contribution:* Formulated the seminal separation between demand arrival intervals and demand transaction magnitude.
- **Syntetos, A. A., & Boylan, J. E. (2005).** The accuracy of intermittent demand estimates. *International Journal of Forecasting*, 21(2), 303–314.
  - *Contribution:* Proved that Croston's original estimator exhibits positive bias and derived the Syntetos-Boylan Approximation (SBA) correction factor $(1 - \alpha/2)$.

### 2.3 Conformal Prediction & Probabilistic Evaluation
- **Vovk, V., Gammerman, A., & Shafer, G. (2005).** *Algorithmic Learning in a Random World*. Springer Science & Business Media.
  - *Contribution:* Groundwork for conformal prediction, establishing non-parametric, distribution-free finite-sample coverage guarantees.
- **Gneiting, T., & Raftery, A. E. (2007).** Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378.
  - *Contribution:* Formalized strictly proper scoring rules, including the interval score (Winkler score), penalizing both width and non-coverage.
- **Hyndman, R. J., & Koehler, A. B. (2006).** Another look at measures of forecast accuracy. *International Journal of Forecasting*, 22(4), 679–688.
  - *Contribution:* Introduced the Mean Absolute Scaled Error (MASE), overcoming division-by-zero instabilities associated with MAPE in intermittent time series.

### 2.4 Inventory Optimization Under Uncertainty
- **Silver, E. A., Pyke, D. F., & Peterson, R. (1998).** *Inventory Management and Production Planning and Scheduling* (Vol. 3). John Wiley & Sons.
  - *Contribution:* Canonical treatment of periodic review $(R, s, S)$ policies, safety stock scaling, and asymmetric stockout penalty structures.
