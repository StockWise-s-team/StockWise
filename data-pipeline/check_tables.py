import psycopg2
conn = psycopg2.connect(
    host="localhost", port=15432, dbname="stockwise",
    user="stockwise", password="stockwise_dev_password"
)
cur = conn.cursor()

# Create tracked_symbols table
cur.execute("""
    CREATE TABLE IF NOT EXISTS tracked_symbols (
        symbol VARCHAR(10) PRIMARY KEY,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
conn.commit()
print("tracked_symbols table created")

# Check company_wiki data to understand financials_snapshot structure
cur.execute("SELECT symbol, wiki_data FROM company_wiki LIMIT 3")
rows = cur.fetchall()
for r in rows:
    print(f"\n{r[0]}: {r[1]}")

cur.close()
conn.close()
