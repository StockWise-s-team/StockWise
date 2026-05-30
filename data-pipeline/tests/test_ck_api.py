import asyncio
import logging

import pytest

from app.stream_a.fetchers.ck_api_fetcher import CkApiFetcher

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


@pytest.mark.asyncio
async def test_ck_api():
    fetcher = CkApiFetcher()

    print("\n=== Test CKApiFetcher (FMP) ===")

    result = await fetcher.fetch(["AAPL"])
    for r in result:
        print(f"  [{r['symbol']}] ratios={r['ratios']}")

    result2 = await fetcher.fetch(["VNM"])
    for r in result2:
        print(f"  [{r['symbol']}] ratios={r['ratios']}")
