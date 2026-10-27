"""Runtime live server verification script."""

import subprocess
import sys
import time
import urllib.request
import json

def main():
    print("Starting FastAPI Uvicorn server on port 8000...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--port", "8000", "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Wait for server to become responsive
        max_retries = 25
        healthy = False
        for i in range(max_retries):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as resp:
                    if resp.status == 200:
                        healthy = True
                        break
            except Exception:
                pass

        if not healthy:
            print("ERROR: Server failed to respond on http://127.0.0.1:8000/health within 12s")
            proc.kill()
            sys.exit(1)

        print("SUCCESS: /health returned HTTP 200")

        # Test /docs
        with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=3) as resp:
            assert resp.status == 200
            print("SUCCESS: /docs (OpenAPI Swagger UI) returned HTTP 200")

        # Test /api/v1/datasets
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/datasets", timeout=5) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            print(f"SUCCESS: /api/v1/datasets returned {data['total_records']} records across {data['num_skus']} SKUs")

        # Test /api/v1/hierarchy
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/hierarchy", timeout=5) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            print(f"SUCCESS: /api/v1/hierarchy returned {data['m_total_series']} total series ({data['k_bottom_series']} bottom series)")

        # Test POST /api/v1/forecasts
        req_data = json.dumps({"series_name": "Total", "model_name": "naive", "horizon": 7}).encode()
        req = urllib.request.Request("http://127.0.0.1:8000/api/v1/forecasts", data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            print(f"SUCCESS: /api/v1/forecasts returned forecast for {data['series_name']} with MAE={data['metrics']['mae']:.2f}")

        # Test POST /api/v1/inventory/simulations
        inv_data = json.dumps({"sku_id": "SKU_001", "store_id": "Store_01", "lead_time_days": 3, "review_period_days": 5, "target_service_level": 0.95}).encode()
        req = urllib.request.Request("http://127.0.0.1:8000/api/v1/inventory/simulations", data=inv_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            print(f"SUCCESS: /api/v1/inventory/simulations returned {len(data['policies_summary'])} policy summaries")

        print("\nALL LIVE RUNTIME ENDPOINTS VERIFIED SUCCESSFULLY (100% OPERATIONAL)!")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
