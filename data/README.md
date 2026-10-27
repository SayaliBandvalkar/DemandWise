# DemandWise Data Dictionary & Dataset Provenance

## 1. Overview
The dataset powering **DemandWise** is a deterministic, synthetic retail dataset structured specifically for **hierarchical time-series forecasting, probabilistic reconciliation, and inventory decision simulation**.

Synthetic data generation is used to provide:
1. Complete ground-truth transparency for evaluating coherence error, empirical coverage, and inventory policy optimality.
2. Controllable demand features (smooth, seasonal, and Croston-type intermittent demand).
3. Realistic retail hierarchy constraints without privacy, NDA, or commercial data-sharing restrictions.

---

## 2. Hierarchy Structure
The hierarchy follows standard retail operational tiers:

```
                  [Total Demand]
                    /        \
           [Region_A]        [Region_B]
            /      \          /      \
      [Store_01] [Store_02] [Store_03] [Store_04]
          |          |          |          |
   [Categories: Beverages, Dairy, Bakery, Snacks]
          |          |          |          |
   [SKU_001 to SKU_012 at each Store (48 series)]
```

- **Level 0 (Total):** 1 series (Sum of all sales across all stores and SKUs).
- **Level 1 (Region):** 2 series (`Region_A`, `Region_B`).
- **Level 2 (Store):** 4 series (`Store_01`, `Store_02`, `Store_03`, `Store_04`).
- **Level 3 (Category):** 4 series (`Beverages`, `Dairy`, `Bakery`, `Snacks`).
- **Level 4 (Bottom - SKU x Store):** 48 individual product-location time series.

---

## 3. Data Dictionary

| Column Name | Data Type | Mandatory | Description / Constraints | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date` | Date (`YYYY-MM-DD`) | Yes | Calendar date of transaction or observation. | `2023-01-15` |
| `sku_id` | String | Yes | Unique identifier of the stock-keeping unit. | `SKU_003` |
| `category` | String | Yes | Merchandise category to which the SKU belongs. | `Beverages` |
| `store_id` | String | Yes | Retail store location identifier. | `Store_01` |
| `region` | String | Yes | Geographic operating zone of the store. | `Region_A` |
| `units_sold` | Float / Int | Yes | Quantity of units demanded/sold ($\ge 0$). | `18.0` |
| `unit_price` | Float | Yes | Selling price per unit in USD ($> 0$). | `12.50` |
| `unit_cost` | Float | Yes | Procurement / wholesale cost per unit in USD ($> 0$). | `7.25` |
| `inventory_on_hand` | Float | No | Physical stock available at start of business day. | `85.0` |
| `lead_time_days` | Integer | No | Supplier replenishment lead time in days ($[1, 30]$). | `5` |
| `is_promotion` | Binary (0/1) | No | Active discount campaign or flyer promotion indicator. | `1` |
| `is_holiday` | Binary (0/1) | No | Major calendar holiday or holiday-eve indicator. | `0` |

---

## 4. Demand Generation Assumptions
- **Smooth SKUs:** Gaussian fluctuations around steady baseline with mild weekend multiplier ($1.35\times$).
- **Seasonal SKUs:** Strong day-of-week profile (Friday/Saturday peak) plus annual trigonometric wave.
- **Intermittent SKUs:** Bernoulli arrival process ($p=0.25$) paired with Gamma-distributed burst sizes, modeling slow-moving or bulky goods.
- **Promotional Lift:** $+30\%$ to $+50\%$ volume increase during active promotions.
- **Supply Disruptions / Spikes:** $1\%$ Bernoulli trigger producing $2.5\times - 4\times$ demand bursts.
- **Stock Tracking:** Continuous depletion based on actual sales with simulated periodic review reorders.
