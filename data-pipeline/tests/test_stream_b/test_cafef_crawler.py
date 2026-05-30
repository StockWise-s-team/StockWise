from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.stream_b.crawlers.cafef_crawler import CafeFCrawler


class TestCafeFCrawler:
    @pytest.fixture
    def crawler(self):
        return CafeFCrawler(max_articles=5)

    @pytest.mark.asyncio
    async def test_source_name(self, crawler):
        assert crawler.source_name == "cafef"

    @pytest.mark.asyncio
    async def test_parse_sitemap(self, crawler):
        xml = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://cafef.vn/article1.chn</loc></url>
            <url><loc>https://cafef.vn/article2.chn</loc></url>
        </urlset>"""
        urls = crawler._parse_sitemap(xml)
        assert urls == [
            "https://cafef.vn/article1.chn",
            "https://cafef.vn/article2.chn",
        ]

    @pytest.mark.asyncio
    async def test_parse_sitemap_empty(self, crawler):
        assert crawler._parse_sitemap("") == []
        assert crawler._parse_sitemap("<urlset/>") == []

    @pytest.mark.asyncio
    async def test_parse_article_extracts_fields(self, crawler, sample_html_article):
        result = crawler._parse_article(
            sample_html_article, "https://cafef.vn/test.chn"
        )
        assert result is not None
        assert result["title"] == "VNM Reports Record Profit, VPB and HPG Surge"
        assert result["url"] == "https://cafef.vn/test.chn"
        assert "VNM" in result["symbols"]
        assert result["source_name"] == "cafef"
        assert "<script>" not in result["content"]

    @pytest.mark.asyncio
    async def test_parse_article_returns_none_for_empty(self, crawler):
        assert crawler._parse_article("", "https://cafef.vn/test.chn") is None
        assert crawler._parse_article("<html><body></body></html>", "https://cafef.vn/test.chn") is None

    @pytest.mark.asyncio
    async def test_crawl_skips_fetch_on_sitemap_error(self, crawler):
        with patch.object(
            crawler, "_fetch_article_urls", side_effect=Exception("Network error")
        ):
            result = await crawler.crawl()
        assert result == []

    @pytest.mark.asyncio
    async def test_crawl_respects_max_articles(self):
        crawler = CafeFCrawler(max_articles=2)

        async def fake_urls():
            return [f"https://cafef.vn/a{i}.chn" for i in range(5)]

        async def fake_article(url):
            return {
                "title": f"Article {url}",
                "content": "<p>Content</p>",
                "excerpt": "",
                "url": url,
                "published_at": None,
                "symbols": [],
                "source_name": "cafef",
            }

        with patch.object(crawler, "_fetch_article_urls", side_effect=fake_urls):
            with patch.object(crawler, "_fetch_article", side_effect=fake_article):
                result = await crawler.crawl()

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_crawl_continues_on_article_error(self, crawler):
        async def fake_urls():
            return [
                "https://cafef.vn/a1.chn",
                "https://cafef.vn/a2.chn",
            ]

        async def fake_article(url):
            if "a1" in url:
                raise Exception("Parse error")
            return {
                "title": "Success",
                "content": "<p>Content</p>",
                "excerpt": "",
                "url": url,
                "published_at": None,
                "symbols": [],
                "source_name": "cafef",
            }

        with patch.object(crawler, "_fetch_article_urls", side_effect=fake_urls):
            with patch.object(crawler, "_fetch_article", side_effect=fake_article):
                result = await crawler.crawl()

        assert len(result) == 1
        assert result[0]["title"] == "Success"
