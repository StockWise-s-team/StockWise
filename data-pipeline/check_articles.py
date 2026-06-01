"""Check DB and Qdrant for articles from the previous pipeline run."""
import logging
import os
import sys

# Fix stdout encoding for Vietnamese characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import psycopg2
import psycopg2.extras
import httpx

logging.basicConfig(level=logging.WARNING)

conn = psycopg2.connect(
    host="localhost",
    port=15432,
    dbname="stockwise",
    user="stockwise",
    password="stockwise_dev_password",
)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# 0. Check schema
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'news_articles'
    ORDER BY ordinal_position
""")
print("=== news_articles schema ===")
for row in cur.fetchall():
    print(f"  {row['column_name']}: {row['data_type']}")

# 1. Overall count
cur.execute("SELECT COUNT(*) as total FROM news_articles")
print(f"\n=== DB news_articles ===")
print(f"  Total: {cur.fetchone()['total']}")

# 2. Sample articles
cur.execute("""
    SELECT title, symbols, url, crawled_at
    FROM news_articles
    ORDER BY crawled_at DESC
    LIMIT 50
""")
print(f"\n=== Last 30 articles ===")
garbage_keywords = [
    'xo so', 'xổ số', 'thoi tiet', 'thời tiết', 'nong', 'nắng',
    'mua', 'bão', 'trai cay', 'trái cây', 'can nang', 'cân nặng',
    'giam can', 'giảm cân', 'ung thu', 'ung thư', 'me vat', 'mẹ và',
    'tre ngu', 'trẻ ngủ', 'hai tuổi', 'ba tuổi', 'bệnh viện', 'bác sĩ',
    'sức khỏe', 'dinh dưỡng', 'thuốc', 'uống thuốc',
    'robot', 'quốc báo', 'cuba', 'iran', 'my ', 'nước mỹ', 'hàn quốc',
    'thị trường chứng khoán', 'giá vàng', 'xăng',
]
for row in cur.fetchall():
    title_lower = row['title'].lower()
    symbols = list(row['symbols']) if row['symbols'] else []
    is_garbage = any(kw in title_lower for kw in garbage_keywords)
    marker = " [GARBAGE?]" if is_garbage else ""
    src = row['url'].split('/')[2] if row['url'] else '?'
    print(f"  [{','.join(symbols) or 'NONE':12}] [{src}] {row['title'][:60]}{marker}")

# 3. Symbols distribution
cur.execute("SELECT COUNT(*) as cnt FROM news_articles WHERE symbols = '{}'")
print(f"\n=== Articles with empty symbols: {cur.fetchone()['cnt']} ===")

cur.close()
conn.close()

# 4. Check Qdrant
r = httpx.get("http://localhost:16333/collections/news_chunks/points", timeout=10)
if r.status_code == 200:
    data = r.json()
    total = data.get('result', {}).get('total', '?')
    print(f"\n=== Qdrant news_chunks ===")
    print(f"  Total points: {total}")
else:
    print(f"\n=== Qdrant news_chunks: {r.status_code} {r.text}")
