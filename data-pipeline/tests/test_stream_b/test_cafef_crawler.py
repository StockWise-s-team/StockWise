import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.stream_b.crawlers.cafef_crawler import CafeFCrawler


def _make_mock_client(json_data):
    """Build a properly-async httpx.AsyncClient mock for a given JSON response."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value=json_data)

    mock_get = AsyncMock(return_value=mock_resp)

    mock_client = AsyncMock()
    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


class TestCafeFCrawler:
    @pytest.fixture
    def crawler(self):
        return CafeFCrawler(max_articles=5)

    @pytest.fixture
    def mock_api_response(self):
        return {
            "isSuccess": True,
            "value": {
                "items": [
                    {
                        "id": "test-id-1",
                        "symbol": "ACB",
                        "dateDeploy": "2026-06-02T08:41:55.932Z",
                        "title": "ACB - Tiềm năng định giá lại",
                        "body": "ACB giao dịch ở mức P/B 1.2x.",
                        "fileName": "ACB_test.pdf",
                        "imageThumb": "thumb_acb.png",
                        "resourceCode": "VPBANKS",
                        "resourceName": "VPB Securities",
                        "isHot": 1,
                        "categoryIDs": "341,",
                        "sourceID": 152,
                        "catID": 3,
                        "reportType": "Cập nhật doanh nghiệp – Khuyến nghị",
                        "reportID": 1,
                        "linkDetail": "/report/acb-tiem-nang-6a1e9781d179f392c9052f2a.chn",
                        "linkStocks": {
                            "ACB": "/hose/ACB-ngan-hang-thuong-mai-co-phan-a-chau.chn"
                        },
                        "config": "https://cafefnew.mediacdn.vn/Images/Uploaded/DuLieuDownload/PhanTichBaoCao/",
                        "isshow": True,
                    },
                    {
                        "id": "test-id-2",
                        "symbol": "TPB, ACB, VIB",
                        "dateDeploy": "2026-06-01T00:00:00Z",
                        "title": "Cập nhật ngành Ngân hàng",
                        "body": "Ngành ngân hàng có nhiều điểm sáng.",
                        "fileName": "bank_sector.pdf",
                        "imageThumb": "",
                        "resourceCode": "VCBS",
                        "resourceName": "VCBS",
                        "isHot": 0,
                        "categoryIDs": "341,",
                        "sourceID": 38,
                        "catID": 3,
                        "reportType": "Báo cáo ngành",
                        "reportID": 2,
                        "linkDetail": "/report/ngan-hang-cap-nhat.chn",
                        "linkStocks": {
                            "TPB": "/hose/TPB.chn",
                            "ACB": "/hose/ACB.chn",
                            "VIB": "/hose/VIB.chn",
                        },
                        "config": "https://cafefnew.mediacdn.vn/",
                        "isshow": True,
                    },
                ]
            },
        }

    # --- source_name ---

    def test_source_name(self, crawler):
        assert crawler.source_name == "cafef"

    # --- _transform_item ---

    def test_transform_item_single_symbol(self, crawler, mock_api_response):
        item = mock_api_response["value"]["items"][0]
        result = crawler._transform_item(item)
        assert result is not None
        assert result["article_id"] == "test-id-1"
        assert result["symbols"] == ["ACB"]
        assert result["title"] == "ACB - Tiềm năng định giá lại"
        assert result["source_name"] == "cafef"
        assert "cafef.vn" in result["url"]
        assert "ACB giao dịch ở mức P/B 1.2x." in result["content"]

    def test_transform_item_multi_symbol(self, crawler, mock_api_response):
        item = mock_api_response["value"]["items"][1]
        result = crawler._transform_item(item)
        assert result is not None
        assert set(result["symbols"]) == {"TPB", "ACB", "VIB"}
        assert result["article_id"] == "test-id-2"
        assert result["_meta"]["report_type"] == "Báo cáo ngành"
        assert result["_meta"]["analyst_company"] == "VCBS"

    def test_transform_item_skips_empty_linkStocks(self, crawler):
        item = {
            "id": "no-symbols",
            "symbol": "UNKNOWN",
            "title": "Some article",
            "body": "No stocks here",
            "linkStocks": {},
        }
        result = crawler._transform_item(item)
        assert result is None

    def test_transform_item_skips_empty_title(self, crawler):
        item = {
            "id": "no-title",
            "symbol": "ACB",
            "title": "",
            "body": "Some content",
            "linkStocks": {"ACB": "/hose/ACB.chn"},
        }
        result = crawler._transform_item(item)
        assert result is None

    # --- _fetch_symbol_reports ---

    @pytest.mark.asyncio
    async def test_fetch_symbol_reports_returns_articles(self, crawler, mock_api_response):
        mock_client = _make_mock_client(mock_api_response)
        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawler._fetch_symbol_reports("ACB")

        assert len(results) == 2
        assert results[0]["article_id"] == "test-id-1"
        assert results[1]["article_id"] == "test-id-2"

    @pytest.mark.asyncio
    async def test_fetch_symbol_reports_empty_response(self, crawler):
        empty = {"isSuccess": True, "value": {"items": []}}
        mock_client = _make_mock_client(empty)
        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawler._fetch_symbol_reports("INVALID")

        assert results == []

    @pytest.mark.asyncio
    async def test_fetch_symbol_reports_respects_max_articles(self):
        crawler = CafeFCrawler(max_articles=1)
        items = [
            {
                "id": f"id-{i}",
                "symbol": "ACB",
                "title": f"Article {i}",
                "body": "Content",
                "linkDetail": f"/report/art{i}.chn",
                "linkStocks": {"ACB": "/hose/ACB.chn"},
                "dateDeploy": "2026-06-01T00:00:00Z",
            }
            for i in range(5)
        ]
        page_response = {"isSuccess": True, "value": {"items": items}}
        mock_client = _make_mock_client(page_response)
        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawler._fetch_symbol_reports("ACB")

        assert len(results) == 1

    # --- crawl with symbols ---

    @pytest.mark.asyncio
    async def test_crawl_no_symbols_returns_empty(self, crawler):
        result = await crawler.crawl(tracked_symbols=[])
        assert result == []

    @pytest.mark.asyncio
    async def test_crawl_deduplicates_by_url(self, crawler, mock_api_response):
        multi_response = {
            "isSuccess": True,
            "value": {
                "items": [
                    {
                        "id": "id-1",
                        "symbol": "ACB",
                        "title": "Article 1",
                        "body": "Content",
                        "linkDetail": "/report/same-link.chn",
                        "linkStocks": {"ACB": "/hose/ACB.chn"},
                        "dateDeploy": "2026-06-01T00:00:00Z",
                    },
                    {
                        "id": "id-2",
                        "symbol": "ACB",
                        "title": "Article 2",
                        "body": "Content",
                        "linkDetail": "/report/same-link.chn",
                        "linkStocks": {"ACB": "/hose/ACB.chn"},
                        "dateDeploy": "2026-06-01T00:00:00Z",
                    },
                ]
            },
        }
        mock_client = _make_mock_client(multi_response)
        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await crawler.crawl(tracked_symbols=["ACB"])

        assert len(results) == 1  # same URL deduplicated

    @pytest.mark.asyncio
    async def test_crawl_falls_back_to_sitemap_on_api_error(self, crawler):
        fallback_response = {
            "title": "Fallback Article",
            "content": "<p>Content</p>",
            "excerpt": "",
            "url": "https://cafef.vn/fallback.chn",
            "published_at": None,
            "symbols": ["ACB"],
            "source_name": "cafef",
        }

        async def fake_api_fail(symbol):
            raise Exception("API error")

        async def fake_sitemap(symbol):
            return [fallback_response]

        with patch.object(crawler, "_fetch_symbol_reports", side_effect=fake_api_fail):
            with patch.object(crawler, "_fallback_sitemap", side_effect=fake_sitemap):
                results = await crawler.crawl(tracked_symbols=["ACB"])

        assert len(results) == 1
        assert results[0]["title"] == "Fallback Article"
        assert results[0]["symbols"] == ["ACB"]

    # --- _fallback_sitemap ---

    @pytest.mark.asyncio
    async def test_fallback_sitemap_calls_sitemap_crawler_and_retags(self, crawler):
        mock_article = {
            "title": "Sitemap Article",
            "content": "<p>Content</p>",
            "url": "https://cafef.vn/sitemap.chn",
            "published_at": None,
            "symbols": [],
            "source_name": "cafef",
        }

        with patch(
            "app.stream_b.crawlers.cafef_crawler_sitemap.CafeFSitemapCrawler"
        ) as MockCrawler:
            mock_instance = AsyncMock()
            mock_instance.crawl = AsyncMock(return_value=[mock_article])
            MockCrawler.return_value = mock_instance

            results = await crawler._fallback_sitemap("FPT")

        mock_instance.crawl.assert_called_once()
        assert len(results) == 1
        assert results[0]["symbols"] == ["FPT"]
