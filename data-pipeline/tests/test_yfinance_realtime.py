"""
Test Yahoo Finance real-time/snapshot capabilities cho cổ phiếu VN.
So sánh với vnstock price_board để xem có thể thay thế không.

Chạy:
    cd data-pipeline
    python -X utf8 tests/test_yfinance_realtime.py
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timezone, timedelta
import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = ["VHM", "VCB", "TCB", "VIC", "HPG"]
# Yahoo dùng suffix .VN cho HOSE
YF_SYMBOLS = [f"{s}.VN" for s in SYMBOLS]

SEP = "=" * 60


def section(title: str):
    print(f"\n{SEP}\n  {title}\n{SEP}")


# ─────────────────────────────────────────────────────────────
# 1. yfinance.Ticker.info — thông tin đầy đủ (chậm, 1 lần/symbol)
# ─────────────────────────────────────────────────────────────
def test_ticker_info():
    section("1. yfinance.Ticker.info (1 symbol)")
    import yfinance as yf

    ticker = yf.Ticker("VHM.VN")
    info = ticker.info or {}
    price_fields = [
        "currentPrice", "regularMarketPrice", "regularMarketOpen",
        "regularMarketDayHigh", "regularMarketDayLow", "regularMarketVolume",
        "previousClose", "open", "dayHigh", "dayLow", "volume",
        "regularMarketPreviousClose", "bid", "ask",
        "regularMarketChangePercent", "regularMarketChange",
        "marketCap", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
        "regularMarketTime", "exchangeTimezoneName",
    ]
    print(f"  Total info fields: {len(info)}")
    print(f"\n  Price-relevant fields:")
    for f in price_fields:
        val = info.get(f)
        if val is not None:
            print(f"    {f:40s} = {val}")
        else:
            print(f"    {f:40s} = [MISSING]")


# ─────────────────────────────────────────────────────────────
# 2. yfinance.Ticker.fast_info — snapshot nhanh hơn
# ─────────────────────────────────────────────────────────────
def test_fast_info():
    section("2. yfinance.Ticker.fast_info")
    import yfinance as yf

    ticker = yf.Ticker("VHM.VN")
    try:
        fi = ticker.fast_info
        print(f"  Type: {type(fi)}")
        attrs = [a for a in dir(fi) if not a.startswith("_")]
        print(f"  Attributes: {attrs}")
        for a in attrs:
            try:
                val = getattr(fi, a)
                print(f"    {a:35s} = {val}")
            except Exception as e:
                print(f"    {a:35s} = ERROR: {e}")
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────
# 3. yfinance.download — 1D history (ngày hôm nay / hôm qua)
# ─────────────────────────────────────────────────────────────
def test_download_1d():
    section("3. yfinance.download - period=5d interval=1d")
    import yfinance as yf

    try:
        df = yf.download(
            tickers=YF_SYMBOLS,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
        )
        print(f"  Shape: {df.shape}")
        print(f"  Columns (top level): {list(df.columns.get_level_values(0).unique()) if hasattr(df.columns, 'get_level_values') else list(df.columns)}")
        print(df.tail(3).to_string())
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────
# 4. yfinance.download — intraday 1m / 5m / 15m
# ─────────────────────────────────────────────────────────────
def test_download_intraday():
    section("4. yfinance.download - period=1d interval=1m (single symbol)")
    import yfinance as yf

    for interval in ["1m", "5m", "15m", "30m"]:
        try:
            df = yf.download(
                tickers="VHM.VN",
                period="1d",
                interval=interval,
                auto_adjust=True,
                progress=False,
            )
            print(f"  [{interval}] shape={df.shape}, columns={list(df.columns)}")
            if not df.empty:
                print(df.tail(3).to_string())
                break
            else:
                print(f"  [{interval}] EMPTY DataFrame")
        except Exception as e:
            print(f"  [{interval}] FAILED: {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────
# 5. Multi-symbol fast_info batch — tốc độ thực tế
# ─────────────────────────────────────────────────────────────
def test_batch_fast_info():
    section("5. Batch fast_info for all symbols (timing)")
    import yfinance as yf
    import time

    t0 = time.time()
    results = {}
    for yf_sym in YF_SYMBOLS:
        try:
            ticker = yf.Ticker(yf_sym)
            fi = ticker.fast_info
            results[yf_sym] = {
                "last_price": getattr(fi, "last_price", None),
                "open": getattr(fi, "open", None),
                "day_high": getattr(fi, "day_high", None),
                "day_low": getattr(fi, "day_low", None),
                "volume": getattr(fi, "three_month_average_volume", None),
                "previous_close": getattr(fi, "previous_close", None),
                "last_volume": getattr(fi, "last_volume", None),
            }
        except Exception as e:
            results[yf_sym] = {"error": str(e)}

    elapsed = time.time() - t0
    print(f"  Time for {len(YF_SYMBOLS)} symbols: {elapsed:.2f}s")
    for sym, data in results.items():
        print(f"  {sym}: {data}")


# ─────────────────────────────────────────────────────────────
# 6. yfinance.Tickers (batch) — download nhiều symbol 1 lần
# ─────────────────────────────────────────────────────────────
def test_tickers_batch():
    section("6. yfinance.Tickers batch - today's OHLCV")
    import yfinance as yf
    import time

    t0 = time.time()
    try:
        tickers = yf.Tickers(" ".join(YF_SYMBOLS))
        df = tickers.download(
            period="2d",
            interval="1d",
            auto_adjust=True,
            progress=False,
        )
        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.2f}s, shape: {df.shape}")
        print(df.to_string())
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")


# ─────────────────────────────────────────────────────────────
# 7. So sánh trực tiếp: yfinance vs vnstock price_board
# ─────────────────────────────────────────────────────────────
def test_compare_with_vnstock():
    section("7. Direct comparison: yfinance vs vnstock price_board (VHM)")
    import yfinance as yf
    import vnstock

    sym = "VHM"

    # vnstock
    print("\n  [vnstock price_board]")
    try:
        vnstock.config.API_KEY = ""
        trading = vnstock.Trading(source="kbs")
        df_vn = trading.price_board(symbols_list=[sym])
        row = df_vn.iloc[0] if not df_vn.empty else {}
        print(f"    close:     {row.get('close_price')}")
        print(f"    open:      {row.get('open_price')}")
        print(f"    high:      {row.get('high_price')}")
        print(f"    low:       {row.get('low_price')}")
        print(f"    volume:    {row.get('volume_accumulated')}")
        print(f"    ref_price: {row.get('reference_price')}")
        print(f"    % change:  {row.get('percent_change')}")
    except Exception as e:
        print(f"    FAILED: {type(e).__name__}: {e}")

    # yfinance fast_info
    print("\n  [yfinance fast_info]")
    try:
        ticker = yf.Ticker(f"{sym}.VN")
        fi = ticker.fast_info
        print(f"    last_price: {getattr(fi, 'last_price', None)}")
        print(f"    open:       {getattr(fi, 'open', None)}")
        print(f"    day_high:   {getattr(fi, 'day_high', None)}")
        print(f"    day_low:    {getattr(fi, 'day_low', None)}")
        print(f"    last_vol:   {getattr(fi, 'last_volume', None)}")
        print(f"    prev_close: {getattr(fi, 'previous_close', None)}")
    except Exception as e:
        print(f"    FAILED: {type(e).__name__}: {e}")

    # yfinance history 1d
    print("\n  [yfinance history 1d - last row]")
    try:
        ticker = yf.Ticker(f"{sym}.VN")
        hist = ticker.history(period="2d", interval="1d")
        if not hist.empty:
            row = hist.iloc[-1]
            print(f"    Close:  {row.get('Close')}")
            print(f"    Open:   {row.get('Open')}")
            print(f"    High:   {row.get('High')}")
            print(f"    Low:    {row.get('Low')}")
            print(f"    Volume: {row.get('Volume')}")
        else:
            print("    EMPTY")
    except Exception as e:
        print(f"    FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print(f"Test time: {datetime.now(timezone.utc).isoformat()}")
    test_ticker_info()
    test_fast_info()
    test_download_1d()
    test_download_intraday()
    test_batch_fast_info()
    test_tickers_batch()
    test_compare_with_vnstock()
    print(f"\n{SEP}\n  DONE\n{SEP}")
