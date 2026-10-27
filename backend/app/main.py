"""DemandWise FastAPI Backend Application.

Project MDS-07: Hierarchical Demand Forecasting with Probabilistic Reconciliation
and Inventory Decisions.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure workspace root and src are accessible in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.services.data_service import DataService

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify dataset and hierarchy initialization on service start."""
    try:
        DataService.load_dataset()
    except Exception as e:
        print(f"Warning on startup data initialization: {e}")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise REST API for Hierarchical Demand Forecasting, Reconciliation & Inventory Intelligence (MDS-07)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for React Vite / Dev Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check():
    """Service health and diagnostic status."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": "production" if not settings.debug else "development",
    }


# Optional production frontend SPA serving (when SERVE_FRONTEND=true)
dist_dir = BASE_DIR / "frontend" / "dist"
if settings.serve_frontend and dist_dir.exists() and (dist_dir / "index.html").exists():
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        potential_file = dist_dir / full_path
        if full_path and potential_file.is_file():
            return FileResponse(str(potential_file))
        return FileResponse(str(dist_dir / "index.html"))
else:
    @app.get("/", include_in_schema=False)
    def root():
        """Redirect root path to interactive Swagger API documentation."""
        return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
