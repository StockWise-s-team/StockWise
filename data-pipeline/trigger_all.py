import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

import requests
import time

# First trigger synthesis
print("Triggering synthesis for all tracked symbols...")
resp = requests.post(
    "http://localhost:8000/synthesis/trigger",
    json={},
    timeout=10,
)
print(f"Synthesis trigger: {resp.status_code} -> {resp.text[:200]}")
print("\nWaiting 90s for synthesis to complete...")
time.sleep(90)

# Check wiki for a few
print("\nWiki status:")
for sym in ["BID", "VCB", "HPG", "MWG", "SSI", "VNM"]:
    r = requests.get(f"http://localhost:8000/company-wiki/{sym}", timeout=5)
    if r.status_code == 200:
        d = r.json()
        cn = d.get('companyName', 'N/A')
        v = d.get('version', '?')
        print(f"  {sym}: {cn[:50]} (v{v})")
    else:
        print(f"  {sym}: {r.status_code} - {r.text[:80]}")
