"""Archive packager for DemandWise React + FastAPI migrated deliverables.

Creates a clean, portable ZIP archive named DemandWise_React_FastAPI_Final.zip.
Excludes virtual environments, node_modules, build artifacts, pycache, git internals, and secrets.
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path


EXCLUDE_PATTERNS = {
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".idea",
    "node_modules",
    "dist",
    ".coverage",
    "htmlcov",
    ".tmp",
}

EXCLUDE_EXACT_NAMES = {
    "DemandWise_React_FastAPI_Final.zip",
    "DemandWise_MDS07_Final.zip",
    "DemandWise_Streamlit_Backup.zip",
    ".env",
}


def should_exclude(rel_path: str) -> bool:
    """Check if relative path matches any exclude pattern."""
    path_obj = Path(rel_path)
    if path_obj.name in EXCLUDE_EXACT_NAMES or path_obj.name.endswith(".zip"):
        return True
    for part in path_obj.parts:
        if part in EXCLUDE_PATTERNS or part.endswith(".pyc") or part.endswith(".log") or part.endswith(".zip"):
            return True
    return False


def create_zip(
    source_dir: str = ".",
    output_filename: str = "DemandForecast_Intelligence_Platform.zip",
) -> str:
    """Create clean ZIP archive of the complete React + FastAPI workspace."""
    source_path = Path(source_dir).resolve()
    output_path = source_path / output_filename

    print(f"Creating project package: {output_path}")
    file_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_PATTERNS]

            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(source_path)

                if should_exclude(str(rel_path)):
                    continue

                zipf.write(full_path, arcname=str(rel_path))
                file_count += 1
                total_uncompressed_bytes += full_path.stat().st_size

    archive_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Archive successfully created: {output_filename}")
    print(f"Files packaged: {file_count}")
    print(f"Archive size:   {archive_size_mb:.2f} MB")
    print(f"Uncompressed:   {total_uncompressed_bytes / (1024 * 1024):.2f} MB")
    return str(output_path)


if __name__ == "__main__":
    create_zip()
