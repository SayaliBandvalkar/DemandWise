"""Deterministic synthetic retail dataset generator for hierarchical demand forecasting.

Generates realistic retail sales and inventory data with:
- Strict hierarchical mappings: SKU -> Category, Store -> Region
- Multiple demand patterns: smooth, seasonal, intermittent (lumpy/slow-moving)
- Day-of-week seasonality, holiday effects, promotional lifts
- Occasional demand spikes and zero-demand periods
- Unit economics (price, cost, margin) and operational constraints (lead time, starting inventory)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class DatasetConfig:
    """Configuration parameters for synthetic retail dataset generation."""

    start_date: str = "2023-01-01"
    end_date: str = "2023-12-31"
    frequency: str = "D"
    num_skus: int = 12
    num_stores: int = 4
    num_regions: int = 2
    random_seed: int = 42

    # Proportions of SKU demand profiles
    # smooth: steady non-zero demand with mild noise
    # seasonal: high weekly/monthly seasonality
    # intermittent: frequent zero-demand periods (Croston-like)
    demand_profiles: Dict[str, float] = field(
        default_factory=lambda: {"smooth": 0.40, "seasonal": 0.35, "intermittent": 0.25}
    )


class RetailDataGenerator:
    """Deterministic retail data generator."""

    def __init__(self, config: Optional[DatasetConfig] = None):
        self.config = config or DatasetConfig()
        self.rng = np.random.default_rng(self.config.random_seed)

    def generate(self) -> pd.DataFrame:
        """Generate the full hierarchical retail dataframe."""
        self.rng = np.random.default_rng(self.config.random_seed)
        dates = pd.date_range(
            start=self.config.start_date,
            end=self.config.end_date,
            freq=self.config.frequency,
        )
        n_days = len(dates)

        # 1. Establish Store -> Region mapping
        regions = [f"Region_{chr(65 + i)}" for i in range(self.config.num_regions)]
        stores = [f"Store_{i+1:02d}" for i in range(self.config.num_stores)]
        store_region_map = {
            store: regions[i % len(regions)] for i, store in enumerate(stores)
        }

        # 2. Establish SKU -> Category mapping and SKU profiles
        categories = ["Beverages", "Dairy", "Bakery", "Snacks"]
        skus = [f"SKU_{i+1:03d}" for i in range(self.config.num_skus)]
        sku_category_map = {
            sku: categories[i % len(categories)] for i, sku in enumerate(skus)
        }

        # Assign profile, base price, cost, base lead time, and base demand to each SKU
        sku_metadata = {}
        profiles = ["smooth", "seasonal", "intermittent"]
        profile_weights = [
            self.config.demand_profiles["smooth"],
            self.config.demand_profiles["seasonal"],
            self.config.demand_profiles["intermittent"],
        ]

        for sku in skus:
            profile = self.rng.choice(profiles, p=profile_weights)
            base_price = round(float(self.rng.uniform(3.5, 45.0)), 2)
            margin = float(self.rng.uniform(0.25, 0.55))
            base_cost = round(base_price * (1.0 - margin), 2)
            lead_time = int(self.rng.integers(2, 10))
            base_volume = float(self.rng.uniform(5.0, 35.0))
            sku_metadata[sku] = {
                "profile": profile,
                "base_price": base_price,
                "base_cost": base_cost,
                "lead_time": lead_time,
                "base_volume": base_volume,
            }

        # Pre-compute calendar effects
        day_of_week = dates.dayofweek
        day_of_year = dates.dayofyear

        # Weekend lift (Saturday=5, Sunday=6)
        weekend_factor = np.where(day_of_week >= 5, 1.35, 1.0)
        # Mid-week dip (Tuesday=1, Wednesday=2)
        midweek_factor = np.where(np.isin(day_of_week, [1, 2]), 0.90, 1.0)

        # Annual seasonality wave
        annual_wave = 1.0 + 0.25 * np.sin(2 * np.pi * day_of_year / 365.25)

        # Major holidays (e.g., New Year, Memorial Day, Labor Day, Thanksgiving, Christmas)
        holiday_mask = np.zeros(n_days, dtype=int)
        for h_month, h_day in [(1, 1), (7, 4), (11, 25), (12, 24), (12, 25), (12, 31)]:
            match = (dates.month == h_month) & (dates.day == h_day)
            holiday_mask[match] = 1

        all_records = []

        # Generate series for each SKU x Store combination (bottom-level series)
        for store in stores:
            region = store_region_map[store]
            # Store multiplier (some stores have larger market footprint)
            store_multiplier = float(self.rng.uniform(0.85, 1.30))

            for sku in skus:
                meta = sku_metadata[sku]
                category = sku_category_map[sku]
                profile = meta["profile"]
                base_vol = meta["base_volume"] * store_multiplier
                unit_price = meta["base_price"]
                unit_cost = meta["base_cost"]
                lead_time = meta["lead_time"]

                # Promotions occur randomly ~5% of days, lasting 3-7 days
                promo_mask = np.zeros(n_days, dtype=int)
                num_promos = int(self.rng.poisson(lam=4))
                for _ in range(num_promos):
                    p_start = int(self.rng.integers(0, max(1, n_days - 7)))
                    p_len = int(self.rng.integers(3, 8))
                    promo_mask[p_start : min(n_days, p_start + p_len)] = 1

                # Generate demand series based on profile
                if profile == "smooth":
                    # Gaussian noise around steady mean
                    noise = self.rng.normal(0, 0.15 * base_vol, n_days)
                    demand = (
                        base_vol * weekend_factor * midweek_factor
                        + noise
                        + promo_mask * (0.4 * base_vol)
                        + holiday_mask * (0.6 * base_vol)
                    )
                    demand = np.maximum(0, demand)

                elif profile == "seasonal":
                    # Strong weekly pattern + annual wave
                    weekly_factor = np.array([0.7, 0.8, 0.9, 1.1, 1.4, 1.6, 1.3])[day_of_week]
                    noise = self.rng.normal(0, 0.20 * base_vol, n_days)
                    demand = (
                        base_vol * weekly_factor * annual_wave
                        + noise
                        + promo_mask * (0.5 * base_vol)
                        + holiday_mask * (0.8 * base_vol)
                    )
                    demand = np.maximum(0, demand)

                else:  # intermittent (Croston-like)
                    # Bernoulli arrival process + Gamma sizing
                    arrival_prob = 0.25
                    arrivals = self.rng.binomial(1, arrival_prob, n_days)
                    sizes = self.rng.gamma(shape=3.0, scale=base_vol / 2.0, size=n_days)
                    demand = arrivals * sizes * (1.0 + 0.3 * promo_mask)
                    demand = np.maximum(0, demand)

                # Occasional spike (supply disruptions or viral trends: 1-2 spikes per year)
                num_spikes = self.rng.binomial(n=1, p=0.01, size=n_days)
                demand += num_spikes * self.rng.uniform(2.5, 4.0, size=n_days) * base_vol

                units_sold = np.round(demand).astype(float)

                # Simulated realistic inventory trajectory
                # Starting stock = ~15 days of average demand
                avg_daily = max(1.0, float(np.mean(units_sold)))
                current_stock = avg_daily * 14.0
                stock_history = np.zeros(n_days)

                for t in range(n_days):
                    stock_history[t] = max(0.0, current_stock)
                    sold = min(current_stock, units_sold[t])
                    current_stock -= sold
                    # Periodic replenishment order every 7 days
                    if t % 7 == 0:
                        order_qty = avg_daily * 10.0
                        current_stock += order_qty

                # Promotional pricing discount
                daily_price = np.where(promo_mask == 1, np.round(unit_price * 0.85, 2), unit_price)

                for t in range(n_days):
                    all_records.append(
                        {
                            "date": dates[t].strftime("%Y-%m-%d"),
                            "sku_id": sku,
                            "category": category,
                            "store_id": store,
                            "region": region,
                            "units_sold": float(units_sold[t]),
                            "unit_price": float(daily_price[t]),
                            "unit_cost": float(unit_cost),
                            "inventory_on_hand": float(stock_history[t]),
                            "lead_time_days": int(lead_time),
                            "is_promotion": int(promo_mask[t]),
                            "is_holiday": int(holiday_mask[t]),
                        }
                    )

        df = pd.DataFrame(all_records)
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values(by=["date", "region", "store_id", "category", "sku_id"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df


def generate_and_save_sample(
    output_path: str = "data/sample/retail_hierarchy.csv",
    seed: int = 42,
) -> pd.DataFrame:
    """Generate deterministic retail dataset and save to CSV."""
    cfg = DatasetConfig(random_seed=seed)
    gen = RetailDataGenerator(cfg)
    df = gen.generate()
    # Ensure directory
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
