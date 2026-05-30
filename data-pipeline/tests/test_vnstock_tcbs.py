import sys
sys.stdout.reconfigure(encoding='utf-8')

from vnstock3 import Quote

# Try TCBS source
q = Quote(symbol='VNM', source='TCBS')
try:
    df = q.history(start='2026-05-01', end='2026-05-31', interval='1D')
    print("TCBS columns:", df.columns.tolist())
    print(df.head(2).to_string())
except Exception as e:
    print("TCBS error:", e)
