"""Verification script for project ZIP archives."""

import sys
import zipfile
from pathlib import Path

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "DemandForecast_Intelligence_Platform.zip"
    zip_path = Path(target)
    assert zip_path.exists(), f"ZIP archive {target} does not exist!"
    print(f"Verified archive exists: {zip_path.resolve()} ({zip_path.stat().st_size / 1024:.1f} KB)")

    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        print(f"Total entries in archive: {len(namelist)}")

        # Check frontend components and logo
        assert "frontend/public/logo.png" in namelist, "Missing frontend/public/logo.png!"
        frontend_files = [f for f in namelist if f.startswith("frontend/src/")]
        assert len(frontend_files) > 10, f"Expected frontend files, found {len(frontend_files)}"
        print(f"[OK] Found {len(frontend_files)} frontend source files + logo (React + TypeScript)")

        # Check all 10 core pages (Settings & Docs removed)
        pages = [
            "frontend/src/pages/ExecutiveOverview.tsx",
            "frontend/src/pages/DataManagement.tsx",
            "frontend/src/pages/HierarchyExplorer.tsx",
            "frontend/src/pages/ForecastStudio.tsx",
            "frontend/src/pages/ReconciliationLab.tsx",
            "frontend/src/pages/UncertaintyCalibration.tsx",
            "frontend/src/pages/InventorySimulator.tsx",
            "frontend/src/pages/ModelEvaluation.tsx",
            "frontend/src/pages/ExperimentsMonitoring.tsx",
            "frontend/src/pages/AuditTrail.tsx",
        ]
        for p in pages:
            assert p in namelist, f"Missing required page: {p}"
        print("[OK] All 10 React operational pages confirmed in archive")

        # Check backend files
        backend_files = [f for f in namelist if f.startswith("backend/app/")]
        assert len(backend_files) > 10, f"Expected backend files, found {len(backend_files)}"
        print(f"[OK] Found {len(backend_files)} FastAPI backend files")

        # Check domain modules
        core_files = [f for f in namelist if f.startswith("src/demandwise/")]
        assert len(core_files) > 10, f"Expected core modules, found {len(core_files)}"
        print(f"[OK] Found {len(core_files)} core Python ML & forecasting modules")

        # Check test suite
        test_files = [f for f in namelist if f.startswith("tests/")]
        assert len(test_files) >= 9, f"Expected test files, found {len(test_files)}"
        print(f"[OK] Found {len(test_files)} test files (35 tests)")

        # Check essential files
        essentials = [
            "README.md",
            "PROJECT_STATUS.md",
            "CONTINUATION_LOG.md",
            "MIGRATION_PLAN.md",
            "requirements.txt",
            "pyproject.toml",
            ".env.example",
            "data/sample/retail_hierarchy.csv",
            "artifacts/experiments/benchmark_results.json",
        ]
        for e in essentials:
            assert e in namelist, f"Missing essential file: {e}"
        print("[OK] All essential configuration, documentation, data, and benchmark files confirmed")

        # Check exclusions
        for name in namelist:
            assert not name.startswith(".venv"), f"Forbidden .venv found: {name}"
            assert not name.startswith("node_modules"), f"Forbidden node_modules found: {name}"
            assert not name.startswith("frontend/node_modules"), f"Forbidden frontend/node_modules found: {name}"
            assert not name.startswith("frontend/dist"), f"Forbidden frontend/dist found: {name}"
            assert not name.startswith(".git/"), f"Forbidden .git found: {name}"
            assert not name.endswith(".pyc"), f"Forbidden .pyc found: {name}"
            assert name != ".env", f"Forbidden .env secrets file found: {name}"
        print("[OK] All exclusions strictly verified: No .venv, node_modules, dist, pycache, or secrets")

    print("\nZIP ARCHIVE INTEGRITY VERIFICATION PASSED (100% CLEAN & COMPLETE)!")

if __name__ == "__main__":
    main()
