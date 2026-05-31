import sys
sys.path.insert(0, r"d:\StockWise\data-pipeline")

from app.config import settings
import psycopg2

conn = psycopg2.connect(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    dbname=settings.POSTGRES_DB,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
)
cur = conn.cursor()

# Get all unique symbols from stock_prices
cur.execute("SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol")
existing = {r[0] for r in cur.fetchall()}

# Get symbols already in tracked_symbols
cur.execute("SELECT symbol FROM tracked_symbols")
tracked = {r[0] for r in cur.fetchall()}

to_add = existing - tracked
print(f"Already tracked: {len(tracked)}")
print(f"Total in stock_prices: {len(existing)}")
print(f"Need to add: {len(to_add)}")

if to_add:
    for sym in sorted(to_add):
        cur.execute(
            "INSERT INTO tracked_symbols (symbol) VALUES (%s) ON CONFLICT DO NOTHING",
            (sym,),
        )
    conn.commit()
    print(f"Added {len(to_add)} symbols: {sorted(to_add)}")

# Verify
cur.execute("SELECT COUNT(*) FROM tracked_symbols")
print(f"Total in tracked_symbols: {cur.fetchone()[0]}")

conn.close()
