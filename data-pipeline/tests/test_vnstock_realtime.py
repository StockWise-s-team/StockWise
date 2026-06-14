"""
Test script: khám phá khả năng real-time/intraday của vnstock
Chạy: python -m tests.test_vnstock_realtime  (từ thư mục data-pipeline)
      hoặc: python tests/test_vnstock_realtime.py
"""
import os
import sys
import json
import pprint

# Thêm thư mục data-pipeline vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import vnstock
    print(f"[OK] vnstock imported, version: {getattr(vnstock, '__version__', 'unknown')}")
except ImportError as e:
    print(f"[ERR] Cannot import vnstock: {e}")
    sys.exit(1)

SYMBOL = "VHM"


def test_quote_intraday():
    """Thử lấy giá intraday (1m / 5m / 15m) — dành cho stream_c."""
    print("\n=== test_quote_intraday ===")
    for interval in ["1", "5", "15", "30"]:
        try:
            q = vnstock.Quote(source="kbs", symbol=SYMBOL)
            # intraday thường dùng interval 1,5,15,30 phút
            df = q.intraday(symbol=SYMBOL, page_size=100)
            print(f"[interval={interval}] OK — shape={df.shape}, columns={list(df.columns)}")
            print(df.head(3).to_string())
            break
        except Exception as e:
            print(f"[interval={interval}] FAILED: {type(e).__name__}: {e}")


def test_quote_latest_price():
    """Thử lấy giá khớp lệnh mới nhất (real-time snapshot)."""
    print("\n=== test_quote_latest_price ===")
    try:
        q = vnstock.Quote(source="kbs", symbol=SYMBOL)
        # Thử method price_board hoặc tương tự
        methods = ["price_board", "intraday", "quote_history"]
        for m in methods:
            if hasattr(q, m):
                print(f"  [found] Quote.{m}")
    except Exception as e:
        print(f"[FAILED] {e}")

    # Thử Stock.quote
    try:
        from vnstock import Stock
        stock = Stock(symbol=SYMBOL, source="kbs")
        print(f"  Stock attrs: {[a for a in dir(stock) if not a.startswith('_')]}")
        if hasattr(stock, "quote"):
            q = stock.quote
            print(f"  stock.quote attrs: {[a for a in dir(q) if not a.startswith('_')]}")
    except Exception as e:
        print(f"[Stock] FAILED: {type(e).__name__}: {e}")


def test_price_board():
    """Thử price_board — bảng giá snapshot nhiều mã cùng lúc."""
    print("\n=== test_price_board ===")
    try:
        from vnstock import Trading
        trading = Trading(source="kbs")
        df = trading.price_board(symbols_list=[SYMBOL, "VCB", "TCB"])
        print(f"  price_board OK — shape={df.shape}")
        print(f"  columns: {list(df.columns)}")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"[Trading.price_board] FAILED: {type(e).__name__}: {e}")

    # Thử Listing
    try:
        from vnstock import Listing
        lst = Listing()
        methods = [a for a in dir(lst) if not a.startswith("_")]
        print(f"  Listing attrs: {methods}")
    except Exception as e:
        print(f"[Listing] FAILED: {type(e).__name__}: {e}")


def test_history_1d():
    """Xác nhận history 1D vẫn hoạt động như stream_a — baseline check."""
    print("\n=== test_history_1d ===")
    from datetime import datetime, timedelta
    try:
        q = vnstock.Quote(source="kbs", symbol=SYMBOL)
        end = datetime.now()
        start = end - timedelta(days=3)
        df = q.history(
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            interval="1D",
        )
        print(f"  history 1D OK — shape={df.shape}, columns={list(df.columns)}")
        print(df.tail(3).to_string())
    except Exception as e:
        print(f"[history_1D] FAILED: {type(e).__name__}: {e}")


def test_vnstock_all_methods():
    """In tất cả methods của vnstock.Quote để tìm real-time option."""
    print("\n=== all Quote methods ===")
    try:
        q = vnstock.Quote(source="kbs", symbol=SYMBOL)
        methods = [a for a in dir(q) if not a.startswith("_")]
        print(f"  Quote attrs: {methods}")
    except Exception as e:
        print(f"[Quote] FAILED: {type(e).__name__}: {e}")

    print("\n=== top-level vnstock attrs ===")
    attrs = [a for a in dir(vnstock) if not a.startswith("_")]
    print(f"  {attrs}")


if __name__ == "__main__":
    print("=" * 60)
    print(f"Testing vnstock real-time capabilities for: {SYMBOL}")
    print("=" * 60)
    test_vnstock_all_methods()
    test_history_1d()
    test_quote_intraday()
    test_quote_latest_price()
    test_price_board()
    print("\n=== DONE ===")
