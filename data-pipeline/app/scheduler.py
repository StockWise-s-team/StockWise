import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.rabbitmq.producer import RabbitMQProducer
from app.stream_a.fetchers.vnstock_fetcher import VnStockFetcher
from app.stream_a.fetchers.ck_api_fetcher import CkApiFetcher
from app.stream_a.transformers.price_transformer import PriceTransformer
from app.stream_a.transformers.ratio_transformer import RatioTransformer
from app.stream_a.repositories.price_repository import PriceRepository
from app.stream_b.crawlers.cafef_crawler import CafeFCrawler
from app.stream_b.crawlers.vietstock_crawler import VietstockCrawler
from app.stream_b.crawlers.reuters_vn_crawler import ReutersVNCrawler
from app.stream_b.transformers.news_transformer import NewsTransformer
from app.stream_b.repositories.news_repository import NewsRepository
from app.stream_b.embedder import Embedder
from app.synthesis.synthesis_agent import SynthesisAgent

logger = logging.getLogger(__name__)

_EXCHANGE_PRICE = "market.exchange"
_ROUTING_PRICE = "price.updated"
_EXCHANGE_NEWS = "news.exchange"
_ROUTING_NEWS = "raw.ingested"

_CRAWLER_SOURCES = ["cafef", "vietstock", "reuters_vn"]


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_stream_a, "interval", hours=4, id="stream_a")
    scheduler.add_job(run_stream_b, "interval", hours=4, id="stream_b")
    scheduler.add_job(run_synthesis, "interval", hours=4, id="synthesis")
    scheduler.start()
    return scheduler


async def run_stream_a() -> None:
    logger.info("[StreamA] Starting price data pipeline")
    producer = RabbitMQProducer()
    price_repo = PriceRepository()
    price_transformer = PriceTransformer()
    ratio_transformer = RatioTransformer()

    try:
        await producer.connect()
        tracked = price_repo.get_tracked_symbols()

        if not tracked:
            logger.warning("[StreamA] No tracked symbols found, skipping run")
        else:
            for symbol in tracked:
                try:
                    await _fetch_and_save_prices(
                        symbol, price_transformer, ratio_transformer, price_repo, producer
                    )
                except Exception as exc:
                    logger.error(
                        "[StreamA] Failed to process symbol %s: %s: %s",
                        symbol, type(exc).__name__, exc,
                    )
    finally:
        close_coro = producer.close()
        if asyncio.iscoroutine(close_coro):
            await close_coro
        else:
            close_coro.close()


async def _fetch_and_save_prices(
    symbol: str,
    price_transformer: PriceTransformer,
    ratio_transformer: RatioTransformer,
    repo: PriceRepository,
    producer: RabbitMQProducer,
) -> None:
    fetcher = VnStockFetcher()
    ratio_fetcher = CkApiFetcher()

    raw_prices = await fetcher.fetch([symbol])
    raw_ratios = await ratio_fetcher.fetch([symbol])

    all_symbols: list[str] = []

    for raw in raw_prices:
        sym = raw.get("symbol", symbol)
        bars = raw.get("prices", [])
        if bars:
            normalized = price_transformer.transform(raw)
            repo.upsert_prices(normalized)
            all_symbols.append(sym)
            logger.info("[StreamA] Fetched %d prices for %s", len(normalized), sym)

    for raw in raw_ratios:
        sym = raw.get("symbol", symbol)
        ratios = raw.get("ratios", {})
        if ratios:
            normalized = ratio_transformer.transform(raw)
            repo.upsert_ratios(normalized)
            if sym not in all_symbols:
                all_symbols.append(sym)
            logger.info("[StreamA] Fetched ratios for %s", sym)

    if all_symbols:
        await producer.publish(
            exchange_name=_EXCHANGE_PRICE,
            routing_key=_ROUTING_PRICE,
            data={
                "symbols": all_symbols,
                "source": "vnstock",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "record_count": len(all_symbols),
                "action": _ROUTING_PRICE,
            },
        )


async def run_stream_b() -> None:
    logger.info("[StreamB] Starting news ingestion pipeline")
    producer = RabbitMQProducer()
    news_repo = NewsRepository()
    news_transformer = NewsTransformer()
    embedder = Embedder()

    try:
        await producer.connect()

        results = await asyncio.gather(
            CafeFCrawler().crawl(),
            VietstockCrawler().crawl(),
            ReutersVNCrawler().crawl(),
            return_exceptions=True,
        )

        all_articles: list[dict] = []
        all_sources: list[str] = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning("[StreamB] Crawler %s failed: %s", _CRAWLER_SOURCES[i], result)
                continue

            if result:
                all_articles.extend(result)
                all_sources.append(result[0].get("source_name", ""))

        if not all_articles:
            logger.info("[StreamB] No articles scraped, skipping publish")
        else:
            normalized = news_transformer.transform(all_articles)
            inserted = news_repo.insert_articles_bulk(normalized)
            logger.info("[StreamB] Inserted %d articles into DB", inserted)

            chunks_embedded = embedder.embed_and_upsert(normalized)
            logger.info("[StreamB] Embedded %d chunks into Qdrant", chunks_embedded)

            all_symbols = _collect_symbols(normalized)

            await producer.publish(
                exchange_name=_EXCHANGE_NEWS,
                routing_key=_ROUTING_NEWS,
                data={
                    "symbols": all_symbols,
                    "source": all_sources[0] if all_sources else "unknown",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "record_count": len(all_articles),
                    "action": _ROUTING_NEWS,
                },
            )

    finally:
        close_coro = producer.close()
        if asyncio.iscoroutine(close_coro):
            await close_coro
        else:
            close_coro.close()


def _collect_symbols(articles: list[dict]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for article in articles:
        symbols = article.get("symbols")
        if not symbols:
            continue
        for sym in symbols:
            if sym not in seen:
                seen.add(sym)
                result.append(sym)
    return result


async def run_synthesis() -> None:
    logger.info("[Synthesis] Starting synthesis pipeline")
    price_repo = PriceRepository()

    try:
        tracked = price_repo.get_tracked_symbols()
        if not tracked:
            logger.warning("[Synthesis] No tracked symbols found")
            return

        agent = SynthesisAgent()
        await agent.synthesize(tracked)
        logger.info("[Synthesis] Completed for %d symbols", len(tracked))

    except Exception as exc:
        logger.error("[Synthesis] Failed: %s: %s", type(exc).__name__, exc)
