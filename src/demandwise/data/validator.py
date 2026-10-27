"""Data validation and quality assessment engine for DemandWise."""

from __future__ import annotations

from typing import List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from demandwise.data.schema import ValidationIssue, ValidationResult


class RetailDataValidator:
    """Validates raw retail dataframes against required hierarchical and transactional schemas."""

    REQUIRED_COLUMNS = [
        "date",
        "sku_id",
        "category",
        "store_id",
        "region",
        "units_sold",
        "unit_price",
        "unit_cost",
    ]

    OPTIONAL_COLUMNS = [
        "inventory_on_hand",
        "lead_time_days",
        "is_promotion",
        "is_holiday",
    ]

    def __init__(self, strict: bool = False):
        self.strict = strict

    def validate(self, df: pd.DataFrame) -> ValidationResult:
        """Execute full validation checks on the supplied DataFrame."""
        issues: List[ValidationIssue] = []

        if df is None or len(df) == 0:
            return ValidationResult(
                is_valid=False,
                total_records=0,
                num_skus=0,
                num_stores=0,
                num_categories=0,
                num_regions=0,
                issues=[
                    ValidationIssue(
                        severity="ERROR",
                        message="Input dataset is empty or None.",
                        count=0,
                    )
                ],
            )

        # 1. Column existence checks
        missing_cols = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing_cols:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="columns",
                    message=f"Missing mandatory columns: {missing_cols}",
                    count=len(missing_cols),
                )
            )
            return ValidationResult(
                is_valid=False,
                total_records=len(df),
                num_skus=0,
                num_stores=0,
                num_categories=0,
                num_regions=0,
                issues=issues,
            )

        # Work on a copy for non-destructive inspection
        df_check = df.copy()

        # 2. Date parsing check
        try:
            df_check["parsed_date"] = pd.to_datetime(df_check["date"])
            date_min = df_check["parsed_date"].min().strftime("%Y-%m-%d")
            date_max = df_check["parsed_date"].max().strftime("%Y-%m-%d")
        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="date",
                    message=f"Date column could not be parsed to datetime: {str(e)}",
                    count=len(df_check),
                )
            )
            return ValidationResult(
                is_valid=False,
                total_records=len(df),
                num_skus=0,
                num_stores=0,
                num_categories=0,
                num_regions=0,
                issues=issues,
            )

        # 3. Missing values check
        missing_counts = {}
        for col in self.REQUIRED_COLUMNS:
            n_missing = int(df_check[col].isna().sum())
            if n_missing > 0:
                missing_counts[col] = n_missing
                issues.append(
                    ValidationIssue(
                        severity="ERROR",
                        field=col,
                        message=f"Column '{col}' has {n_missing} missing (NaN/Null) values.",
                        count=n_missing,
                    )
                )

        # 4. Quantity & price positivity checks
        neg_units = int((df_check["units_sold"] < 0).sum())
        if neg_units > 0:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="units_sold",
                    message=f"Found {neg_units} records with negative units_sold.",
                    count=neg_units,
                )
            )

        non_pos_price = int((df_check["unit_price"] <= 0).sum())
        if non_pos_price > 0:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="unit_price",
                    message=f"Found {non_pos_price} records with unit_price <= 0.",
                    count=non_pos_price,
                )
            )

        non_pos_cost = int((df_check["unit_cost"] <= 0).sum())
        if non_pos_cost > 0:
            issues.append(
                ValidationIssue(
                    severity="WARNING",
                    field="unit_cost",
                    message=f"Found {non_pos_cost} records with unit_cost <= 0.",
                    count=non_pos_cost,
                )
            )

        # 5. Duplicate primary key check (date + sku_id + store_id must be unique)
        dup_mask = df_check.duplicated(subset=["date", "sku_id", "store_id"], keep=False)
        dup_count = int(dup_mask.sum())
        if dup_count > 0:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="primary_key",
                    message=f"Found {dup_count} duplicate records for (date, sku_id, store_id).",
                    count=dup_count,
                )
            )

        # 6. Hierarchy consistency checks
        # SKU -> Category must be 1-to-1
        sku_cat_map = df_check.groupby("sku_id")["category"].nunique()
        multi_cat_skus = sku_cat_map[sku_cat_map > 1].index.tolist()
        if multi_cat_skus:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="category",
                    message=f"Inconsistent hierarchy: SKUs mapped to multiple categories: {multi_cat_skus}",
                    count=len(multi_cat_skus),
                )
            )

        # Store -> Region must be 1-to-1
        store_reg_map = df_check.groupby("store_id")["region"].nunique()
        multi_reg_stores = store_reg_map[store_reg_map > 1].index.tolist()
        if multi_reg_stores:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    field="region",
                    message=f"Inconsistent hierarchy: Stores mapped to multiple regions: {multi_reg_stores}",
                    count=len(multi_reg_stores),
                )
            )

        # 7. Missing dates per series check
        expected_dates = pd.date_range(start=date_min, end=date_max, freq="D")
        n_expected_dates = len(expected_dates)
        series_date_counts = df_check.groupby(["sku_id", "store_id"])["parsed_date"].nunique()
        missing_date_series = series_date_counts[series_date_counts < n_expected_dates]
        missing_dates_count = int((n_expected_dates - series_date_counts).clip(lower=0).sum())

        if len(missing_date_series) > 0:
            issues.append(
                ValidationIssue(
                    severity="WARNING",
                    field="date",
                    message=f"{len(missing_date_series)} series have missing dates (total {missing_dates_count} missing date-slots).",
                    count=missing_dates_count,
                )
            )

        # Zero demand ratio
        zero_demand_count = int((df_check["units_sold"] == 0).sum())
        zero_demand_pct = (zero_demand_count / max(1, len(df_check))) * 100.0

        # Overall validity: valid if NO 'ERROR' level issues
        has_errors = any(issue.severity == "ERROR" for issue in issues)

        return ValidationResult(
            is_valid=(not has_errors),
            total_records=len(df),
            num_skus=int(df_check["sku_id"].nunique()),
            num_stores=int(df_check["store_id"].nunique()),
            num_categories=int(df_check["category"].nunique()),
            num_regions=int(df_check["region"].nunique()),
            date_min=date_min,
            date_max=date_max,
            missing_dates_count=missing_dates_count,
            duplicate_rows_count=dup_count,
            negative_quantity_count=neg_units,
            missing_values=missing_counts,
            zero_demand_percentage=zero_demand_pct,
            issues=issues,
        )
