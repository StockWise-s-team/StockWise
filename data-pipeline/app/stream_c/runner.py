"""
stream_c / runner.py
====================
Real-time price feed runner.

Chiến lược fetch (primary → fallback):
  1. PriceBoardFetcher (vnstock KBS) — real-time snapshot, batch 40 symbols
     - Ưu: real-time thật sự trong giờ giao dịch
     - Nhược: bị rate limit nếu gọi quá nhiều
  2. YahooFinancePriceFetcher (fallback) — khi vnstock rate limit
     - Ưu: không bị limit, 1 request cho toàn bộ batch
     - Nhược: delay ~15 phút (Yahoo cache), không có giá trần/sàn

Vòng lặp:
  - Gọi xong → chờ POLL_INTERVAL_SECONDS → gọi lại (không overlap)
  - Chỉ chạy trong giờ giao dịch VN (09:00–15:15 ICT)
  - Ngoài giờ nghỉ IDLE_INTERVAL_SECONDS rồi kiểm tra lại
"""

import asyncio
import logging
from datetime import datetime, timezone, time as dt_time
from typing import Any, Dict, List

from app.rabbitmq.producer import RabbitMQProducer
from app.stream_a.repositories.price_repository import PriceRepository
from app.stream_c.fetcher import PriceBoardFetcher
from app.stream_c.yf_fetcher import YahooFinancePriceFetcher
from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository

logger = logging.getLogger(__name__)

# ── Cấu hình ──────────────────────────────────────────────────────────────────
POLL_INTERVAL_SECONDS = 30      # nghỉ 30s sau mỗi lần fetch thành công
IDLE_INTERVAL_SECONDS = 60      # nghỉ 60s khi ngoài giờ giao dịch

# Rate limit fallback: nếu vnstock thất bại >= N symbol → dùng yfinance luôn
RATE_LIMIT_THRESHOLD = 0.5      # > 50% symbols lỗi → coi là rate limit

# Giờ giao dịch VN (UTC): HOSE 09:00–15:15 ICT = 02:00–08:15 UTC
MARKET_OPEN_UTC  = dt_time(2, 0)
MARKET_CLOSE_UTC = dt_time(8, 15)

_EXCHANGE_PRICE = "market.exchange"
_ROUTING_PRICE  = "price.updated"

# Rate-limit keywords để nhận diện lỗi vnstock
_RATE_LIMIT_HINTS = ("rate limit", "gioi han api", "request limit", "too many", "429")


def _is_market_open() -> bool:
    """True nếu đang trong giờ giao dịch VN."""
    now_utc = datetime.now(timezone.utc).time()
    return MARKET_OPEN_UTC <= now_utc <= MARKET_CLOSE_UTC


def _is_rate_limit_error(records: List[Dict[str, Any]], total: int) -> bool:
    """
    Heuristic: nếu > RATE_LIMIT_THRESHOLD phần trăm symbols trả về lỗi
    có chứa rate-limit keywords thì coi là bị rate limit.
    """
    if not records or total == 0:
        return False
    err_records = [
        r for r in records
        if "error" in r and any(h in str(r["error"]).lower() for h in _RATE_LIMIT_HINTS)
    ]
    return len(err_records) / total >= RATE_LIMIT_THRESHOLD


async def run_stream_c_loop() -> None:
    """
    Vòng lặp bất tận của stream_c.
    Được gọi từ scheduler.py qua thread riêng.
    """
    producer = RabbitMQProducer()
    price_repo = PriceRepository()
    primary_fetcher = PriceBoardFetcher()
    fallback_fetcher = YahooFinancePriceFetcher()

    logger.info(
        "[StreamC] Real-time price loop started — primary=vnstock, fallback=yfinance, poll=%ds",
        POLL_INTERVAL_SECONDS,
    )

    await producer.connect()

    try:
        while True:
            if not _is_market_open():
                logger.debug("[StreamC] Outside market hours — sleeping %ds", IDLE_INTERVAL_SECONDS)
                await asyncio.sleep(IDLE_INTERVAL_SECONDS)
                continue

            await _run_once(price_repo, primary_fetcher, fallback_fetcher, producer)
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    except asyncio.CancelledError:
        logger.info("[StreamC] Loop cancelled, shutting down")
    except Exception as exc:
        logger.error("[StreamC] Unexpected error in loop: %s: %s", type(exc).__name__, exc)
        raise
    finally:
        close_coro = producer.close()
        if asyncio.iscoroutine(close_coro):
            await close_coro


async def _run_once(
    price_repo: PriceRepository,
    primary_fetcher: PriceBoardFetcher,
    fallback_fetcher: YahooFinancePriceFetcher,
    producer: RabbitMQProducer,
) -> None:
    """Một lần fetch + publish. Lỗi được log nhưng không raise để loop tiếp tục."""
    run_repo = PipelineRunsRepository()
    run_id = None

    try:
        run_id = run_repo.create_run(
            run_type="stream_c",
            trigger_type="continuous",
        )
    except Exception as e:
        logger.warning("[StreamC] Cannot create run record: %s", e)

    try:
        tracked = price_repo.get_tracked_symbols()
        if not tracked:
            logger.warning("[StreamC] No tracked symbols, skipping")
            if run_id:
                run_repo.finish_run(run_id, "success", [])
            return

        # ── Bước 1: Thử primary (vnstock price_board) ──────────────────────────
        logger.info("[StreamC] Fetching via vnstock (primary) for %d symbols", len(tracked))
        records = await primary_fetcher.fetch(tracked)
        source_used = "vnstock_price_board"

        # ── Bước 2: Fallback sang yfinance nếu rate limit ──────────────────────
        if _is_rate_limit_error(records, len(tracked)):
            logger.warning(
                "[StreamC] vnstock rate limit detected (>%.0f%% errors) — falling back to yfinance",
                RATE_LIMIT_THRESHOLD * 100,
            )
            try:
                records = await fallback_fetcher.fetch(tracked)
                source_used = "yahoo_finance_price"
                logger.info("[StreamC] yfinance fallback fetched %d records", len(records))
            except Exception as fb_exc:
                logger.error("[StreamC] yfinance fallback also failed: %s", fb_exc)
                # Giữ records từ vnstock (dù bị lỗi nhiều)

        # ── Bước 3: Phân loại kết quả ──────────────────────────────────────────
        ok_records = []
        errors = []

        for rec in records:
            sym = rec.get("symbol", "?")
            if "error" in rec:
                err_msg = rec["error"]
                errors.append(f"{sym}: {err_msg}")
                logger.warning("[StreamC] Symbol %s error: %s", sym, err_msg)
                if run_id:
                    run_repo.add_symbol_result(run_id, sym, "error", err_msg)
            else:
                ok_records.append(rec)
                if run_id:
                    run_repo.add_symbol_result(run_id, sym, "success")

        # ── Bước 4: Publish lên RabbitMQ ───────────────────────────────────────
        if ok_records:
            await producer.publish(
                exchange_name=_EXCHANGE_PRICE,
                routing_key=_ROUTING_PRICE,
                data={
                    "symbols":      [r["symbol"] for r in ok_records],
                    "prices":       ok_records,
                    "source":       source_used,
                    "timestamp":    _now_iso(),
                    "record_count": len(ok_records),
                    "action":       _ROUTING_PRICE,
                },
            )
            logger.info(
                "[StreamC] Published %d/%d symbols via %s to %s/%s",
                len(ok_records), len(tracked), source_used,
                _EXCHANGE_PRICE, _ROUTING_PRICE,
            )
        else:
            logger.warning("[StreamC] No records to publish (all failed)")

        if errors:
            logger.warning("[StreamC] %d symbols failed: %s", len(errors), errors[:5])

        if run_id:
            status = "success" if not errors else ("partial" if ok_records else "failed")
            run_repo.finish_run(run_id, status, errors)

    except Exception as exc:
        logger.error("[StreamC] _run_once error: %s: %s", type(exc).__name__, exc)
        if run_id:
            try:
                run_repo.finish_run(run_id, "failed", [str(exc)])
            except Exception:
                pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
