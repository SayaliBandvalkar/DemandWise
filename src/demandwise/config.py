"""Configuration management for DemandWise.

Provides centralized access to directory paths, model hyperparameters,
simulation defaults, and audit database connection settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class DemandWiseConfig:
    """Master configuration for the DemandWise forecasting and inventory engine."""

    # Project directories
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DEMANDWISE_DATA_DIR", "data")))
    sample_data_dir: Path = field(default_factory=lambda: Path(os.getenv("DEMANDWISE_DATA_DIR", "data")) / "sample")
    artifacts_dir: Path = field(default_factory=lambda: Path(os.getenv("DEMANDWISE_ARTIFACTS_DIR", "artifacts")))
    reports_dir: Path = field(default_factory=lambda: Path(os.getenv("DEMANDWISE_REPORTS_DIR", "reports")))
    docs_dir: Path = field(default_factory=lambda: Path("docs"))

    # SQLite audit database path
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("DEMANDWISE_DB_PATH", "artifacts/demandwise_audit.db"))
    )

    # Determinism
    random_seed: int = int(os.getenv("DEMANDWISE_RANDOM_SEED", "42"))

    # Hierarchy structure configuration
    hierarchy_levels: List[str] = field(
        default_factory=lambda: ["sku_store", "category", "store", "region", "total"]
    )

    # Forecasting defaults
    default_horizon_days: int = 14
    default_test_days: int = 28
    confidence_levels: List[float] = field(default_factory=lambda: [0.80, 0.95])

    # Inventory defaults
    default_review_period_days: int = 7
    default_service_level: float = 0.95
    default_holding_cost_rate: float = 0.20  # 20% annual holding cost rate or per-unit daily
    default_stockout_penalty_multiplier: float = 2.5  # 2.5x lost gross margin

    def ensure_directories(self) -> None:
        """Create all required working directories if they do not exist."""
        for path in [
            self.data_dir,
            self.sample_data_dir,
            self.artifacts_dir,
            self.reports_dir,
            self.docs_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


# Global default configuration instance
config = DemandWiseConfig()
