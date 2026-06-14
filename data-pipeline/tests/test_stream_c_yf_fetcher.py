"""
Test YahooFinancePriceFetcher thực tế + fallback logic của runner.

Chạy:
    cd data-pipeline
    python -X utf8 tests/test_stream_c_yf_fetcher.py
"""
import asyncio
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SYMBOLS = ["VHM", "VCB", "TCB", "VIC", "HPG", "VPB", "TCB"]

SEP = "=" * 60


async def test_yf_fetcher():
    """Test YahooFinancePriceFetcher trực tiếp."""
    print(f"\n{SEP}")
    print("[Test A] YahooFinancePriceFetcher.fetch()")
    print(SEP)

    from app.stream_c.yf_fetcher import YahooFinancePriceFetcher
    fetcher = YahooFinancePriceFetcher()
    records = await fetcher.fetch(SYMBOLS[:5])

    print(f"Got {len(records)} records:")
    ok = [r for r in records if "error" not in r]
    err = [r for r in records if "error" in r]
    print(f"  OK: {len(ok)}, Errors: {len(err)}")

    for r in ok:
        print(f"\n  {r['symbol']}:")
        for k, v in r.items():
            if k != "symbol":
                print(f"    {k:20s} = {v}")

    return ok


async def test_fallback_logic_mocked():
    """Giả lập vnstock rate limit, kiểm tra fallback sang yfinance."""
    print(f"\n{SEP}")
    print("[Test B] Fallback logic — giả lập vnstock rate limit")
    print(SEP)

    from app.stream_c import runner
    from app.stream_c.yf_fetcher import YahooFinancePriceFetcher

    # Mock primary fetcher trả về 100% lỗi rate limit
    class MockRateLimitFetcher:
        async def fetch(self, symbols):
            print(f"  [MockPrimary] Simulating rate limit for {len(symbols)} symbols")
            return [{"symbol": s, "error": "rate limit exceeded"} for s in symbols]

    # Mock producer
    published_data = []
    class MockProducer:
        async def publish(self, exchange_name, routing_key, data):
            published_data.append(data)
            print(f"  [MockProducer] Published via source={data['source']}")
            print(f"    symbols: {data['symbols']}")
            print(f"    record_count: {data['record_count']}")

    # Mock price repo
    class MockPriceRepo:
        def get_tracked_symbols(self):
            return SYMBOLS[:5]

    # Mock run repo
    class MockRunRepo:
        def create_run(self, **kwargs): return "mock-run"
        def add_symbol_result(self, *args, **kwargs): pass
        def finish_run(self, run_id, status, errors):
            print(f"  [MockRunRepo] finish_run: status={status}, errors={errors[:2] if errors else []}")

    # Patch PipelineRunsRepository
    original_repo = runner.PipelineRunsRepository
    runner.PipelineRunsRepository = lambda: MockRunRepo()

    try:
        await runner._run_once(
            price_repo=MockPriceRepo(),
            primary_fetcher=MockRateLimitFetcher(),
            fallback_fetcher=YahooFinancePriceFetcher(),
            producer=MockProducer(),
        )
    finally:
        runner.PipelineRunsRepository = original_repo

    if published_data:
        assert published_data[0]["source"] == "yahoo_finance_price", \
            f"Expected yahoo_finance_price, got {published_data[0]['source']}"
        print(f"\n  [PASS] Fallback to yfinance worked correctly!")
    else:
        print("\n  [WARN] Nothing published (both sources failed or no market hours?)")


async def test_compare_close_prices():
    """So sánh giá close giữa yfinance và vnstock."""
    print(f"\n{SEP}")
    print("[Test C] Close price comparison: yfinance vs vnstock")
    print(SEP)

    from app.stream_c.yf_fetcher import YahooFinancePriceFetcher
    from app.stream_c.fetcher import PriceBoardFetcher

    symbols = ["VHM", "VCB", "HPG"]

    yf_records = await YahooFinancePriceFetcher().fetch(symbols)
    vn_records = await PriceBoardFetcher().fetch(symbols)

    yf_map = {r["symbol"]: r for r in yf_records if "error" not in r}
    vn_map = {r["symbol"]: r for r in vn_records if "error" not in r}

    print(f"\n  {'Symbol':6s} {'yf_close':>12s} {'vn_close':>12s} {'diff':>8s} {'pct_yf':>10s} {'pct_vn':>10s}")
    print(f"  {'-'*62}")
    for sym in symbols:
        yf = yf_map.get(sym, {})
        vn = vn_map.get(sym, {})
        yf_c = yf.get("close", 0) or 0
        vn_c = vn.get("close", 0) or 0
        diff = yf_c - vn_c
        yf_pct = yf.get("percent_change")
        vn_pct = vn.get("percent_change")
        print(f"  {sym:6s} {yf_c:>12,.0f} {vn_c:>12,.0f} {diff:>+8,.0f} {str(round(yf_pct,2) if yf_pct else 'N/A'):>10s} {str(round(vn_pct,2) if vn_pct else 'N/A'):>10s}")


async def main():
    await test_yf_fetcher()
    await test_fallback_logic_mocked()
    await test_compare_close_prices()
    print(f"\n{SEP}\nALL TESTS DONE\n{SEP}")


if __name__ == "__main__":
    asyncio.run(main())
