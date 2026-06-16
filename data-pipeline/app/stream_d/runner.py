"""
stream_d / runner.py
====================
Runner cho stream_d: fetch intraday OHLCV bars (5m interval) moi 5 phut,
gui len RabbitMQ exchange `intraday.exchange` / routing key `intraday-price.updated`.

Exchange/queue contract moi:
  Exchange : intraday.exchange (topic, durable)
  Routing  : intraday-price.updated
  Consumer: market_service_intraday_q (cai dat o market-service)

Payload:
  {
    "symbols": [...],
    "bars": [
      {
        "symbol": "VHM",
        "time": "2026-06-16 09:15:00",
        "interval": "5m",
        "open": 137000.0,
        "high": 137500.0,
        "low": 136800.0,
        "close": 137100.0,
        "volume": 31000,
        "timestamp": "2026-06-16T09:51:00+00:00"
      },
      ...
    ],
    "source": "vnstock_quote_history",
    "timestamp": "2026-06-16T09:51:00+00:00",
    "record_count": 46,
    "action": "intraday-price.updated"
  }

Chu ky:
  - Moi 5 phut (300s) fetch tat ca tracked symbols
  - Chi chay trong gio giao dich VN (09:00-15:15 ICT)
  - Ngoai gio -> nghi IDLE_INTERVAL_SECONDS roi kiem tra lai
"""

import asyncio
import logging
from datetime import datetime, timezone, time as dt_time
from typing import Any

from app.rabbitmq.constants import INTRADAY_EXCHANGE, INTRADAY_PRICE_ROUTING_KEY
from app.rabbitmq.producer import RabbitMQProducer
from app.stream_a.repositories.price_repository import PriceRepository
from app.stream_d.fetcher import IntradayFetcher
from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository

logger = logging.getLogger(__name__)

# ── Cấu hình ──────────────────────────────────────────────────────────────────
LOOP_INTERVAL_SECONDS = 300   # 5 phut
IDLE_INTERVAL_SECONDS = 60   # ngoai gio thi nghi 60s roi kiem tra lai

# Gio giao dich VN (UTC): 09:00-15:15 ICT = 02:00-08:15 UTC
MARKET_OPEN_UTC  = dt_time(2, 0)
MARKET_CLOSE_UTC = dt_time(8, 15)


def _is_market_open() -> bool:
    from app.config import settings
    if not settings.TRADING_HOURS_ENABLED:
        return True
    now_utc = datetime.now(timezone.utc).time()
    return MARKET_OPEN_UTC <= now_utc <= MARKET_CLOSE_UTC


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Runner loop ────────────────────────────────────────────────────────────────

async def run_stream_d_loop() -> None:
    """
    Vong lap bat tận của stream_d.
    Đuoc goi tu scheduler.py qua thread rieng.
    """
    producer = RabbitMQProducer()
    price_repo = PriceRepository()
    fetcher = IntradayFetcher()

    logger.info(
        "[StreamD] Intraday OHLCV loop started -- interval=%ds, exchange=%s, routing=%s",
        LOOP_INTERVAL_SECONDS,
        INTRADAY_EXCHANGE,
        INTRADAY_PRICE_ROUTING_KEY,
    )

    await producer.connect()

    try:
        while True:
            if not _is_market_open():
                logger.debug("[StreamD] Outside market hours -- sleeping %ds", IDLE_INTERVAL_SECONDS)
                await asyncio.sleep(IDLE_INTERVAL_SECONDS)
                continue

            await _run_once(price_repo, fetcher, producer)
            await asyncio.sleep(LOOP_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        logger.info("[StreamD] Loop cancelled, shutting down")
    except Exception as exc:
        logger.error("[StreamD] Unexpected error in loop: %s: %s", type(exc).__name__, exc)
        raise
    finally:
        close_coro = producer.close()
        if asyncio.iscoroutine(close_coro):
            await close_coro


async def _run_once(
    price_repo: PriceRepository,
    fetcher: IntradayFetcher,
    producer: RabbitMQProducer,
) -> None:
    """Mot lan fetch + publish. Loi duoc log nhung khong raise."""
    run_repo = PipelineRunsRepository()
    run_id = None

    try:
        run_id = run_repo.create_run(
            run_type="stream_d",
            trigger_type="continuous",
        )
    except Exception as e:
        logger.warning("[StreamD] Cannot create run record: %s", e)

    try:
        tracked = price_repo.get_tracked_symbols()
        if not tracked:
            logger.warning("[StreamD] No tracked symbols, skipping")
            if run_id:
                run_repo.finish_run(run_id, "success", [])
            return

        logger.info("[StreamD] Fetching intraday bars for %d symbols", len(tracked))
        results = await fetcher.fetch(tracked)

        ok_records: list[dict[str, Any]] = []
        errors: list[str] = []

        for result in results:
            if isinstance(result, Exception):
                sym = result.args[0] if result.args else "?"
                err = f"{type(result).__name__}: {result}"
                errors.append(err)
                logger.error("[StreamD] Symbol %s exception: %s", sym, result)
                continue

            sym = result.get("symbol", "?")
            if "error" in result:
                err = result["error"]
                errors.append(f"{sym}: {err}")
                logger.warning("[StreamD] Symbol %s error: %s", sym, err)
                if run_id:
                    run_repo.add_symbol_result(run_id, sym, "error", err)
            else:
                bars = result.get("records", [])
                ok_records.append({
                    "symbol": sym,
                    "records": bars,
                })
                if run_id:
                    run_repo.add_symbol_result(run_id, sym, "success")

        # ── Publish lên RabbitMQ ─────────────────────────────────────────────
        if ok_records:
            payload = {
                "symbols":      [r["symbol"] for r in ok_records],
                "bars":        ok_records,
                "source":       fetcher.source_name,
                "timestamp":    _now_iso(),
                "record_count": sum(len(r["records"]) for r in ok_records),
                "action":       INTRADAY_PRICE_ROUTING_KEY,
            }
            try:
                await producer.publish(
                    exchange_name=INTRADAY_EXCHANGE,
                    routing_key=INTRADAY_PRICE_ROUTING_KEY,
                    data=payload,
                )
            except Exception as pub_exc:
                logger.warning(
                    "[StreamD] Publish failed (%s: %s) -- reconnecting and retrying once",
                    type(pub_exc).__name__, pub_exc,
                )
                try:
                    await producer.reconnect()
                    await producer.publish(
                        exchange_name=INTRADAY_EXCHANGE,
                        routing_key=INTRADAY_PRICE_ROUTING_KEY,
                        data=payload,
                    )
                except Exception as retry_exc:
                    logger.error(
                        "[StreamD] Retry publish also failed (%s: %s) -- skipping this cycle",
                        type(retry_exc).__name__, retry_exc,
                    )

            total_bars = sum(len(r["records"]) for r in ok_records)
            logger.info(
                "[StreamD] Published %d symbols (%d bars) to %s/%s",
                len(ok_records), total_bars,
                INTRADAY_EXCHANGE, INTRADAY_PRICE_ROUTING_KEY,
            )
        else:
            logger.warning("[StreamD] No records to publish (all failed)")

        if errors:
            logger.warning("[StreamD] %d symbols failed: %s", len(errors), errors[:5])

        if run_id:
            status = "success" if not errors else ("partial" if ok_records else "failed")
            run_repo.finish_run(run_id, status, errors)

    except Exception as exc:
        logger.error("[StreamD] _run_once error: %s: %s", type(exc).__name__, exc)
        if run_id:
            try:
                run_repo.finish_run(run_id, "failed", [str(exc)])
            except Exception:
                pass
