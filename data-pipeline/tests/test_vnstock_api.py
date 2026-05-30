import sys
sys.stdout.reconfigure(encoding='utf-8')

from vnstock3 import Quote

q = Quote(symbol='VNM')
df = q.history(start='2026-05-01', end='2026-05-31', interval='1D')
print(df.columns.tolist())
print(df.head(3).to_string())
