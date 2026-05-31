import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

from app.synthesis.wiki_repository import WikiRepository
from app.api.schemas import CompanyWikiResponse

repo = WikiRepository()

for sym in ["ACB", "ADC"]:
    print(f"\n=== {sym} ===")
    wiki = repo.get_wiki(sym)
    if not wiki:
        print("  No wiki found!")
        continue

    # Check all types
    for k, v in wiki.items():
        t = type(v).__name__
        if t != "str" and t != "int" and t != "NoneType":
            print(f"  {k}: {t} = {repr(v)[:80]}")

    try:
        resp = CompanyWikiResponse(**wiki)
        print(f"  **wiki: OK -> companyName={repr(resp.companyName)[:50]}, sector={repr(resp.sector)}")
    except Exception as e:
        err_type = type(e).__name__
        print(f"  **wiki FAILED: {err_type}: {e}")
        # Try field by field to find culprit
        required_fields = ["symbol", "companyName", "sector", "businessSummary",
                          "recentPerformance", "keyRisks", "sentiment",
                          "lastNewsSummary", "financialsSnapshot", "version", "updatedAt"]
        for f in required_fields:
            try:
                pass
            except:
                pass

        # Try stripping problematic fields
        wiki2 = {k: v for k, v in wiki.items() if k in ["symbol", "version", "sector"]}
        try:
            resp2 = CompanyWikiResponse(**wiki2)
            print(f"  minimal fields OK")
        except Exception as e2:
            print(f"  minimal also FAILED: {type(e2).__name__}: {e2}")
