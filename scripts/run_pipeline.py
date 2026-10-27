"""Command-line pipeline runner for DemandWise end-to-end execution.

Usage:
    python scripts/run_pipeline.py [--generate-data] [--benchmark] [--horizon 14]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure src is on Python search path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from demandwise.data.generator import DatasetConfig, RetailDataGenerator
from demandwise.data.validator import RetailDataValidator
from demandwise.experiments.benchmark import BenchmarkConfig, BenchmarkRunner
from demandwise.governance.audit import AuditLogger


def main():
    parser = argparse.ArgumentParser(description="DemandWise Master Execution Pipeline")
    parser.add_argument("--generate-data", action="store_true", help="Generate fresh synthetic dataset")
    parser.add_argument("--benchmark", action="store_true", default=True, help="Run master benchmark suite")
    parser.add_argument("--horizon", type=int, default=14, help="Forecast horizon days")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    print("=" * 65)
    print(" DEMANDWISE: HIERARCHICAL FORECASTING & INVENTORY INTELLIGENCE")
    print(" Project MDS-07 - Capstone Execution Pipeline")
    print("=" * 65)

    audit = AuditLogger()
    data_path = ROOT_DIR / "data" / "sample" / "retail_hierarchy.csv"

    if args.generate_data or not data_path.exists():
        print(f"\n[1/3] Generating deterministic retail dataset (seed={args.seed})...")
        cfg = DatasetConfig(random_seed=args.seed)
        gen = RetailDataGenerator(cfg)
        df = gen.generate()
        data_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(data_path, index=False)
        print(f"Dataset generated with shape {df.shape} and saved to {data_path}")

        validator = RetailDataValidator()
        res = validator.validate(df)
        print(f"Validation status: {'PASSED' if res.is_valid else 'FAILED'} (Zero demand: {res.zero_demand_percentage:.1f}%)")
        audit.log_event("DATA_INGESTION", "Generate synthetic retail dataset", res.summary())

    if args.benchmark:
        print(f"\n[2/3] Executing scientific benchmark suite (horizon={args.horizon})...")
        bench_runner = BenchmarkRunner()
        payload = bench_runner.run_full_suite()
        audit.log_event(
            "EXPERIMENT_RUN",
            "Master Benchmark Suite Execution",
            {"runtime_sec": payload["runtime_seconds"], "models_tested": len(payload["models_benchmark"])},
        )

    print("\n[3/3] Execution finished successfully.")
    print("To launch the interactive dashboard, run:")
    print("    .\\.venv\\Scripts\\streamlit.exe run app.py")
    print("=" * 65)


if __name__ == "__main__":
    main()
