"""
Test stream_c fetcher: chạy PriceBoardFetcher thực tế để xem dữ liệu shape.

Chạy:
    cd data-pipeline
    python tests/test_stream_c_fetcher.py
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = ["VHM", "VCB", "TCB", "VIC", "HPG"]


async def main():
    from app.stream_c.fetcher import PriceBoardFetcher

    fetcher = PriceBoardFetcher()
    print(f"[StreamC Test] Fetching price_board for: {SYMBOLS}")
    records = await fetcher.fetch(SYMBOLS)

    print(f"\n[StreamC Test] Got {len(records)} records\n")
    for rec in records:
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        print("-" * 40)

    # Kiểm tra payload sẽ publish lên RabbitMQ
    ok = [r for r in records if "error" not in r]
    payload = {
        "symbols": [r["symbol"] for r in ok],
        "prices": ok,
        "source": "vnstock_price_board",
        "timestamp": "2026-06-14T02:00:00Z",
        "record_count": len(ok),
        "action": "price.updated",
    }
    print("\n[StreamC Test] RabbitMQ payload shape:")
    print(f"  symbols: {payload['symbols']}")
    print(f"  record_count: {payload['record_count']}")
    print(f"  sample price fields: {list(ok[0].keys()) if ok else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(main())
