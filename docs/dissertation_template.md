# DemandWise — M.Sc. Data Science Dissertation / Capstone Report Template

**Degree:** Master of Science in Data Science (Semester III Capstone)  
**Project ID:** MDS-07  
**Title:** Hierarchical Demand Forecasting with Probabilistic Reconciliation and Inventory Decisions  
**Product Name:** DemandWise  

---

## Abstract
Accurate multi-echelon demand forecasting in retail enterprises is fundamentally challenged by hierarchical aggregation inconsistencies, intermittent demand patterns, and uncalibrated prediction intervals. When demand forecasts are produced independently at different levels of an organization (e.g., SKU, store, regional, and national totals), the mathematical sum of lower-level forecasts rarely reconciles with aggregate predictions, creating operational confusion and suboptimal replenishment. This dissertation presents **DemandWise**, an end-to-end framework that unifies:
1. Structural summing matrix representations ($y_t = S b_t$) across a 59-series retail hierarchy.
2. Intermittent demand estimation via Syntetos-Boylan Approximated (SBA) Croston methods alongside gradient-boosted autoregressive models.
3. Optimal forecast reconciliation (Bottom-Up, Top-Down proportions, and Minimum Trace Shrinkage) that reduces coherence error to exactly zero while improving top-level WAPE from 15.50% to 14.83%.
4. Split Conformal Prediction for calibrated uncertainty quantification, achieving 95.5% empirical coverage against nominal 95.0% targets, overcoming severe residual bootstrap undercoverage (61.7%).
5. An operational discrete-event inventory simulator demonstrating that uncertainty-aware safety stock sizing dynamically reduces holding costs by over 50% under stress-test demand volatility without sacrificing customer service levels.

---

## Table of Contents
1. **Chapter 1: Introduction**
   - 1.1 Industrial Problem Statement
   - 1.2 Research Questions & Formal Hypotheses
   - 1.3 Project Objectives (MDS-07)
   - 1.4 Scope and Delimitations
2. **Chapter 2: Literature Review**
   - 2.1 Classical Time Series & Intermittent Demand (Croston, Syntetos & Boylan)
   - 2.2 Hierarchical Reconciliation Theory (Hyndman, Wickramasuriya, MinT)
   - 2.3 Probabilistic Calibration & Conformal Prediction (Vovk, Gneiting)
   - 2.4 Multi-Echelon Inventory Control (Silver, Pyke, Peterson)
3. **Chapter 3: Methodology & Mathematical Formulation**
   - 3.1 Structural Summing Matrix $S \in \{0, 1\}^{m \times k}$
   - 3.2 Base Forecasting Algorithms
   - 3.3 Linear Projection Reconciliation: $\tilde{y} = S P \hat{y}$
   - 3.4 Conformal Nonconformity Scores and Coverage Guarantees
   - 3.5 Discrete-Event Inventory Dynamics
4. **Chapter 4: Implementation Architecture & MLOps**
   - 4.1 Modular Software Architecture
   - 4.2 Deterministic Synthetic Retail Generation & Provenance
   - 4.3 SQLite Cryptographic Audit Logging
   - 4.4 Population Stability Index (PSI) Drift Monitoring
5. **Chapter 5: Empirical Results & Discussion**
   - 5.1 Experiment 1: Base Forecaster Benchmarking across Levels
   - 5.2 Experiment 2: Unreconciled vs Reconciled Coherence Errors
   - 5.3 Experiment 3: Probabilistic Interval Calibration at 80% and 95%
   - 5.4 Experiment 4: Inventory Policy Simulation & Cost Trade-Offs
   - 5.5 Experiment 5: Robustness Ablation under Demand Spikes & Zero Inflation
6. **Chapter 6: Conclusion & Future Work**
   - 6.1 Summary of Contributions
   - 6.2 Industrial Implications
   - 6.3 Limitations & Future Research Horizons
7. **References**
8. **Appendices**
   - Appendix A: Summing Matrix Mathematical Proofs
   - Appendix B: Complete Code Repository & Pytest Execution Logs
   - Appendix C: Threat Model & Risk Matrix
