# DemandWise — Forecasting, Reconciliation & Inventory Methodology

## 1. Mathematical Formulation of Hierarchical Time Series

Let a retail organization manage $k$ bottom-level series (e.g., individual SKU sales at specific store locations). The bottom-level demand at time $t$ is represented by the vector:
$$b_t = [b_{1, t}, b_{2, t}, \dots, b_{k, t}]^T \in \mathbb{R}^k$$

Let $m$ denote the total number of series across all levels of the operational hierarchy ($m > k$), including category subtotals, store subtotals, regional totals, and the national total:
$$y_t = [y_{1, t}, y_{2, t}, \dots, y_{m, t}]^T \in \mathbb{R}^m$$

The aggregation relationships across the hierarchy are completely described by the structural **Summing Matrix** $S \in \{0, 1\}^{m \times k}$:
$$y_t = S b_t$$

Where:
- Row $i$ of $S$ has entry $S_{ij} = 1$ if bottom series $j$ belongs to aggregate series $i$, and $0$ otherwise.
- The bottom $k$ rows of $S$ form the identity matrix $I_k \in \mathbb{R}^{k \times k}$.

---

## 2. Base Forecasting Algorithms

Base forecasts $\hat{y}_{t+h}$ are generated independently for each series in the hierarchy without cross-series constraints:

1. **Naive Baseline:**
   $$\hat{y}_{t+h|t} = y_t$$

2. **Seasonal Naive Baseline ($m=7$):**
   $$\hat{y}_{t+h|t} = y_{t+h - m \cdot (k+1)}$$

3. **Croston's Method & Syntetos-Boylan Approximation (SBA) for Intermittent Demand:**
   Separates non-zero demand size $z_t$ and inter-arrival intervals $p_t$ via exponential smoothing:
   $$z_t = \alpha y_t + (1 - \alpha) z_{t-1}$$
   $$p_t = \alpha q_t + (1 - \alpha) p_{t-1}$$
   The standard Croston forecast rate is $\hat{y} = \frac{z}{p}$. Syntetos & Boylan (2005) showed this estimator is positively biased and introduced the SBA correction:
   $$\hat{y}_{SBA} = \left(1 - \frac{\alpha}{2}\right) \frac{z}{p}$$

4. **Holt-Winters Exponential Smoothing:**
   Captures additive level $\ell_t$, trend $b_t$, and seasonal factor $s_t$:
   $$\hat{y}_{t+h|t} = \ell_t + h b_t + s_{t+h-m}$$

5. **Gradient Boosted Autoregressive Tree (LightGBM):**
   $$\hat{y}_{t+h} = f(y_{t-1}, y_{t-2}, \dots, y_{t-14}, \text{roll\_mean}_7, \text{roll\_mean}_{14}, \text{dow}, \text{month})$$

---

## 3. Hierarchical Forecast Reconciliation

Because base forecasts $\hat{y}$ are produced independently, they are generally **incoherent**, meaning $\hat{y} \ne S \hat{b}$.

Reconciliation seeks a linear mapping matrix $P \in \mathbb{R}^{k \times m}$ that maps the unreconciled forecasts $\hat{y}$ into revised bottom forecasts $\tilde{b} = P \hat{y}$, which are then summed to yield coherent forecasts:
$$\tilde{y} = S P \hat{y}$$

### 3.1 Bottom-Up (BU)
Takes only bottom-level forecasts ($P = [0_{k \times (m-k)} \mid I_k]$):
$$\tilde{y}_{BU} = S \hat{b}$$
- **Guarantee:** Exactly coherent ($\text{coherence error} = 0.0000$).
- **Limitation:** Ignores valuable aggregate signals captured at upper levels.

### 3.2 Top-Down (TD Proportions)
Disaggregates top-level forecast $\hat{y}_{total}$ according to proportions $p_j$:
$$\tilde{b}_j = p_j \cdot \hat{y}_{total}, \quad \tilde{y}_{TD} = S \tilde{b}$$

### 3.3 MinT (Minimum Trace Optimal Reconciliation)
Wickramasuriya, Athanasopoulos, & Hyndman (2019) proved that the unbiased linear reconciliation minimizing the trace of the reconciled error covariance matrix is:
$$P_{MinT} = (S^T W^{-1} S)^{-1} S^T W^{-1}$$
Where $W = \text{Cov}(e_t)$ is the in-sample forecast error covariance matrix.

To prevent instability when $m$ is large relative to sample size $T$, DemandWise applies **Ledoit-Wolf shrinkage**:
$$W_{shrink} = (1 - \lambda) W_{sample} + \lambda \text{diag}(W_{sample})$$

---

## 4. Probabilistic Uncertainty & Conformal Calibration

To produce calibrated prediction intervals $[L_{t+h}, U_{t+h}]$ with nominal coverage $1 - \alpha$:

### 4.1 Split Conformal Prediction
Given held-out calibration actuals $y_i^{cal}$ and predictions $\hat{y}_i^{cal}$, compute nonconformity scores:
$$R_i = |y_i^{cal} - \hat{y}_i^{cal}|$$
Compute the $(1 - \alpha)$-quantile adjusted for finite sample size:
$$\hat{q} = \text{Quantile}\left(\{R_i\}, \frac{\lceil (n+1)(1 - \alpha) \rceil}{n}\right)$$
The prediction interval is:
$$C(X_{t+h}) = [\max(0, \hat{y}_{t+h} - \hat{q}), \hat{y}_{t+h} + \hat{q}]$$
- **Guarantee:** Finite-sample, distribution-free coverage:
  $$P(Y_{t+h} \in C(X_{t+h})) \ge 1 - \alpha$$

### 4.2 Winkler Score (Interval Score)
$$S_\alpha(L, U, y) = (U - L) + \frac{2}{\alpha}(L - y)\mathbb{I}(y < L) + \frac{2}{\alpha}(y - U)\mathbb{I}(y > U)$$

---

## 5. Inventory Decision Optimization

Replenishment decisions operate under periodic review $(R)$ with lead time $(L)$:

- **Protection Interval:** $T_p = L + R$
- **Safety Stock (Uncertainty-Aware):** Sized from the upper calibrated quantile $\hat{q}_{1-\alpha}$ over the protection window:
  $$SS = \sum_{t=1}^{T_p} \hat{U}_t - \sum_{t=1}^{T_p} \hat{y}_t$$
- **Reorder Point (ROP):**
  $$ROP = \sum_{t=1}^L \hat{y}_t + SS$$
- **Order Quantity:** If $I_{on\_hand} + I_{pipeline} \le ROP$, order:
  $$Q = \max\left(MOQ, \sum_{t=1}^{T_p} \hat{U}_t - (I_{on\_hand} + I_{pipeline})\right)$$
