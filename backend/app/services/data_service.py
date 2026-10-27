"""Data access and hierarchy caching service."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

from backend.app.core.config import settings
from demandwise.data.generator import DatasetConfig, RetailDataGenerator
from demandwise.data.validator import RetailDataValidator
from demandwise.forecasting.hierarchy import HierarchyTree
from demandwise.governance.audit import AuditLogger

audit_logger = AuditLogger(db_path=str(settings.db_path))


class DataService:
    """Manages transactional retail data ingestion, validation, and hierarchy representation."""

    _cached_df: Optional[pd.DataFrame] = None
    _cached_tree: Optional[HierarchyTree] = None
    _cached_wide_df: Optional[pd.DataFrame] = None

    @classmethod
    def get_dataset_path(cls) -> Path:
        return settings.sample_data_dir / "retail_hierarchy.csv"

    @classmethod
    def load_dataset(cls, force_reload: bool = False) -> pd.DataFrame:
        """Load retail dataset from disk or memory cache."""
        if cls._cached_df is not None and not force_reload:
            return cls._cached_df

        file_path = cls.get_dataset_path()
        if not file_path.exists():
            cls.generate_demo_dataset()

        df = pd.read_csv(file_path)
        df["date"] = pd.to_datetime(df["date"])
        cls._cached_df = df
        cls._cached_tree = None
        cls._cached_wide_df = None
        return df

    @classmethod
    def get_hierarchy_tree(cls) -> Tuple[HierarchyTree, pd.DataFrame]:
        """Get or initialize the HierarchyTree and wide matrix."""
        df = cls.load_dataset()
        if cls._cached_tree is None or cls._cached_wide_df is None:
            tree = HierarchyTree(df)
            wide_df = tree.aggregate_time_series(df)
            cls._cached_tree = tree
            cls._cached_wide_df = wide_df
        return cls._cached_tree, cls._cached_wide_df

    @classmethod
    def generate_demo_dataset(
        cls,
        num_skus: int = 12,
        num_stores: int = 4,
        num_regions: int = 2,
        random_seed: int = 42,
    ) -> pd.DataFrame:
        """Generate deterministic synthetic dataset and save to disk."""
        cfg = DatasetConfig(
            num_skus=num_skus,
            num_stores=num_stores,
            num_regions=num_regions,
            random_seed=random_seed,
        )
        gen = RetailDataGenerator(cfg)
        df = gen.generate()

        out_path = cls.get_dataset_path()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)

        cls._cached_df = df
        cls._cached_tree = None
        cls._cached_wide_df = None

        audit_logger.log_event(
            event_type="DATA_INGESTION",
            action="Generate synthetic retail dataset",
            details={"rows": len(df), "num_skus": num_skus, "num_stores": num_stores},
        )
        return df

    @classmethod
    def validate_current_dataset(cls) -> Dict:
        """Execute validation suite on the active dataset."""
        df = cls.load_dataset()
        validator = RetailDataValidator()
        res = validator.validate(df)
        return {
            "is_valid": res.is_valid,
            "total_records": res.total_records,
            "num_skus": res.num_skus,
            "num_stores": res.num_stores,
            "num_categories": res.num_categories,
            "num_regions": res.num_regions,
            "missing_dates_count": res.missing_dates_count,
            "duplicate_rows_count": res.duplicate_rows_count,
            "negative_quantity_count": res.negative_quantity_count,
            "zero_demand_percentage": round(res.zero_demand_percentage, 2),
            "missing_values": res.missing_values,
            "issues": [issue.dict() for issue in res.issues],
        }

    @classmethod
    def upload_dataset(cls, file_content: bytes, filename: str) -> Dict:
        """Parse, validate, and store uploaded CSV dataset."""
        df = pd.read_csv(io.BytesIO(file_content))
        validator = RetailDataValidator()
        res = validator.validate(df)

        if not res.is_valid:
            audit_logger.log_event(
                event_type="DATA_INGESTION",
                action=f"Upload rejected for {filename}",
                details={"errors": [i.message for i in res.issues if i.severity == "ERROR"]},
                status="ERROR",
            )
            return {"success": False, "summary": res.summary(), "issues": [i.dict() for i in res.issues]}

        # Save uploaded file
        out_path = cls.get_dataset_path()
        df.to_csv(out_path, index=False)
        cls._cached_df = df
        cls._cached_tree = None
        cls._cached_wide_df = None

        audit_logger.log_event(
            event_type="DATA_INGESTION",
            action=f"Upload accepted for {filename}",
            details={"rows": len(df), "skus": res.num_skus, "stores": res.num_stores},
            status="SUCCESS",
        )
        return {"success": True, "summary": res.summary(), "issues": [i.dict() for i in res.issues]}
