"""Dataset management and data quality API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.schemas.dataset import (
    DataQualityResponse,
    DatasetSummaryResponse,
    GenerateDemoRequest,
)
from backend.app.services.data_service import DataService

router = APIRouter()


@router.get("", response_model=DatasetSummaryResponse)
def get_current_dataset_summary():
    """Get metadata and statistical summary of the active dataset."""
    df = DataService.load_dataset()
    tree, _ = DataService.get_hierarchy_tree()

    zero_count = int((df["units_sold"] == 0).sum())
    total_rev = float((df["units_sold"] * df["unit_price"]).sum())
    total_units = float(df["units_sold"].sum())

    return DatasetSummaryResponse(
        name="retail_hierarchical_dataset",
        file_path=str(DataService.get_dataset_path()),
        total_records=len(df),
        num_skus=int(df["sku_id"].nunique()),
        num_stores=int(df["store_id"].nunique()),
        num_categories=int(df["category"].nunique()),
        num_regions=int(df["region"].nunique()),
        date_min=df["date"].min().strftime("%Y-%m-%d"),
        date_max=df["date"].max().strftime("%Y-%m-%d"),
        zero_demand_percentage=round((zero_count / max(1, len(df))) * 100.0, 2),
        total_revenue=round(total_rev, 2),
        total_units=round(total_units, 1),
    )


@router.get("/quality", response_model=DataQualityResponse)
def get_dataset_quality():
    """Execute validation suite and return detailed data quality diagnostics."""
    diagnostics = DataService.validate_current_dataset()
    return DataQualityResponse(**diagnostics)


@router.post("/generate-demo", response_model=DatasetSummaryResponse)
def generate_demo_dataset(req: GenerateDemoRequest):
    """Regenerate deterministic retail hierarchy dataset with specified dimensions."""
    df = DataService.generate_demo_dataset(
        num_skus=req.num_skus,
        num_stores=req.num_stores,
        num_regions=req.num_regions,
        random_seed=req.random_seed,
    )
    return get_current_dataset_summary()


@router.post("/upload")
async def upload_dataset_csv(file: UploadFile = File(...)):
    """Upload CSV dataset, validate schema, and activate if valid."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    content = await file.read()
    result = DataService.upload_dataset(content, file.filename)
    if not result["success"]:
        raise HTTPException(status_code=422, detail=result)
    return {"message": "Dataset uploaded and activated successfully.", "details": result}
