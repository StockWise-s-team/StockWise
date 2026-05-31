import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

import requests

for sym in ["ACB", "ADC"]:
    print(f"\n=== {sym} ===")
    resp = requests.get(f"http://localhost:8000/company-wiki/{sym}", timeout=5)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Keys: {list(data.keys())}")
        print(f"company_name: {repr(data.get('company_name'))}")
        print(f"sector: {repr(data.get('sector'))}")
        print(f"business_summary: {repr(str(data.get('business_summary',''))[:100])}")
        print(f"financials_snapshot: {repr(data.get('financials_snapshot'))}")
        print(f"key_risks: {repr(data.get('key_risks'))}")
        print(f"version: {data.get('version')}")
    else:
        print(f"Error: {resp.status_code} -> {resp.text}")

    # Also check company_info directly
    resp2 = requests.get(f"http://localhost:8000/company-info/{sym}", timeout=5)
    print(f"  /company-info/{sym}: {resp2.status_code} -> {resp2.text[:200]}")
