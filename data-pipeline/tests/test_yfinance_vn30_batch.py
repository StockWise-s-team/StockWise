"""
Test tốc độ yfinance.download batch cho toàn bộ VN30 (33 symbols).
So sánh với vnstock price_board về tốc độ + dữ liệu đầy đủ.

Chạy:
    cd data-pipeline
    python -X utf8 tests/test_yfinance_vn30_batch.py
"""
import asyncio
import sys, os, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lấy VN30 symbols từ config
from app.config import settings
VN30 = settings.get_vn30_symbols()
YF_SYMS = [f"{s}.VN" for s in VN30]

print(f"VN30 count: {len(VN30)}")
print(f"Symbols: {VN30}\n")

SEP = "-" * 60


def test_yfinance_download_batch():
    """yfinance.download — tải 1D OHLCV batch toàn bộ VN30."""
    import yfinance as yf
    print("=== [A] yfinance.download batch (period=2d, interval=1d) ===")
    t0 = time.time()
    df = yf.download(
        tickers=" ".join(YF_SYMS),
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
    )
    elapsed = time.time() - t0
    print(f"  Time: {elapsed:.2f}s | Shape: {df.shape}")

    # Lấy hàng cuối (hôm nay hoặc ngày giao dịch gần nhất)
    records = []
    for sym, yf_sym in zip(VN30, YF_SYMS):
        try:
            sub = df[yf_sym].dropna()
            if sub.empty:
                records.append({"symbol": sym, "error": "no data"})
                continue
            row = sub.iloc[-1]
            records.append({
                "symbol": sym,
                "close":  float(row["Close"]),
                "open":   float(row["Open"]),
                "high":   float(row["High"]),
                "low":    float(row["Low"]),
                "volume": int(row["Volume"]),
            })
        except Exception as e:
            records.append({"symbol": sym, "error": str(e)})

    ok = [r for r in records if "error" not in r]
    err = [r for r in records if "error" in r]
    print(f"  OK: {len(ok)}/{len(VN30)} | Errors: {len(err)}")
    if err:
        print(f"  Failed: {[r['symbol'] for r in err]}")
    print(f"\n  Sample (first 5):")
    for r in ok[:5]:
        print(f"    {r}")
    return elapsed, ok


def test_yfinance_fast_info_batch():
    """fast_info per-symbol — cũ hơn nhưng có percent_change."""
    import yfinance as yf
    print("\n=== [B] yfinance fast_info per-symbol (toàn VN30) ===")
    t0 = time.time()
    records = []
    for sym, yf_sym in zip(VN30, YF_SYMS):
        try:
            fi = yf.Ticker(yf_sym).fast_info
            prev_close = getattr(fi, "previous_close", None) or getattr(fi, "regular_market_previous_close", None)
            last = getattr(fi, "last_price", None)
            pct = ((last - prev_close) / prev_close * 100) if last and prev_close else None
            records.append({
                "symbol":        sym,
                "close":         last,
                "open":          getattr(fi, "open", None),
                "high":          getattr(fi, "day_high", None),
                "low":           getattr(fi, "day_low", None),
                "volume":        getattr(fi, "last_volume", None),
                "prev_close":    prev_close,
                "percent_change": round(pct, 4) if pct else None,
            })
        except Exception as e:
            records.append({"symbol": sym, "error": str(e)})

    elapsed = time.time() - t0
    ok = [r for r in records if "error" not in r]
    err = [r for r in records if "error" in r]
    print(f"  Time: {elapsed:.2f}s | OK: {len(ok)}/{len(VN30)}")
    if err:
        print(f"  Failed: {[r['symbol'] for r in err]}")
    print(f"  Sample (first 5):")
    for r in ok[:5]:
        print(f"    {r}")
    return elapsed, ok


def test_vnstock_price_board():
    """vnstock price_board — benchmark hiện tại."""
    import vnstock
    print("\n=== [C] vnstock Trading.price_board (toàn VN30) ===")
    t0 = time.time()
    try:
        vnstock.config.API_KEY = ""
        trading = vnstock.Trading(source="kbs")
        # Chia batch 40 như stream_c
        all_records = []
        BATCH = 40
        for i in range(0, len(VN30), BATCH):
            batch = VN30[i:i+BATCH]
            df = trading.price_board(symbols_list=batch)
            for _, row in df.iterrows():
                all_records.append({
                    "symbol":  str(row.get("symbol", "")).upper(),
                    "close":   float(row.get("close_price", 0) or 0),
                    "open":    float(row.get("open_price", 0) or 0),
                    "high":    float(row.get("high_price", 0) or 0),
                    "low":     float(row.get("low_price", 0) or 0),
                    "volume":  int(row.get("volume_accumulated", 0) or 0),
                    "ref":     float(row.get("reference_price", 0) or 0),
                    "pct":     float(row.get("percent_change", 0) or 0),
                })
        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.2f}s | OK: {len(all_records)}/{len(VN30)}")
        for r in all_records[:5]:
            print(f"    {r}")
        return elapsed, all_records
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  FAILED after {elapsed:.2f}s: {type(e).__name__}: {e}")
        return elapsed, []


def compare(yf_records, vn_records):
    """So sánh giá trị giữa hai nguồn."""
    print(f"\n{SEP}")
    print("=== [D] Comparison yfinance vs vnstock (Close price) ===")
    vn_map = {r["symbol"]: r for r in vn_records}
    for r in yf_records[:8]:
        sym = r["symbol"]
        vn = vn_map.get(sym, {})
        yf_c = r.get("close")
        vn_c = vn.get("close")
        match = "OK" if yf_c and vn_c and abs(yf_c - vn_c) < 500 else "DIFF"
        print(f"  {sym:5s}  yf={yf_c}  vn={vn_c}  [{match}]")

    print(f"\n=== [E] Fields available in yfinance.download ===")
    print("  close, open, high, low, volume  (OHLCV)")
    print("  percent_change: derived = (close - prev_close) / prev_close * 100")
    print("  ceiling_price: NOT available (VN-specific, giá trần)")
    print("  floor_price:   NOT available (VN-specific, giá sàn)")
    print("  reference_price (TC): available via previous_close")
    print("  bid/ask: NOT available via download (only in ticker.info)")


if __name__ == "__main__":
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}\n")
    t_yf_dl, ok_dl = test_yfinance_download_batch()
    t_yf_fi, ok_fi = test_yfinance_fast_info_batch()
    t_vn, ok_vn = test_vnstock_price_board()
    compare(ok_dl, ok_vn)

    print(f"\n{SEP}")
    print("=== SUMMARY ===")
    print(f"  yfinance download batch : {t_yf_dl:.2f}s  (recommended)")
    print(f"  yfinance fast_info loop : {t_yf_fi:.2f}s")
    print(f"  vnstock price_board     : {t_vn:.2f}s")
