import psycopg2
import psycopg2.extras

conn = psycopg2.connect(
    host="localhost", port=15432, dbname="stockwise",
    user="stockwise", password="stockwise_dev_password"
)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Fetch all articles ordered by crawled_at desc
cur.execute("""
    SELECT
        na.id,
        na.title,
        na.url,
        na.published_at,
        na.symbols,
        ns.name AS source_name,
        na.crawled_at
    FROM news_articles na
    JOIN news_sources ns ON ns.id = na.source_id
    ORDER BY na.crawled_at DESC
    LIMIT 50
""")
rows = cur.fetchall()
total = len(rows)
print(f"Total articles in DB: {total}")
print()

# Count per source
cur.execute("""
    SELECT ns.name, COUNT(na.id)
    FROM news_articles na
    JOIN news_sources ns ON ns.id = na.source_id
    GROUP BY ns.name
""")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} articles")

print()
for r in rows:
    src = r["source_name"]
    title = (r["title"] or "")[:90]
    syms = list(r["symbols"] or [])
    pub = str(r["published_at"])[:10] if r["published_at"] else "N/A"
    url = r["url"]
    print(f"[{src}] {title}")
    print(f"  Symbols: {syms} | Published: {pub}")
    print(f"  URL: {url}")
    print()

cur.close()
conn.close()
