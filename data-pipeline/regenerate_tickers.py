"""Regenerate valid_tickers.json from vnstock symbols_by_exchange (STOCK only)."""
import json
import re
from pathlib import Path

from vnstock import Listing

KNOWN_GARBAGE = {
    # Vietnamese market categories/indices
    "SMA", "NHA", "TOP", "TRA", "LAI", "CAR", "APP",
    # Common English words that appear as symbols
    "BIG", "NDT", "HRC", "ECO", "COM", "WCS", "DTC", "CEO",
    "NTL", "ONE", "ALL", "NEW", "PRO", "MAX", "MIN", "SUP",
    "NET", "OLD", "PUT", "GET", "SET", "OUT", "SUM", "FIL",
    # Misc abbreviations that aren't real stock tickers
    "CFM", "BCF", "NAV", "FIF", "DPR", "BWE", "ESOP",
    "BTT", "BKS", "PDF", "HTM", "TIN", "NIM", "VIN", "HOA",
    "BAY", "MRO", "FILI", "PDF",
}


def main():
    print("Fetching symbols_by_exchange...")
    lst = Listing(source="vci")
    df = lst.symbols_by_exchange()

    print(f"  Total rows: {len(df)}")
    print(f"  Columns: {df.columns.tolist()}")
    print(f"  Types: {df['type'].unique().tolist()}")
    print(f"  Exchanges: {df['exchange'].unique().tolist()}")

    # Filter: type=STOCK only, symbol matches [A-Z]{3,4}
    stock_df = df[df["type"].str.upper() == "STOCK"]
    print(f"  STOCK rows: {len(stock_df)}")

    syms: list[str] = []
    for s in stock_df["symbol"].unique():
        s = str(s).strip().upper()
        if re.fullmatch(r"[A-Z]{3,4}", s):
            syms.append(s)

    print(f"  Symbols matching [A-Z]{{3,4}}: {len(syms)}")

    # Remove known garbage
    before = len(syms)
    syms = [s for s in syms if s not in KNOWN_GARBAGE]
    removed = before - len(syms)
    print(f"  After garbage filter (-{removed}): {len(syms)}")

    syms = sorted(set(syms))
    out_path = Path(__file__).parent / "valid_tickers.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(syms, f, ensure_ascii=False, indent=2)
    print(f"\nWritten {len(syms)} clean tickers to {out_path}")

    # Quick sanity checks
    test_cases = ["ACB", "VNM", "FPT", "SMA", "NHA", "TOP", "APP", "BIG", "ETF"]
    print("\nSanity check:")
    sym_set = set(syms)
    for t in test_cases:
        print(f"  {t}: {'VALID' if t in sym_set else 'INVALID/filtered'}")


if __name__ == "__main__":
    main()
