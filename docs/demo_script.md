# DemandWise — 5-to-8 Minute Capstone Presentation & Defense Script

**Project ID:** MDS-07  
**Official Project Title:** Hierarchical Demand Forecasting with Probabilistic Reconciliation and Inventory Decisions  
**Product Name:** DemandWise  
**Target Audience:** Capstone Evaluation Committee & Academic Supervisors  

---

## 🎙️ Slide / Screen Demo Walkthrough

### 0:00 - 1:00 | Introduction & The Industrial Problem
> *"Good morning, respected committee members and faculty advisors. Today, I am proud to present **DemandWise**, my M.Sc. Data Science Semester III capstone project.*
>
> *In enterprise retail and supply chain operations, organizations face a critical mathematical conflict: if every store planner forecasts their local SKU demand independently, the sum of those local forecasts almost never equals the regional or national total forecasted by headquarters. This cross-level contradiction is known as **forecast incoherence**.*
>
> *Furthermore, point forecasts fail to convey risk. Overestimating demand locks up working capital in holding costs, while underestimating causes stockouts, lost sales, and customer attrition. DemandWise bridges the gap between hierarchical statistical theory, distribution-free probabilistic calibration, and downstream inventory decisions."*

---

### 1:00 - 2:30 | Mathematical Architecture & Summing Matrix S
*(Action: Navigate to Module 2: Data & Hierarchy Explorer)*
> *"Let us examine the mathematical structure. Here in Module 2, DemandWise constructs the structural Summing Matrix $S \in \{0, 1\}^{59 \times 48}$.*
>
> *We model 48 bottom-level SKU-store combinations, aggregating through 4 categories, 4 stores, and 2 geographical regions to 1 enterprise total. The heatmap on screen displays the exact linear summing matrix $S$ where $y_t = S b_t$. Every entry represents the exact structural aggregation rule."*

---

### 2:30 - 4:00 | Base Forecasting & The Incoherence Dilemma
*(Action: Navigate to Module 3: Forecast Studio & Module 4: Reconciliation Lab)*
> *"In Module 3, DemandWise generates multi-step forward predictions using five distinct algorithms: Naive, Seasonal Naive, Croston's Syntetos-Boylan Approximation for intermittent demand, Holt-Winters Exponential Smoothing, and Gradient Boosted LightGBM trees.*
>
> *When we move to Module 4, the Reconciliation Lab, observe this crucial finding: when models predict each series independently, the maximum coherence error is **112.94 units**. National headquarters expects one number, but summing the store predictions produces another.*
>
> *DemandWise implements Bottom-Up, Top-Down, and MinT shrinkage reconciliation. By applying the linear projection $\tilde{y} = S P \hat{y}$, Bottom-Up reconciliation reduces coherence error to **exactly 0.0000**, and simultaneously improves overall accuracy, reducing total WAPE from 15.50% down to 14.83%."*

---

### 4:00 - 5:30 | Conformal Uncertainty Calibration
*(Action: Navigate to Module 5: Uncertainty & Calibration)*
> *"Next, we address uncertainty quantification. Traditional forecasting assumes residual normality. In Module 5, our empirical benchmark shows that standard residual bootstrap severely undercovers: at a nominal 95% confidence level, it only captures 61.7% of actual realizations due to demand spikes.*
>
> *To solve this, DemandWise integrates **Split Conformal Prediction**. Conformal prediction provides distribution-free, finite-sample theoretical guarantees. As demonstrated in our benchmark table, Conformal Prediction achieves **95.5% empirical coverage** against the 95.0% nominal target, with a vastly superior Winkler interval score of 236.74 compared to 368.39 for bootstrap."*

---

### 5:30 - 7:00 | Inventory Decision Simulation
*(Action: Navigate to Module 6: Inventory Simulator)*
> *"The ultimate value of data science is operational decision-making. In Module 6, DemandWise powers a discrete-event inventory simulator across time horizons.*
>
> *We compare three policies: a baseline moving-average buffer, a forecast-driven policy, and an uncertainty-aware policy that sizes safety stock directly from the upper conformal quantile.*
>
> *In our stress-test ablation experiment where demand spikes and zero-inflation are injected, the baseline policy over-orders, incurring $21.55 in holding costs. The uncertainty-aware policy reduces holding costs to $10.72 while maintaining safety stock protection, effectively minimizing total relevant inventory cost."*

---

### 7:00 - 8:00 | MLOps Governance & Conclusion
*(Action: Navigate to Module 9: Audit Trail and Module 10: Settings)*
> *"Finally, DemandWise is built for governance. In Module 9, every data ingestion, model fit, reconciliation run, and inventory scenario is logged to an immutable SQLite database with SHA-256 cryptographic hashes.*
>
> *The entire codebase is verified by a 25-test automated pytest suite with a 100% pass rate. The project is completely packaged into `DemandWise_MDS07_Final.zip`.*
>
> *Thank you. I welcome your questions and feedback."*
