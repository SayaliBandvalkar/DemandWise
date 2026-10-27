"""Data schemas and validation structures for DemandWise retail datasets."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class RetailRecord(BaseModel):
    """Schema for an individual daily retail sales and inventory record."""

    date: date
    sku_id: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    store_id: str = Field(..., min_length=1, max_length=50)
    region: str = Field(..., min_length=1, max_length=50)
    units_sold: float = Field(..., ge=0.0)
    unit_price: float = Field(..., gt=0.0)
    unit_cost: float = Field(..., gt=0.0)
    inventory_on_hand: float = Field(..., ge=0.0)
    lead_time_days: int = Field(..., ge=1, le=180)
    is_promotion: int = Field(default=0, ge=0, le=1)
    is_holiday: int = Field(default=0, ge=0, le=1)

    @field_validator("unit_cost")
    @classmethod
    def validate_cost_price(cls, v: float, info: Any) -> float:
        # Note: Cost should typically be <= price, but allow promotional clearance
        return v


class ValidationIssue(BaseModel):
    """Represents a specific validation error or warning."""

    severity: str  # 'ERROR' or 'WARNING'
    field: Optional[str] = None
    message: str
    row_indices: Optional[List[int]] = None
    count: int = 1


class ValidationResult(BaseModel):
    """Comprehensive diagnostics result from schema and data quality validation."""

    is_valid: bool
    total_records: int
    num_skus: int
    num_stores: int
    num_categories: int
    num_regions: int
    date_min: Optional[str] = None
    date_max: Optional[str] = None
    missing_dates_count: int = 0
    duplicate_rows_count: int = 0
    negative_quantity_count: int = 0
    missing_values: Dict[str, int] = Field(default_factory=dict)
    zero_demand_percentage: float = 0.0
    issues: List[ValidationIssue] = Field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        """Return a compact dictionary summary for reporting and dashboards."""
        return {
            "valid": self.is_valid,
            "records": self.total_records,
            "hierarchy_size": {
                "skus": self.num_skus,
                "stores": self.num_stores,
                "categories": self.num_categories,
                "regions": self.num_regions,
            },
            "date_range": f"{self.date_min} to {self.date_max}",
            "missing_dates": self.missing_dates_count,
            "zero_demand_pct": f"{self.zero_demand_percentage:.1f}%",
            "issues_count": len(self.issues),
        }
