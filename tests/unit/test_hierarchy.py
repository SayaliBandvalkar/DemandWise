"""Unit tests for mathematical hierarchy and summing matrix S."""

import pytest
import numpy as np
import pandas as pd

from demandwise.data.generator import DatasetConfig, RetailDataGenerator
from demandwise.forecasting.hierarchy import HierarchyTree, SummingMatrix


@pytest.fixture
def sample_retail_df():
    cfg = DatasetConfig(
        start_date="2023-01-01",
        end_date="2023-01-14",
        num_skus=4,
        num_stores=2,
        num_regions=2,
        random_seed=42,
    )
    return RetailDataGenerator(cfg).generate()


def test_hierarchy_tree_construction(sample_retail_df):
    """Test Summing Matrix dimensions and aggregation relationships."""
    tree = HierarchyTree(sample_retail_df)

    k = tree.k  # 4 SKUs * 2 Stores = 8 bottom series
    m = tree.m  # 1 (Total) + 2 (Regions) + 2 (Stores) + 4 (Categories) + 8 (Bottom) = 17 series
    assert k == 8
    assert m == 17
    assert tree.summing_matrix.matrix.shape == (m, k)


def test_hierarchy_time_series_aggregation_coherence(sample_retail_df):
    """Verify that aggregate_time_series produces exact mathematical coherence across all dates."""
    tree = HierarchyTree(sample_retail_df)
    wide_df = tree.aggregate_time_series(sample_retail_df)

    S = tree.summing_matrix.matrix
    k = tree.k

    for _, row in wide_df.iterrows():
        y_vec = row.values
        is_coherent, max_err = tree.summing_matrix.is_coherent(y_vec, tolerance=1e-5)
        assert is_coherent is True
        assert max_err < 1e-5
