import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

import requests
import time

resp = requests.post(
    "http://localhost:8000/scripts/seed",
    json={"symbols": ["ACB", "ADC"]},
    timeout=10,
)
print(f"Trigger: {resp.status_code} -> {resp.text[:200]}")
print("Waiting 40s for seed to complete...")

time.sleep(40)

for sym in ["ACB", "ADC"]:
    resp2 = requests.get(f"http://localhost:8000/company-wiki/{sym}", timeout=5)
    if resp2.status_code == 200:
        data = resp2.json()
        print(f"\n{sym}:")
        print(f"  company_name: {data.get('company_name')}")
        print(f"  sector: {data.get('sector')}")
        print(f"  business_summary: {str(data.get('business_summary',''))[:80]}")
        print(f"  financials: {data.get('financials_snapshot')}")
        print(f"  version: {data.get('version')}")
    else:
        print(f"\n{sym}: not found ({resp2.status_code})")
