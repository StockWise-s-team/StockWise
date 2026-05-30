from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.stream_b.crawlers.reuters_vn_crawler import ReutersVNCrawler


class TestReutersVNCrawler:
    @pytest.fixture
    def crawler(self):
        return ReutersVNCrawler()

    @pytest.mark.asyncio
    async def test_source_name(self, crawler):
        assert crawler.source_name == "reuters_vn"

    def test_is_vn_related(self, crawler):
        assert crawler._is_vn_related(
            "Vietnam GDP grows 6%", "Manufacturing output rises"
        ) is True
        assert crawler._is_vn_related(
            "Apple reports earnings", "Tech giant beats estimates"
        ) is False
        assert crawler._is_vn_related(
            "Hanoi factory output up", "Industrial production increases"
        ) is True
        assert crawler._is_vn_related(
            "Ho Chi Minh City exports surge", "Trade data released"
        ) is True

    def test_extract_symbols(self, crawler):
        text = "AAPL.N MSFT.O and VNM:VN reported results."
        symbols = crawler._extract_symbols(text)
        assert "VNM" in symbols
        assert "AAPL" in symbols
        assert "MSFT" in symbols

    def test_extract_symbols_filters_common_words(self, crawler):
        text = "THE AND NEWS WORLD ASIA REUTERS are not symbols."
        symbols = crawler._extract_symbols(text)
        assert "THE" not in symbols
        assert "NEWS" not in symbols

    def test_extract_symbols_empty(self, crawler):
        assert crawler._extract_symbols("No symbols here.") == []

    @pytest.mark.asyncio
    async def test_parse_listing_filters_non_vn(self, crawler):
        html = """
        <html><body>
            <article>
                <a href="/world/apple-earnings">
                    <h2>Apple Reports Q2 Earnings</h2>
                    <p>Tech giant beats estimates.</p>
                </a>
            </article>
            <article>
                <a href="/world/vietnam-manufacturing">
                    <h2>Vietnam Manufacturing Rises</h2>
                    <p>PMI data shows expansion.</p>
                </a>
            </article>
        </body></html>
        """
        results = crawler._parse_listing(html)
        assert len(results) == 1
        assert "Vietnam" in results[0]["title"]

    @pytest.mark.asyncio
    async def test_parse_article(self, crawler):
        html = """
        <html><body>
            <h1>Vietnam GDP Growth Accelerates</h1>
            <article data-testid="Body">
                <p>Vietnam's economy grew 6.5% in Q1 2026.</p>
            </article>
            <time datetime="2026-05-30T08:00:00Z"></time>
        </body></html>
        """
        result = crawler._parse_article(html, "https://reuters.com/test")
        assert result is not None
        assert result["title"] == "Vietnam GDP Growth Accelerates"
        assert result["url"] == "https://reuters.com/test"

    @pytest.mark.asyncio
    async def test_crawl_returns_empty_on_error(self, crawler):
        with patch.object(
            crawler, "_fetch_listing", side_effect=Exception("Network error")
        ):
            result = await crawler.crawl()
        assert result == []
