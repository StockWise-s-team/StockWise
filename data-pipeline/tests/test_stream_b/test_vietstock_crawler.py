from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.stream_b.crawlers.vietstock_crawler import VietstockCrawler
from app.stream_b.crawlers.vietstock_sitemap_crawler import (
    VietstockSitemapCrawler,
    _parse_relative_date,
)


class TestVietstockCrawler:
    @pytest.fixture
    def crawler(self):
        return VietstockSitemapCrawler(max_articles=5)

    @pytest.mark.asyncio
    async def test_source_name(self, crawler):
        assert crawler.source_name == "vietstock"

    @pytest.mark.asyncio
    async def test_parse_sitemap(self, crawler):
        xml = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://vietstock.vn/article1.htm</loc></url>
            <url><loc>https://vietstock.vn/article2.htm</loc></url>
        </urlset>"""
        urls = crawler._parse_sitemap(xml)
        assert urls == [
            "https://vietstock.vn/article1.htm",
            "https://vietstock.vn/article2.htm",
        ]

    @pytest.mark.asyncio
    async def test_parse_article(self, crawler):
        html = """
        <html><body>
            <h1 class="title-detail">VPB Capital Raise Plan</h1>
            <p class="sapo">VPB announced a major bond issuance.</p>
            <div class="detail-content">
                <p>VPB plans to raise 5 trillion VND through bond issuance in Q2.</p>
            </div>
            <span class="date-time">2 giờ trước</span>
            <div class="tag-list">
                <a href="#">VPB</a>
                <a href="#">ACB</a>
            </div>
        </body></html>
        """
        result = crawler._parse_article(
            html, "https://vietstock.vn/vpb-bond-2026.htm"
        )
        assert result is not None
        assert result["title"] == "VPB Capital Raise Plan"
        assert result["url"] == "https://vietstock.vn/vpb-bond-2026.htm"
        assert result["source_name"] == "vietstock"

    @pytest.mark.asyncio
    async def test_parse_article_returns_none_for_empty(self, crawler):
        assert crawler._parse_article("", "https://vietstock.vn/test.htm") is None

    @pytest.mark.asyncio
    async def test_crawl_skips_fetch_on_sitemap_error(self, crawler):
        with patch.object(
            crawler, "_fetch_article_urls", side_effect=Exception("Network error")
        ):
            result = await crawler.crawl()
        assert result == []

    @pytest.mark.asyncio
    async def test_crawl_respects_max_articles(self):
        crawler = VietstockSitemapCrawler(max_articles=2)

        async def fake_urls():
            return [f"https://vietstock.vn/a{i}.htm" for i in range(5)]

        async def fake_article(url):
            return {
                "title": f"Article {url}",
                "content": "<p>Content</p>",
                "excerpt": "",
                "url": url,
                "published_at": None,
                "symbols": [],
                "source_name": "vietstock",
            }

        with patch.object(crawler, "_fetch_article_urls", side_effect=fake_urls):
            with patch.object(crawler, "_fetch_article", side_effect=fake_article):
                result = await crawler.crawl()

        assert len(result) == 2


class TestParseRelativeDate:
    def test_parses_hours(self):
        result = _parse_relative_date("1 giờ trước")
        assert result is not None

    def test_parses_minutes(self):
        result = _parse_relative_date("30 phút trước")
        assert result is not None

    def test_parses_days(self):
        result = _parse_relative_date("2 ngày trước")
        assert result is not None

    def test_parses_weeks(self):
        result = _parse_relative_date("1 tuần trước")
        assert result is not None

    def test_returns_none_for_invalid(self):
        assert _parse_relative_date("Không rõ ngày") is None
        assert _parse_relative_date("") is None
