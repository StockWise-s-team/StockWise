import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

from app.synthesis.wiki_repository import WikiRepository
from app.config import settings
import psycopg2

repo = WikiRepository()

print("=== get_company_info ===")
for sym in ["ACB", "ADC"]:
    info = repo.get_company_info(sym)
    print(f"  {sym}: {repr(info)[:300]}")

print("\n=== get_ratios ===")
for sym in ["ACB", "ADC"]:
    ratios = repo.get_ratios(sym)
    print(f"  {sym}: {repr(ratios)[:200]}")

print("\n=== Direct DB query ===")
conn = psycopg2.connect(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    dbname=settings.POSTGRES_DB,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
)
cur = conn.cursor()
for sym in ["ACB", "ADC"]:
    cur.execute("SELECT symbol, company_name, sector FROM company_info WHERE symbol = %s", (sym,))
    row = cur.fetchone()
    print(f"  company_info {sym}: {row}")

    cur.execute("SELECT symbol, pe_ratio, pb_ratio, roe FROM stock_ratios WHERE symbol = %s", (sym,))
    row = cur.fetchone()
    print(f"  stock_ratios {sym}: {row}")
conn.close()
