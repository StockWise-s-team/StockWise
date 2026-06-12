import asyncio
import logging
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

logger = logging.getLogger(__name__)

_EXCHANGE_PRICE = "market.exchange"
_ROUTING_PRICE = "price.updated"
_EXCHANGE_NEWS = "news.exchange"
_ROUTING_NEWS = "raw.ingested"

_CRAWLER_MAP = {
    "cafef": CafeFCrawler,
    "vietstock": VietstockCrawler,
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


_mock_price_cache = {}


async def run_mock_realtime_feed() -> None:
    import random
    logger.info("[MockRealtimeFeed] Starting simulation run...")
    price_repo = PriceRepository()
    producer = RabbitMQProducer()

    try:
        await producer.connect()
        tracked = price_repo.get_tracked_symbols()
        if not tracked:
            logger.warning("[MockRealtimeFeed] No tracked symbols found, skipping feed")
            return

        for symbol in tracked:
            # Check cache first
            if symbol not in _mock_price_cache:
                prices = price_repo.get_latest_prices(symbol, limit=2)
                if not prices:
                    # No price in DB, skip
                    logger.debug("[MockRealtimeFeed] No DB price for %s, skipping", symbol)
                    continue
                latest = prices[0]
                prev_close = float(prices[1]["close"]) if len(prices) > 1 else float(latest["close"])

                # Store in cache
                _mock_price_cache[symbol] = {
                    "open": float(latest["open"]),
                    "high": float(latest["high"]),
                    "low": float(latest["low"]),
                    "close": float(latest["close"]),
                    "volume": int(latest["volume"]),
                    "tradeDate": latest["trade_date"].isoformat() if hasattr(latest["trade_date"], "isoformat") else str(latest["trade_date"]),
                    "prev_close": prev_close
                }

            cache = _mock_price_cache[symbol]

            # Deviate the close price by a tiny amount (e.g. -0.5% to +0.5%)
            change_percent = (random.random() - 0.5) * 1.0  # -0.5% to +0.5%
            deviation = cache["close"] * (change_percent / 100.0)
            new_close = round(cache["close"] + deviation, 2)

            # Update high/low
            new_high = round(max(cache["high"], new_close), 2)
            new_low = round(min(cache["low"], new_close), 2)
            new_volume = cache["volume"] + random.randint(100, 2000)

            # Calculate change and changePercent relative to prev_close
            prev_close = cache["prev_close"]
            change = round(new_close - prev_close, 2)
            change_percent = round((new_close - prev_close) / prev_close * 100, 2) if prev_close != 0 else 0.0

            # Update cache
            cache["close"] = new_close
            cache["high"] = new_high
            cache["low"] = new_low
            cache["volume"] = new_volume

            # Publish update
            await producer.publish(
                exchange_name=_EXCHANGE_PRICE,
                routing_key=f"price.{symbol}",
                data={
                    "symbol": symbol,
                    "source": "mock_feed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": _ROUTING_PRICE,
                    "tradeDate": cache["tradeDate"],
                    "open": cache["open"],
                    "high": new_high,
                    "low": new_low,
                    "close": new_close,
                    "volume": new_volume,
                    "change": change,
                    "changePercent": change_percent,
                },
            )
            logger.info("[MockRealtimeFeed] Published mock price for %s: close=%s, changePercent=%s%%", symbol, new_close, change_percent)

    except Exception as e:
        logger.error("[MockRealtimeFeed] Error in mock realtime feed: %s", e)
    finally:
        close_coro = producer.close()
        if asyncio.iscoroutine(close_coro):
            await close_coro
        else:
            close_coro.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    import threading
    from app.config import settings
    scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_stream_a(),)).start(), "interval", seconds=settings.STREAM_A_INTERVAL_SECONDS, id="stream_a", next_run_time=datetime.now(timezone.utc))
    scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_stream_b(),)).start(), "interval", hours=4, id="stream_b", next_run_time=datetime.now(timezone.utc))
    scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_synthesis(),)).start(), "interval", hours=4, id="synthesis", next_run_time=datetime.now(timezone.utc))
    if settings.ENABLE_MOCK_FEED:
        scheduler.add_job(lambda: threading.Thread(target=_run_async, args=(run_mock_realtime_feed(),)).start(), "interval", seconds=5, id="mock_feed", next_run_time=datetime.now(timezone.utc))
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
    producer: RabbitMQProducer,
) -> list[str]:
    errors: list[str] = []

    # Check if price history exists to decide days_back
    try:
        latest_prices = repo.get_latest_prices(symbol, limit=1)
        days_back = 2 if latest_prices else 30
    except Exception as e:
        logger.warning("[StreamA] Failed to check price history for %s, defaulting to 30 days: %s", symbol, e)
        days_back = 30

    fetcher = VnStockFetcher(days_back=days_back)
    raw_prices = await fetcher.fetch([symbol])

    # Check if ratios exist to avoid rate limiting Yahoo Finance on frequent updates
    has_ratios = False
    try:
        conn = repo.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM financial_ratios WHERE symbol = %s LIMIT 1", (symbol,))
        has_ratios = cur.fetchone() is not None
        cur.close()
        conn.close()
    except Exception as e:
        logger.warning("[StreamA] Failed to check ratios for %s: %s", symbol, e)

    raw_ratios = []
    if not has_ratios:
        ratio_fetcher = YahooFinanceFetcher()
        raw_ratios = await ratio_fetcher.fetch([symbol])
    else:
        logger.debug("[StreamA] Ratios already exist for %s, skipping Yahoo Finance fetch", symbol)

    all_symbols: list[str] = []

    for raw in raw_prices:
        sym = raw.get("symbol", symbol)
        bars = raw.get("prices", [])
        if bars:
            normalized = price_transformer.transform(raw)
            repo.upsert_prices(normalized)
            all_symbols.append(sym)
            logger.info("[StreamA] Fetched %d prices for %s", len(normalized), sym)

            # Extract the latest bar for the WebSocket push payload.
            # bars are ordered newest-first from VnStock.
            latest_bar = bars[0]
            prev_close_raw = bars[1] if len(bars) > 1 else None

            try:
                prev_close = float(prev_close_raw.get("close")) if prev_close_raw else None
                latest_close = float(latest_bar.get("close"))
                change = round(latest_close - prev_close, 2) if prev_close else None
                change_percent = (
                    round((latest_close - prev_close) / prev_close * 100, 2)
                    if prev_close and prev_close != 0
                    else None
                )
            except (TypeError, ValueError):
                change = None
                change_percent = None

            await producer.publish(
                exchange_name=_EXCHANGE_PRICE,
                routing_key=f"price.{sym}",
                data={
                    "symbol": sym,
                    "source": "vnstock",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": _ROUTING_PRICE,
                    "tradeDate": latest_bar.get("date"),
                    "open": latest_bar.get("open"),
                    "high": latest_bar.get("high"),
                    "low": latest_bar.get("low"),
                    "close": latest_bar.get("close"),
                    "volume": latest_bar.get("volume"),
                    "change": change,
                    "changePercent": change_percent,
                },
            )
            logger.info("[StreamA] Published price update for %s: close=%s", sym, latest_bar.get("close"))

    for raw in raw_ratios:
        sym = raw.get("symbol", symbol)
        ratios = raw.get("ratios", {})
        if ratios:
            normalized = ratio_transformer.transform(raw)
            repo.upsert_ratios(normalized)
            if sym not in all_symbols:
                all_symbols.append(sym)
            logger.info("[StreamA] Fetched ratios for %s", sym)


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

        results = await asyncio.gather(
            *[crawler_class().crawl(tracked_symbols=tracked_symbols) for crawler_class in [_CRAWLER_MAP[s.crawler_type] for s in active_sources]],
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
            from dataclasses import asdict
            normalized_dicts = [asdict(a) for a in normalized]
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
        for symbol in tracked:
            try:
                await agent.synthesize([symbol])
                if run_id:
                    repo.add_symbol_result(run_id, symbol, "success")
            except Exception as exc:
                err = f"{type(exc).__name__}: {exc}"
                logger.error("[Synthesis] Failed for %s: %s", symbol, exc)
                if run_id:
                    repo.add_symbol_result(run_id, symbol, "error", err)
                errors.append(f"{symbol}: {err}")
                # continue to next symbol instead of re-raising

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
