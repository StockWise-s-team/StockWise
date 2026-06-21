import asyncio
import logging
import threading
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.rabbitmq.producer import RabbitMQProducer
from app.stream_a.fetchers.vnstock_fetcher import VnStockFetcher
from app.stream_a.fetchers.yahoo_finance_fetcher import YahooFinanceFetcher
from app.stream_a.transformers.price_transformer import PriceTransformer
from app.stream_a.transformers.ratio_transformer import RatioTransformer
from app.stream_a.repositories.price_repository import PriceRepository
from app.stream_b.crawlers.cafef_crawler import CafeFCrawler
from app.stream_b.crawlers.vietstock_crawler import VietstockCrawler
from app.stream_b.transformers.news_transformer import NewsTransformer
from app.stream_b.repositories.news_repository import NewsRepository
from app.stream_b.embedder import Embedder
from app.synthesis.synthesis_agent import SynthesisAgent
from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository
from app.sources.source_repository import SourceRepository
from app.stream_c.runner import run_stream_c_loop

logger = logging.getLogger(__name__)

_EXCHANGE_PRICE = "market.exchange"
_ROUTING_PRICE = "price.updated"
_EXCHANGE_NEWS = "news.exchange"
_ROUTING_NEWS = "raw.ingested"

_CRAWLER_MAP = {
    "cafef": "CafeFCrawler",
    "vietstock": "VietstockCrawler",
}


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    # Drain httpx/anyio background cleanup tasks (e.g. AsyncClient.aclose)
    # scheduled after the main coroutine returned but before the loop stopped.
    try:
        pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
        if pending:
            loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )
    except Exception:
        pass
    loop.stop()
    loop.close()


def _start_stream_c_thread() -> None:
    """Khởi động stream_c trong thread riêng với event-loop của chính nó."""
    def _thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_stream_c_loop())
        except Exception as exc:
            logger.error("[StreamC] Thread crashed: %s", exc)
        finally:
            loop.close()

    t = threading.Thread(target=_thread_target, name="stream_c", daemon=True)
    t.start()
    logger.info("[StreamC] Background thread started")


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_stream_a(),)).start(), "interval", hours=4, id="stream_a", next_run_time=datetime.now(timezone.utc))
    scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_stream_b(),)).start(), "interval", hours=4, id="stream_b", next_run_time=datetime.now(timezone.utc))
    scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_synthesis(),)).start(), "interval", hours=4, id="synthesis", next_run_time=datetime.now(timezone.utc))
    # stream_c chạy liên tục trong thread riêng (không dùng APScheduler interval)
    _start_stream_c_thread()
    scheduler.start()
    return scheduler


async def _auto_seed_missing_metadata(tracked: list[str]) -> None:
    """Seed company_info and financial_ratios for symbols that don't have them yet."""
    from app.synthesis.wiki_repository import WikiRepository
    from app.scripts.seed import _seed_company_info, _seed_financial_ratios

    wiki_repo = WikiRepository()
    missing_company: list[str] = []
    missing_ratios: list[str] = []

    for symbol in tracked:
        try:
            info = wiki_repo.get_company_info(symbol)
            if not info or info.get("company_name") in (None, "", symbol):
                missing_company.append(symbol)
        except Exception:
            missing_company.append(symbol)

        try:
            ratios = wiki_repo.get_ratios(symbol)
            if not ratios:
                missing_ratios.append(symbol)
        except Exception:
            missing_ratios.append(symbol)

    if missing_company:
        logger.info("[StreamA] Auto-seeding company info for %d symbols: %s", len(missing_company), missing_company)
        try:
            _seed_company_info(missing_company)
        except Exception as exc:
            logger.warning("[StreamA] Company info auto-seed error: %s", exc)

    if missing_ratios:
        logger.info("[StreamA] Auto-seeding financial ratios for %d symbols: %s", len(missing_ratios), missing_ratios)
        try:
            _seed_financial_ratios(missing_ratios)
        except Exception as exc:
            logger.warning("[StreamA] Ratios auto-seed error: %s", exc)


async def run_stream_a() -> None:
    repo = PipelineRunsRepository()
    run_id = None
    errors = []

    try:
        run_id = repo.create_run(
            run_type="stream_a",
            trigger_type="scheduled",
        )
    except Exception as e:
        logger.error("[StreamA] Failed to create DB run record: %s", e)
        run_id = None

    logger.info("[StreamA] Starting price data pipeline")
    producer = RabbitMQProducer()
    price_repo = PriceRepository()
    price_transformer = PriceTransformer()
    ratio_transformer = RatioTransformer()
    tracked = []

    try:
        await producer.connect()
        tracked = price_repo.get_tracked_symbols()

        if not tracked:
            logger.warning("[StreamA] No tracked symbols found, skipping run")
        else:
            # Auto-seed company info & ratios for any symbols missing them
            try:
                await _auto_seed_missing_metadata(tracked)
            except Exception as exc:
                logger.warning("[StreamA] Auto-seed metadata failed (non-fatal): %s", exc)

            for i, symbol in enumerate(tracked):
                sym_errors = []
                try:
                    sym_errors = await _fetch_and_save_prices(
                        symbol, price_transformer, ratio_transformer, price_repo, producer
                    )
                    if run_id:
                        repo.add_symbol_result(run_id, symbol, "success")
                except Exception as exc:
                    err = f"{type(exc).__name__}: {exc}"
                    sym_errors.append(err)
                    logger.error(
                        "[StreamA] Failed to process symbol %s: %s", symbol, exc
                    )
                    if run_id:
                        repo.add_symbol_result(run_id, symbol, "error", err)
                    errors.append(f"{symbol}: {exc}")

                if i < len(tracked) - 1:
                    await asyncio.sleep(4)

        if run_id:
            final_status = "success" if not errors else "partial"
            repo.finish_run(run_id, final_status, errors)
            run_id = None

    except Exception as exc:
        logger.error("[StreamA] Pipeline failed: %s: %s", type(exc).__name__, exc)
        if run_id:
            repo.finish_run(run_id, "failed", [str(exc)])
            run_id = None
        errors.append(str(exc))
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
    producer: RabbitMQProducer,  # kept for signature compatibility, no longer used
) -> list[str]:
    """Fetch lịch sử giá & ratios, lưu vào DB.

    NOTE: publish RabbitMQ đã được chuyển sang stream_c (real-time feed).
    Stream_a chỉ còn nhiệm vụ upsert historical data vào PostgreSQL.
    """
    errors: list[str] = []
    fetcher = VnStockFetcher()
    ratio_fetcher = YahooFinanceFetcher()

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

    # Publish đã được chuyển sang stream_c — không publish ở đây nữa
    # (stream_c cung cấp giá real-time cho market-service với chu kỳ ngắn hơn)
    return all_symbols


async def run_stream_b() -> None:
    repo = PipelineRunsRepository()
    run_id = None
    errors = []
    symbols_ingested: list[str] = []

    try:
        run_id = repo.create_run(
            run_type="stream_b",
            trigger_type="scheduled",
        )
    except Exception as e:
        logger.error("[StreamB] Failed to create DB run record: %s", e)
        run_id = None

    logger.info("[StreamB] Starting news ingestion pipeline")
    producer = RabbitMQProducer()
    news_repo = NewsRepository()
    news_transformer = NewsTransformer()
    embedder = Embedder()

    try:
        await producer.connect()

        source_repo = SourceRepository()
        active_sources = source_repo.get_active_sources()
        logger.info("[StreamB] Active sources from DB: %s", [s.crawler_type for s in active_sources])

        tracked_repo = PriceRepository()
        tracked_symbols = tracked_repo.get_tracked_symbols()
        logger.info("[StreamB] Tracked symbols for priority: %s", tracked_symbols)

        async def crawl_safe(source):
            ctype = source.crawler_type
            if ctype not in _CRAWLER_MAP:
                raise ValueError(f"No crawler found for source type: {ctype}")
            crawler_class_name = _CRAWLER_MAP[ctype]
            crawler_class = globals().get(crawler_class_name)
            if not crawler_class:
                raise ValueError(f"Crawler class {crawler_class_name} not found in globals")
            return await crawler_class().crawl(tracked_symbols=tracked_symbols)

        results = await asyncio.gather(
            *[crawl_safe(s) for s in active_sources],
            return_exceptions=True,
        )

        all_articles: list[dict] = []
        all_sources: list[str] = []

        for i, result in enumerate(results):
            src_name = active_sources[i].crawler_type
            if isinstance(result, Exception):
                err = f"{src_name}: {type(result).__name__}: {result}"
                errors.append(err)
                logger.warning("[StreamB] Crawler %s failed: %s", src_name, result)
                continue

            logger.info("[StreamB] %s returned %d articles", src_name, len(result))
            if result:
                all_articles.extend(result)
                all_sources.append(result[0].get("source_name", ""))
                # Log first article sample for debugging
                sample = result[0]
                logger.debug(
                    "[StreamB] %s sample — title='%s', symbols=%s, url=%s",
                    src_name,
                    sample.get("title", "")[:80],
                    sample.get("symbols", []),
                    sample.get("url", "")[:80],
                )

        if not all_articles:
            logger.info("[StreamB] No articles scraped, skipping")
        else:
            normalized = news_transformer.transform(all_articles)
            # Convert dataclasses to dicts for embedder (uses .get())
            from dataclasses import asdict, is_dataclass
            normalized_dicts = [asdict(a) if is_dataclass(a) else a for a in normalized]
            await _embed_and_publish(
                normalized_dicts, normalized, news_repo, embedder, producer, all_sources
            )
            symbols_ingested = _collect_symbols(normalized)

        if run_id:
            final_status = "success" if not errors else "partial"
            repo.finish_run(run_id, final_status, errors)
            run_id = None

    except Exception as exc:
        err_str = f"{type(exc).__name__}: {exc}"
        logger.error("[StreamB] Pipeline failed: %s", exc)
        if run_id:
            repo.finish_run(run_id, "failed", [err_str])
            run_id = None
        errors.append(err_str)
    finally:
        close_coro = producer.close()
        if asyncio.iscoroutine(close_coro):
            await close_coro
        else:
            close_coro.close()


async def _embed_and_publish(
    normalized_dicts: list[dict],
    normalized_models: list,
    news_repo: NewsRepository,
    embedder: Embedder,
    producer: RabbitMQProducer,
    all_sources: list[str],
) -> None:
    inserted = news_repo.insert_articles_bulk(normalized_models)
    logger.info("[StreamB] Inserted %d articles into DB", inserted)

    try:
        chunks_embedded = await asyncio.to_thread(embedder.embed_and_upsert, normalized_dicts)
        logger.info("[StreamB] Embedded %d chunks into Qdrant", chunks_embedded)
    except Exception as exc:
        logger.warning("[StreamB] Embedding failed (will retry next run): %s", exc)
        chunks_embedded = 0

    all_symbols = _collect_symbols(normalized_dicts)

    await producer.publish(
        exchange_name=_EXCHANGE_NEWS,
        routing_key=_ROUTING_NEWS,
        data={
            "symbols": all_symbols,
            "source": all_sources[0] if all_sources else "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "record_count": len(normalized_dicts),
            "action": _ROUTING_NEWS,
        },
    )


def _collect_symbols(articles: list) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for article in articles:
        if not article:
            continue
        if isinstance(article, dict):
            symbols = article.get("symbols")
        else:
            symbols = getattr(article, "symbols", None)
        if not symbols:
            continue
        for sym in symbols:
            if sym not in seen:
                seen.add(sym)
                result.append(sym)
    return result


async def run_synthesis() -> None:
    repo = PipelineRunsRepository()
    run_id = None
    errors = []

    try:
        run_id = repo.create_run(
            run_type="synthesis",
            trigger_type="scheduled",
        )
    except Exception as e:
        logger.error("[Synthesis] Failed to create DB run record: %s", e)
        run_id = None

    logger.info("[Synthesis] Starting synthesis pipeline")
    price_repo = PriceRepository()

    try:
        tracked = price_repo.get_tracked_symbols()
        if not tracked:
            logger.warning("[Synthesis] No tracked symbols found")
            if run_id:
                repo.finish_run(run_id, "success", [])
                run_id = None
            return

        agent = SynthesisAgent()
        results = await agent.synthesize(tracked)
        if run_id:
            for r in results:
                if r.success:
                    repo.add_symbol_result(run_id, r.symbol, "success")
                else:
                    repo.add_symbol_result(run_id, r.symbol, "error", r.error or "Unknown error")

        logger.info("[Synthesis] Completed for %d symbols", len(tracked))
        if run_id:
            final_status = "success" if not errors else "partial"
            repo.finish_run(run_id, final_status, errors)
            run_id = None

    except Exception as exc:
        err_str = f"{type(exc).__name__}: {exc}"
        logger.error("[Synthesis] Pipeline failed: %s", exc)
        if run_id:
            repo.finish_run(run_id, "failed", [err_str])
            run_id = None
        errors.append(err_str)
