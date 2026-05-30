import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")

from app.stream_a.fetchers.ck_api_fetcher import CkApiFetcher


async def test_ck_api():
    fetcher = CkApiFetcher()

    # Test AAPL (US stock - should work with FMP)
    print("\n=== Test CKApiFetcher (FMP) ===")

    result = await fetcher.fetch(["AAPL"])
    for r in result:
        print(f"  [{r['symbol']}] ratios={r['ratios']}")

    # Test VNM (Vietnamese stock - may not be supported)
    result2 = await fetcher.fetch(["VNM"])
    for r in result2:
        print(f"  [{r['symbol']}] ratios={r['ratios']}")


if __name__ == "__main__":
    asyncio.run(test_ck_api())
