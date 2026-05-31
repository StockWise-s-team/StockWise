import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

import psycopg2.extras

from app.synthesis.wiki_repository import WikiRepository

repo = WikiRepository()

print("=== get_company_info ===")
for sym in ["ACB", "ADC", "VNM"]:
    info = repo.get_company_info(sym)
    print(f"  {sym}: {repr(info)[:200]}")

print("\n=== get_ratios ===")
for sym in ["ACB", "ADC", "VNM"]:
    ratios = repo.get_ratios(sym)
    print(f"  {sym}: {repr(ratios)[:200]}")

print("\n=== get_recent_prices ===")
for sym in ["ACB", "ADC"]:
    prices = repo.get_recent_prices(sym, limit=3)
    print(f"  {sym}: count={len(prices)}, data={repr(prices)[:200]}")

print("\n=== get_recent_articles ===")
for sym in ["ACB", "ADC"]:
    arts = repo.get_recent_articles(sym, limit=3)
    print(f"  {sym}: {len(arts)} articles")

print("\n=== get_wiki ===")
for sym in ["ACB", "ADC", "VNM"]:
    wiki = repo.get_wiki(sym)
    print(f"  {sym}: {repr(wiki)[:200] if wiki else None}")
