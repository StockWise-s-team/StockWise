import httpx
import pytest

from app.services.data_providers import HTTPMarketDataProvider, HTTPPortfolioProvider


@pytest.mark.asyncio
async def test_http_market_provider_maps_java_contract():
    def handler(request):
        if "/price/" in request.url.path:
            return httpx.Response(200, json={"symbol": "FPT", "tradeDate": "2026-05-30", "close": 133500, "volume": 10})
        return httpx.Response(200, json=[])

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = HTTPMarketDataProvider("http://market", client)
    assert (await provider.get_latest_price("fpt"))["trade_date"] == "2026-05-30"
    await client.aclose()


@pytest.mark.asyncio
async def test_http_portfolio_provider_reports_contract_limitation():
    def handler(request):
        if request.url.path.endswith("/pnl"):
            return httpx.Response(200, json={"totalPnl": 100})
        return httpx.Response(200, json={"portfolio": {"virtualCash": 10}, "holdings": []})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = HTTPPortfolioProvider("http://portfolio", client)
    result = await provider.get_portfolio("user-1")
    assert result["total_value"] is None
    assert result["unrealized_pnl"] == 100
    await client.aclose()
