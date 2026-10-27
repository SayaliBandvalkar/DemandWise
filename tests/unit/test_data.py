"""Unit tests for synthetic data generation and schema validation."""

import pytest
import pandas as pd
import numpy as np

from demandwise.data.generator import DatasetConfig, RetailDataGenerator
from demandwise.data.validator import RetailDataValidator


def test_generator_shape_and_hierarchy():
    """Verify generator output dimensions, columns, and deterministic reproducibility."""
    cfg = DatasetConfig(
        start_date="2023-01-01",
        end_date="2023-01-31",
        num_skus=4,
        num_stores=2,
        num_regions=2,
        random_seed=42,
    )
    gen = RetailDataGenerator(cfg)
    df1 = gen.generate()
    df2 = gen.generate()

    assert len(df1) == 31 * 4 * 2  # 31 days * 4 SKUs * 2 stores = 248 rows
    assert list(df1.columns) == [
        "date",
        "sku_id",
        "category",
        "store_id",
        "region",
        "units_sold",
        "unit_price",
        "unit_cost",
        "inventory_on_hand",
        "lead_time_days",
        "is_promotion",
        "is_holiday",
    ]
    # Determinism
    pd.testing.assert_frame_equal(df1, df2)


def test_validator_valid_dataset():
    """Test that a compliant dataset passes validation."""
    cfg = DatasetConfig(
        start_date="2023-01-01",
        end_date="2023-01-14",
        num_skus=3,
        num_stores=2,
        random_seed=42,
    )
    gen = RetailDataGenerator(cfg)
    df = gen.generate()

    validator = RetailDataValidator()
    result = validator.validate(df)

    assert result.is_valid is True
    assert result.total_records == len(df)
    assert result.num_skus == 3
    assert result.num_stores == 2
    assert result.negative_quantity_count == 0


def test_validator_detects_negative_units():
    """Test that validator catches invalid negative demand values."""
    cfg = DatasetConfig(
        start_date="2023-01-01",
        end_date="2023-01-07",
        num_skus=2,
        num_stores=1,
        random_seed=42,
    )
    df = RetailDataGenerator(cfg).generate()
    # Inject negative sales
    df.loc[0, "units_sold"] = -10.0

    validator = RetailDataValidator()
    result = validator.validate(df)

    assert result.is_valid is False
    assert result.negative_quantity_count > 0


def test_validator_detects_duplicates():
    """Test that duplicate primary keys (date, sku_id, store_id) are caught."""
    cfg = DatasetConfig(
        start_date="2023-01-01",
        end_date="2023-01-05",
        num_skus=2,
        num_stores=1,
        random_seed=42,
    )
    df = RetailDataGenerator(cfg).generate()
    # Duplicate first row
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)

    validator = RetailDataValidator()
    result = validator.validate(df)

    assert result.is_valid is False
    assert result.duplicate_rows_count > 0
