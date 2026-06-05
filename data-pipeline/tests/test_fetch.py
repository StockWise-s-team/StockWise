import asyncio
import logging

import pytest

from app.stream_a.fetchers.vnstock_fetcher import VnStockFetcher
from app.stream_a.fetchers.yahoo_finance_fetcher import YahooFinanceFetcher
from app.stream_a.transformers.ratio_transformer import RatioTransformer

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


@pytest.mark.asyncio
async def test_vnstock_fetcher():
    print("\n=== Test VnStockFetcher ===")
    fetcher = VnStockFetcher(days_back=7)
    result = await fetcher.fetch(["VNM", "HPG"])

    for r in result:
        symbol = r.get("symbol")
        prices = r.get("prices", [])
        error = r.get("error")

        if error:
            print(f"  [{symbol}] ERROR: {error}")
        else:
            print(f"  [{symbol}] OK - {len(prices)} bars")
            if prices:
                first = prices[0]
                last = prices[-1]
                print(f"    First: {first.get('date')} O={first.get('open')} H={first.get('high')} L={first.get('low')} C={first.get('close')} V={first.get('volume')}")
                print(f"    Last:  {last.get('date')} O={last.get('open')} H={last.get('high')} L={last.get('low')} C={last.get('close')} V={last.get('volume')}")


@pytest.mark.asyncio
async def test_yahoo_finance_fetcher():
    print("\n=== Test YahooFinanceFetcher ===")
    fetcher = YahooFinanceFetcher()
    result = await fetcher.fetch(["VNM", "HPG"])
    for r in result:
        print(f"  [{r.get('symbol')}] ratios={r.get('ratios')}")


def test_ratio_transformer():
    print("\n=== Test RatioTransformer ===")
    transformer = RatioTransformer()

    test_data = {
        "symbol": "VNM",
        "ratios": {
            "pe_ratio": 15.5,
            "pb_ratio": 2.3,
            "eps": 4500.0,
            "roe": 0.18,
            "roa": 0.12,
            "period": "quarterly",
        }
    }

    result = transformer.transform(test_data)
    if result:
        r = result[0]
        print(f"  [{r.symbol}] period={r.period}")
        print(f"    PE={r.pe_ratio}, PB={r.pb_ratio}, EPS={r.eps}")
        print(f"    ROE={r.roe}, ROA={r.roa}")
    else:
        print("  Transformer returned empty (skipped invalid)")

    invalid_data = {
        "symbol": "INVALID",
        "ratios": {
            "pe_ratio": -5,
            "pb_ratio": 2.3,
        }
    }
    result2 = transformer.transform(invalid_data)
    print(f"  Invalid data result: {result2}")
