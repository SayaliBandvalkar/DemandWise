"""Mathematical representation of hierarchical time-series structures.

Implements the Summing Matrix S such that:
    y_t = S * b_t
where:
    b_t in R^k is the vector of bottom-level series (SKU x Store)
    y_t in R^m is the full vector of all series across all levels (Total, Region, Store, Category, Bottom)
    S in {0, 1}^{m x k} is the summing matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class HierarchyNode:
    """Represents a node in the retail hierarchy."""

    node_id: str
    level: str  # 'total', 'region', 'store', 'category', 'bottom'
    parent_id: Optional[str] = None
    children: List[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class SummingMatrix:
    """Constructs and manages the structural Summing Matrix S."""

    def __init__(
        self,
        series_names: List[str],
        bottom_names: List[str],
        matrix: np.ndarray,
        level_map: Dict[str, str],
    ):
        self.series_names = series_names
        self.bottom_names = bottom_names
        self.matrix = matrix  # shape: (m, k)
        self.level_map = level_map  # series_name -> level name
        self.m = len(series_names)
        self.k = len(bottom_names)

    def bottom_up_aggregate(self, bottom_forecasts: np.ndarray) -> np.ndarray:
        """Map bottom forecasts b (shape: (k, horizon) or (k,)) to full hierarchy y = S @ b."""
        if bottom_forecasts.ndim == 1:
            return self.matrix @ bottom_forecasts
        return self.matrix @ bottom_forecasts

    def is_coherent(self, y: np.ndarray, tolerance: float = 1e-4) -> Tuple[bool, float]:
        """Verify if full vector y satisfies y = S @ b.

        Returns (is_coherent, max_absolute_coherence_error).
        """
        # Bottom series are the last k rows of S (identity matrix)
        bottom_values = y[-self.k :]
        expected_y = self.matrix @ bottom_values
        abs_diff = np.abs(y - expected_y)
        max_err = float(np.max(abs_diff))
        return (max_err <= tolerance, max_err)


class HierarchyTree:
    """Parses tabular retail data into structural hierarchy and produces the Summing Matrix S."""

    def __init__(self, df: pd.DataFrame):
        """Initialize hierarchy from a validated retail DataFrame."""
        self._build_mappings(df)

    def _build_mappings(self, df: pd.DataFrame) -> None:
        """Extract unique hierarchical entities and construct relationships."""
        # Bottom series are SKU x Store pairs
        bottom_df = df[["sku_id", "store_id", "category", "region"]].drop_duplicates()
        bottom_df["bottom_id"] = bottom_df["sku_id"] + "_" + bottom_df["store_id"]
        bottom_df.sort_values(by=["region", "store_id", "category", "sku_id"], inplace=True)
        self.bottom_series: List[str] = bottom_df["bottom_id"].tolist()
        self.k = len(self.bottom_series)

        # Unique aggregations
        self.regions: List[str] = sorted(bottom_df["region"].unique().tolist())
        self.stores: List[str] = sorted(bottom_df["store_id"].unique().tolist())
        self.categories: List[str] = sorted(bottom_df["category"].unique().tolist())

        # Construct full series list in defined hierarchical order:
        # 1. Total (Level 0)
        # 2. Regions (Level 1)
        # 3. Stores (Level 2)
        # 4. Categories (Level 3)
        # 5. Bottom series (Level 4)
        self.all_series: List[str] = []
        self.level_map: Dict[str, str] = {}

        # Level 0
        total_name = "Total"
        self.all_series.append(total_name)
        self.level_map[total_name] = "total"

        # Level 1: Region
        for reg in self.regions:
            name = f"Region_{reg}" if not reg.startswith("Region_") else reg
            self.all_series.append(name)
            self.level_map[name] = "region"

        # Level 2: Store
        for store in self.stores:
            name = f"Store_{store}" if not store.startswith("Store_") else store
            self.all_series.append(name)
            self.level_map[name] = "store"

        # Level 3: Category
        for cat in self.categories:
            name = f"Category_{cat}"
            self.all_series.append(name)
            self.level_map[name] = "category"

        # Level 4: Bottom
        for b_id in self.bottom_series:
            self.all_series.append(b_id)
            self.level_map[b_id] = "bottom"

        self.m = len(self.all_series)

        # Build Summing Matrix S of shape (m, k)
        S = np.zeros((self.m, self.k), dtype=float)

        # Bottom index lookup
        bottom_lookup = {b_id: idx for idx, b_id in enumerate(self.bottom_series)}

        for row_idx, series_name in enumerate(self.all_series):
            lvl = self.level_map[series_name]
            if lvl == "total":
                # Total is sum of all bottom series
                S[row_idx, :] = 1.0
            elif lvl == "region":
                # Find all bottom series belonging to this region
                reg_name = series_name.replace("Region_", "")
                matching_bottoms = bottom_df[bottom_df["region"] == reg_name]["bottom_id"]
                for b_id in matching_bottoms:
                    S[row_idx, bottom_lookup[b_id]] = 1.0
            elif lvl == "store":
                # Find all bottom series belonging to this store
                store_name = series_name.replace("Store_", "")
                matching_bottoms = bottom_df[bottom_df["store_id"] == store_name]["bottom_id"]
                for b_id in matching_bottoms:
                    S[row_idx, bottom_lookup[b_id]] = 1.0
            elif lvl == "category":
                # Find all bottom series belonging to this category
                cat_name = series_name.replace("Category_", "")
                matching_bottoms = bottom_df[bottom_df["category"] == cat_name]["bottom_id"]
                for b_id in matching_bottoms:
                    S[row_idx, bottom_lookup[b_id]] = 1.0
            elif lvl == "bottom":
                # Identity matrix block
                col_idx = bottom_lookup[series_name]
                S[row_idx, col_idx] = 1.0

        self.summing_matrix = SummingMatrix(
            series_names=self.all_series,
            bottom_names=self.bottom_series,
            matrix=S,
            level_map=self.level_map,
        )

    def aggregate_time_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create wide time-series matrix (Date x All Series) matching the hierarchy.

        Returns DataFrame indexed by date with columns matching all_series.
        """
        df_work = df.copy()
        df_work["date"] = pd.to_datetime(df_work["date"])
        df_work["bottom_id"] = df_work["sku_id"] + "_" + df_work["store_id"]

        # Pivot bottom series: index=date, cols=bottom_id
        bottom_pivot = df_work.pivot_table(
            index="date",
            columns="bottom_id",
            values="units_sold",
            aggfunc="sum",
            fill_value=0.0,
        )

        # Reindex to ensure strictly ordered columns matching self.bottom_series
        for b_id in self.bottom_series:
            if b_id not in bottom_pivot.columns:
                bottom_pivot[b_id] = 0.0
        bottom_pivot = bottom_pivot[self.bottom_series]

        # Compute full hierarchy matrix using S: Y = (S @ B^T)^T = B @ S^T
        B = bottom_pivot.values  # (n_dates, k)
        Y = B @ self.summing_matrix.matrix.T  # (n_dates, m)

        full_df = pd.DataFrame(
            Y,
            index=bottom_pivot.index,
            columns=self.all_series,
        )
        return full_df
