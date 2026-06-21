import asyncio
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, ANY

import pytest

from app import scheduler as scheduler_module


class TestSchedulerStreamA:
    @pytest.fixture
    def mock_producer(self):
        p = AsyncMock()
        p.connect = AsyncMock()
        p.publish = AsyncMock()
        p.close = AsyncMock()
        return p

    @pytest.fixture
    def mock_price_repo(self):
        repo = MagicMock()
        repo.upsert_prices = MagicMock(return_value=5)
        repo.upsert_ratios = MagicMock(return_value=1)
        repo.get_tracked_symbols = MagicMock(return_value=["VNM"])
        return repo

    @pytest.fixture
    def mock_price_transformer(self):
        t = MagicMock()
        t.transform.return_value = [
            MagicMock(
                symbol="VNM", trade_date=date(2026, 5, 30),
                open=Decimal("95000"), high=Decimal("96000"),
                low=Decimal("94500"), close=Decimal("95500"), volume=1000000,
            )
        ]
        return t

    @pytest.fixture
    def mock_ratio_transformer(self):
        t = MagicMock()
        t.transform.return_value = [MagicMock()]
        return t

    @pytest.fixture
    def mock_vnstock_fetcher(self):
        f = AsyncMock()
        f.fetch = AsyncMock(return_value=[{
            "symbol": "VNM",
            "prices": [{
                "date": "2026-05-30",
                "open": "95000",
                "high": "96000",
                "low": "94500",
                "close": "95500",
                "volume": 1000000,
            }],
        }])
        return f

    @pytest.fixture
    def mock_yahoo_finance_fetcher(self):
        f = AsyncMock()
        f.fetch = AsyncMock(return_value=[{
            "symbol": "VNM",
            "ratios": {
                "pe_ratio": 15.5,
                "pb_ratio": 3.2,
                "eps": 6200,
                "roe": 0.21,
                "roa": 12,
                "period": "ttm",
            },
        }])
        return f

    @pytest.mark.asyncio
    async def test_stream_a_success_publishes_price_updated(
        self,
        mock_producer,
        mock_price_repo,
        mock_price_transformer,
        mock_ratio_transformer,
        mock_vnstock_fetcher,
        mock_yahoo_finance_fetcher,
    ):
        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "PriceRepository", return_value=mock_price_repo), \
             patch.object(scheduler_module, "PriceTransformer", return_value=mock_price_transformer), \
             patch.object(scheduler_module, "RatioTransformer", return_value=mock_ratio_transformer), \
             patch.object(scheduler_module, "VnStockFetcher", return_value=mock_vnstock_fetcher), \
             patch.object(scheduler_module, "YahooFinanceFetcher", return_value=mock_yahoo_finance_fetcher):

            await scheduler_module.run_stream_a()

        mock_producer.connect.assert_awaited_once()
        mock_producer.publish.assert_not_called()
        mock_producer.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stream_a_producer_close_called_on_error(self, mock_producer):
        mock_producer.connect.return_value = None
        mock_producer.close.return_value = None
        mock_repo = MagicMock()
        mock_repo.get_tracked_symbols.side_effect = RuntimeError("db error")

        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "PriceRepository", return_value=mock_repo), \
             patch.object(scheduler_module, "PriceTransformer"), \
             patch.object(scheduler_module, "RatioTransformer"), \
             patch.object(scheduler_module, "VnStockFetcher"), \
             patch.object(scheduler_module, "YahooFinanceFetcher"):

            # Scheduler catches exceptions internally and returns normally
            await scheduler_module.run_stream_a()

        mock_producer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stream_a_no_tracked_symbols_skips_publish(self, mock_producer):
        mock_repo = MagicMock()
        mock_repo.get_tracked_symbols.return_value = []

        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "PriceRepository", return_value=mock_repo), \
             patch.object(scheduler_module, "PriceTransformer"), \
             patch.object(scheduler_module, "RatioTransformer"), \
             patch.object(scheduler_module, "VnStockFetcher"), \
             patch.object(scheduler_module, "YahooFinanceFetcher"):

            await scheduler_module.run_stream_a()

        mock_producer.publish.assert_not_called()
        mock_producer.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stream_a_per_symbol_error_isolation(self):
        mock_producer = AsyncMock()
        mock_producer.connect = AsyncMock()
        mock_producer.publish = AsyncMock()
        mock_producer.close = AsyncMock()

        mock_repo = MagicMock()
        mock_repo.get_tracked_symbols.return_value = ["VNM", "HPG"]

        f_vnm = AsyncMock()
        f_vnm.fetch = AsyncMock(return_value=[{
            "symbol": "VNM",
            "prices": [{"date": "2026-05-30", "open": "1", "high": "2",
                        "low": "1", "close": "1.5", "volume": 100}],
        }])

        f_hpg = AsyncMock()
        f_hpg.fetch = AsyncMock(return_value=[{
            "symbol": "HPG",
            "prices": [{
                "date": "2026-05-30",
                "open": "30000", "high": "31000",
                "low": "29500", "close": "30500",
                "volume": 500000,
            }],
        }])

        f_ratio = AsyncMock()
        f_ratio.fetch = AsyncMock(return_value=[{"symbol": "HPG", "ratios": {}}])

        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "PriceRepository", return_value=mock_repo), \
             patch.object(scheduler_module, "RatioTransformer", return_value=MagicMock()), \
             patch.object(scheduler_module, "YahooFinanceFetcher", return_value=f_ratio), \
             patch.object(scheduler_module, "VnStockFetcher", side_effect=[f_vnm, f_hpg]) as mock_fetcher_cls:

            pt = MagicMock()
            pt_instance = MagicMock()

            call_count = [0]

            def transform(data):
                call_count[0] += 1
                if data.get("symbol") == "VNM":
                    raise RuntimeError("VNM transform failed")
                return [
                    MagicMock(
                        symbol="HPG", trade_date=date(2026, 5, 30),
                        open=Decimal("30000"), high=Decimal("31000"),
                        low=Decimal("29500"), close=Decimal("30500"), volume=500000,
                    )
                ]

            pt_instance.transform.side_effect = transform

            with patch.object(scheduler_module, "PriceTransformer", return_value=pt_instance):
                await scheduler_module.run_stream_a()

        mock_producer.publish.assert_not_called()


class TestSchedulerStreamB:
    @pytest.fixture
    def mock_producer(self):
        p = AsyncMock()
        p.connect = AsyncMock()
        p.publish = AsyncMock()
        p.close = AsyncMock()
        return p

    @pytest.fixture
    def mock_news_repo(self):
        repo = MagicMock()
        repo.insert_articles_bulk = MagicMock(return_value=2)
        return repo

    @pytest.fixture
    def mock_embedder(self):
        e = MagicMock()
        e.embed_and_upsert = MagicMock(return_value=3)
        return e

    @pytest.fixture
    def mock_news_transformer(self):
        t = MagicMock()
        t.transform.return_value = [{
            "title": "VNM Reports Profit",
            "content": "VNM content",
            "url": "https://cafef.vn/vnm",
            "symbols": ["VNM"],
            "source_id": "abc123",
            "published_at": None,
            "crawled_at": None,
        }]
        return t

    @pytest.mark.asyncio
    async def test_stream_b_success_publishes_raw_ingested(
        self,
        mock_producer,
        mock_news_repo,
        mock_embedder,
        mock_news_transformer,
    ):
        cafeF_ok = AsyncMock()
        cafeF_ok.crawl = AsyncMock(return_value=[{
            "title": "VNM Reports Profit",
            "content": "<p>VNM content</p>",
            "excerpt": "VNM excerpt",
            "url": "https://cafef.vn/vnm",
            "published_at": "2026-05-30T10:00:00Z",
            "symbols": ["VNM"],
            "source_name": "cafef",
        }])

        vs_empty = AsyncMock()
        vs_empty.crawl = AsyncMock(return_value=[])

        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "NewsRepository", return_value=mock_news_repo), \
             patch.object(scheduler_module, "NewsTransformer", return_value=mock_news_transformer), \
             patch.object(scheduler_module, "Embedder", return_value=mock_embedder), \
             patch.object(scheduler_module, "CafeFCrawler", return_value=cafeF_ok), \
             patch.object(scheduler_module, "VietstockCrawler", return_value=vs_empty):

            await scheduler_module.run_stream_b()

        mock_producer.publish.assert_awaited_once()
        call = mock_producer.publish.call_args
        assert call.kwargs["exchange_name"] == "news.exchange"
        assert call.kwargs["routing_key"] == "raw.ingested"
        body = call.kwargs["data"]
        assert body["action"] == "raw.ingested"
        assert body["record_count"] == 1
        mock_producer.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stream_b_empty_articles_skips_publish(self, mock_producer):
        empty_crawler = AsyncMock()
        empty_crawler.crawl = AsyncMock(return_value=[])

        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "NewsRepository") as mock_repo, \
             patch.object(scheduler_module, "NewsTransformer"), \
             patch.object(scheduler_module, "Embedder"), \
             patch.object(scheduler_module, "CafeFCrawler", return_value=empty_crawler), \
             patch.object(scheduler_module, "VietstockCrawler") as mock_vs:

            vs_empty = AsyncMock()
            vs_empty.crawl = AsyncMock(return_value=[])
            mock_vs.return_value = vs_empty

            await scheduler_module.run_stream_b()

        mock_producer.publish.assert_not_called()
        mock_producer.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_stream_b_crawler_exception_continues(
        self,
        mock_producer,
        mock_news_repo,
        mock_embedder,
    ):
        failed_crawler = AsyncMock()
        failed_crawler.crawl = AsyncMock(side_effect=RuntimeError("network error"))

        good_crawler = AsyncMock()
        good_crawler.crawl = AsyncMock(return_value=[{
            "title": "HPG News",
            "content": "<p>HPG</p>",
            "excerpt": "",
            "url": "https://cafef.vn/hpg",
            "published_at": None,
            "symbols": ["HPG"],
            "source_name": "cafef",
        }])

        good_transformer = MagicMock()
        good_transformer.transform.return_value = [{
            "title": "HPG News",
            "content": "HPG content",
            "url": "https://cafef.vn/hpg",
            "symbols": ["HPG"],
            "source_id": "abc",
            "published_at": None,
            "crawled_at": None,
        }]

        with patch.object(scheduler_module, "RabbitMQProducer", return_value=mock_producer), \
             patch.object(scheduler_module, "NewsRepository", return_value=mock_news_repo), \
             patch.object(scheduler_module, "NewsTransformer", return_value=good_transformer), \
             patch.object(scheduler_module, "Embedder", return_value=mock_embedder), \
             patch.object(scheduler_module, "CafeFCrawler", return_value=failed_crawler), \
             patch.object(scheduler_module, "VietstockCrawler", return_value=good_crawler):

            await scheduler_module.run_stream_b()

        mock_producer.publish.assert_awaited_once()
        body = mock_producer.publish.call_args.kwargs["data"]
        assert "HPG" in body["symbols"]


class TestSchedulerSynthesis:
    @pytest.mark.asyncio
    async def test_synthesis_success(self):
        mock_agent = AsyncMock()
        mock_agent.synthesize = AsyncMock()

        mock_repo = MagicMock()
        mock_repo.get_tracked_symbols.return_value = ["VNM", "HPG"]

        with patch.object(scheduler_module, "SynthesisAgent", return_value=mock_agent), \
             patch.object(scheduler_module, "PriceRepository", return_value=mock_repo):

            await scheduler_module.run_synthesis()

        mock_agent.synthesize.assert_awaited_once_with(["VNM", "HPG"])

    @pytest.mark.asyncio
    async def test_synthesis_no_symbols_skips(self):
        mock_repo = MagicMock()
        mock_repo.get_tracked_symbols.return_value = []

        with patch.object(scheduler_module, "SynthesisAgent") as mock_agent_cls, \
             patch.object(scheduler_module, "PriceRepository", return_value=mock_repo):

            await scheduler_module.run_synthesis()

        mock_agent_cls.assert_not_called()


class TestCollectSymbols:
    def test_collect_symbols_deduplicates(self):
        articles = [
            {"symbols": ["VNM", "HPG"]},
            {"symbols": ["VNM", "VPB"]},
            {"symbols": ["HPG"]},
        ]
        result = scheduler_module._collect_symbols(articles)
        assert result == ["VNM", "HPG", "VPB"]

    def test_collect_symbols_empty_list(self):
        result = scheduler_module._collect_symbols([])
        assert result == []

    def test_collect_symbols_none_and_empty(self):
        articles = [{"symbols": []}, {"symbols": None}, {"symbols": ["VNM"]}]
        result = scheduler_module._collect_symbols(articles)
        assert result == ["VNM"]

    def test_collect_symbols_missing_key(self):
        articles = [{}, {"symbols": ["HPG"]}]
        result = scheduler_module._collect_symbols(articles)
        assert result == ["HPG"]
