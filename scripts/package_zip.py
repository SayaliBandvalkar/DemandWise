"""Archive packager for DemandWise capstone project deliverables.

Creates a clean, portable ZIP archive named DemandWise_MDS07_Final.zip.
Excludes virtual environments, pycache, pytest caches, git internals, and large logs.
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
    ".vscode",
    "DemandWise_MDS07_Final.zip",
    ".coverage",
    "htmlcov",
}


def should_exclude(rel_path: str) -> bool:
    """Check if relative path matches any exclude pattern."""
    parts = Path(rel_path).parts
    for p in parts:
        if p in EXCLUDE_PATTERNS or p.endswith(".pyc") or p.endswith(".log"):
            return True
    return False


def create_zip(
    source_dir: str = ".",
    output_filename: str = "DemandWise_MDS07_Final.zip",
) -> str:
    """Create clean ZIP archive of the project workspace."""
    source_path = Path(source_dir).resolve()
    output_path = source_path / output_filename

    print(f"Creating project package: {output_path}")
    file_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            # Modify dirs in-place to avoid traversing into excluded folders
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
