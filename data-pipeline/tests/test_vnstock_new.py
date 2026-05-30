import sys
sys.stdout.reconfigure(encoding='utf-8')
import vnstock

q = vnstock.Quote(symbol='VNM')
print("Source:", q.source)
df = q.history(start='2026-05-01', end='2026-05-30')
print("Columns:", df.columns.tolist())
print(df.head(2).to_string())
