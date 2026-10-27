"""Backend configuration settings for DemandWise FastAPI service."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Settings:
    """Application configuration settings."""

    app_name: str = "DemandWise API"
    app_version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
    serve_frontend: bool = os.getenv("SERVE_FRONTEND", "false").lower() in ("true", "1")

    # Root directories (resolved relative to workspace)
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent)

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def sample_data_dir(self) -> Path:
        return self.base_dir / "data" / "sample"

    @property
    def artifacts_dir(self) -> Path:
        return self.base_dir / "artifacts"

    @property
    def db_path(self) -> Path:
        return self.base_dir / "artifacts" / "demandwise_audit.db"

    # CORS configuration for React frontend (Vite & Next/React ports)
    cors_origins: List[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
            ).split(",")
            if origin.strip()
        ]
    )


settings = Settings()
