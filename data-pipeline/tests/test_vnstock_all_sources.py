import sys
sys.stdout.reconfigure(encoding='utf-8')

from vnstock3 import Quote

for src in ['VCI', 'TCBS', 'SSI', 'HMSOURCE']:
    print(f"\n=== Source: {src} ===")
    try:
        q = Quote(symbol='VNM', source=src)
        df = q.history(start='2026-05-20', end='2026-05-30', interval='1D')
        print("Columns:", df.columns.tolist())
        print(df.head(1).to_string())
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
