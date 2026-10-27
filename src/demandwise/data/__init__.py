"""Data ingestion, synthetic generation, and schema validation module."""

from demandwise.data.generator import RetailDataGenerator
from demandwise.data.schema import RetailRecord, ValidationResult
from demandwise.data.validator import RetailDataValidator

__all__ = ["RetailDataGenerator", "RetailRecord", "ValidationResult", "RetailDataValidator"]
