"""
Seed script for initializing VN30 stock data.

Run: python -m app.scripts.seed
Flags:
    --dry-run   Validate data sources without writing to database
    --prices    Seed price data only
    --wiki      Seed initial wikis only
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date, timedelta
from typing import Any

import httpx
import psycopg2
import psycopg2.extras

from app.config import settings
from app.synthesis.synthesis_agent import SynthesisAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

VN30_SYMBOLS = [
    "VHM", "VND", "VPB", "VCB", "BID", "CTG", "GAS", "GVR",
    "HDB", "HPG", "MBB", "MSN", "MWG", "NLG", "PDR", "PLX",
    "PNC", "POW", "SAB", "SHB", "SSB", "SSI", "STB", "TCB",
    "TPB", "VCA", "VCI", "VGC", "VIB", "VIC", "VJC", "VNM",
    "VRE",
]

PRICE_DAYS = 30
PRICE_RETRY_DAYS = 7


def _get_connection():
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )


def _seed_prices(symbols: list[str], dry_run: bool = False) -> dict[str, int]:
    try:
        import vnstock
    except ImportError:
        logger.error("[Seed] vnstock not installed — price seeding skipped")
        return {}

    seeded: dict[str, int] = {}
    today = date.today()
    end_date = today.isoformat()
    start_date = (today - timedelta(days=PRICE_DAYS + PRICE_RETRY_DAYS)).isoformat()

    for symbol in symbols:
        try:
            df = vnstock.stock.price_historical(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            rows = df.tail(PRICE_DAYS)

            if rows.empty:
                logger.warning("[Seed] No price data for %s — skipping", symbol)
                seeded[symbol] = 0
                continue

            rows_list = rows.rename(columns=lambda c: c.lower()).to_dict("records")
            count = _upsert_prices(symbol, rows_list, dry_run)
            seeded[symbol] = count
            logger.info("[Seed] Seeded %d price rows for %s", count, symbol)

        except Exception as exc:
            logger.error("[Seed] Failed to seed prices for %s: %s", symbol, exc)
            seeded[symbol] = 0

    return seeded


def _upsert_prices(symbol: str, rows: list[dict[str, Any]], dry_run: bool) -> int:
    if not rows:
        return 0

    count = 0
    if dry_run:
        return len(rows)

    conn = _get_connection()
    cur = conn.cursor()
    try:
        for row in rows:
            trade_date = row.get("date") or row.get("trade_date") or row.get(" TradingDate")
            close = row.get("close") or row.get("Close") or row.get("close_price")
            open_price = row.get("open") or row.get("Open") or row.get("open_price")
            high = row.get("high") or row.get("High") or row.get("high_price")
            low = row.get("low") or row.get("Low") or row.get("low_price")
            volume = row.get("volume") or row.get("Volume") or 0

            if not trade_date or not close:
                continue

            if dry_run:
                count += 1
                continue

            cur.execute("""
                INSERT INTO stock_prices (symbol, trade_date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, trade_date) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
            """, (symbol, trade_date, open_price, high, low, close, volume))
            count += 1

        if not dry_run:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("[Seed] DB error upserting prices for %s: %s", symbol, e)
        raise
    finally:
        cur.close()
        conn.close()

    return count


def _seed_news_sources(dry_run: bool = False) -> int:
    if dry_run:
        logger.info("[Seed] [dry-run] Would seed news_sources")
        return 3

    conn = _get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO news_sources (id, name, base_url, crawler_type, is_active)
            VALUES
                ('00000000-0000-0000-0000-000000000001', 'CafeF', 'https://cafef.vn', 'cafef', true),
                ('00000000-0000-0000-0000-000000000002', 'Vietstock', 'https://vietstock.vn', 'vietstock', true),
                ('00000000-0000-0000-0000-000000000003', 'Reuters VN', 'https://www.reuters.com/world/asia-pacific', 'reuters_vn', true)
            ON CONFLICT (name) DO NOTHING
        """)
        conn.commit()
        affected = cur.rowcount
        logger.info("[Seed] Seeded news_sources (%d rows)", affected)
        return affected
    finally:
        cur.close()
        conn.close()


async def _seed_wikis(symbols: list[str], dry_run: bool = False) -> dict[str, bool]:
    results: dict[str, bool] = {}

    for symbol in symbols:
        try:
            if dry_run:
                logger.info("[Seed] [dry-run] Would synthesize wiki for %s", symbol)
                results[symbol] = True
                continue

            logger.info("[Seed] Synthesizing initial wiki for %s...", symbol)
            agent = SynthesisAgent()
            await agent.synthesize([symbol])
            results[symbol] = True
            logger.info("[Seed] Wiki seeded for %s", symbol)

        except Exception as exc:
            logger.error("[Seed] Failed to seed wiki for %s: %s", symbol, exc)
            results[symbol] = False

    return results


def _seed_financial_ratios(symbols: list[str], dry_run: bool = False) -> dict[str, bool]:
    import httpx

    results: dict[str, bool] = {}
    FMP_BASE = "https://financialmodelingprep.com/stable"

    for symbol in symbols:
        try:
            if not settings.FMP_API_KEY or settings.FMP_API_KEY.startswith("your-"):
                logger.warning("[Seed] FMP_API_KEY not configured — skipping ratios")
                break

            resp = httpx.get(
                f"{FMP_BASE}/ratios-ttm",
                params={"symbol": symbol, "apikey": settings.FMP_API_KEY},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or not data:
                logger.warning("[Seed] No ratio data for %s", symbol)
                results[symbol] = False
                continue

            ratios = data[0]
            pe = _safe_float(ratios.get("priceToEarningsRatioTTM"))
            pb = _safe_float(ratios.get("priceToBookRatioTTM"))
            eps = _safe_float(ratios.get("epsTTM"))
            roe = _safe_float(ratios.get("returnOnEquityTTM"))
            roa = _safe_float(ratios.get("returnOnAssetsTTM"))

            if dry_run:
                results[symbol] = True
                continue

            conn = _get_connection()
            cur = conn.cursor()
            try:
                cur.execute("""
                    INSERT INTO financial_ratios (symbol, period, pe_ratio, pb_ratio, eps, roe, roa)
                    VALUES (%s, 'ttm', %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, period) DO UPDATE SET
                        pe_ratio = EXCLUDED.pe_ratio,
                        pb_ratio = EXCLUDED.pb_ratio,
                        eps = EXCLUDED.eps,
                        roe = EXCLUDED.roe,
                        roa = EXCLUDED.roa
                """, (symbol, pe, pb, eps, roe, roa))
                conn.commit()
                results[symbol] = True
                logger.info("[Seed] Seeded ratios for %s", symbol)
            finally:
                cur.close()
                conn.close()

        except Exception as exc:
            logger.error("[Seed] Failed to seed ratios for %s: %s", symbol, exc)
            results[symbol] = False

    return results


def _safe_float(value: Any) -> float | None:
    if value is None or value == "None" or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_db_connection() -> bool:
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error("[Seed] Cannot connect to database: %s", e)
        return False


async def _run(symbols: list[str], seed_prices: bool, seed_wiki: bool, seed_ratios: bool, dry_run: bool):
    if dry_run:
        logger.info("=== DRY RUN MODE — no data will be written ===")

    if not _validate_db_connection():
        sys.exit(1)

    logger.info("=== Seeding %d symbols: %s ===", len(symbols), symbols)

    if seed_prices:
        logger.info("--- Seeding price data (%d days) ---", PRICE_DAYS)
        seeded_prices = _seed_prices(symbols, dry_run)
        total_price_rows = sum(seeded_prices.values())
        logger.info("--- Price seeding done: %d total rows ---", total_price_rows)

    if seed_ratios:
        logger.info("--- Seeding financial ratios ---")
        results = _seed_financial_ratios(symbols, dry_run)
        success = sum(1 for v in results.values() if v)
        logger.info("--- Ratios seeding: %d/%d succeeded ---", success, len(results))

    if seed_wiki:
        logger.info("--- Synthesizing initial wikis (LLM call per symbol) ---")
        logger.info("--- This will make %d LLM requests ---", len(symbols))
        wiki_results = await _seed_wikis(symbols, dry_run)
        success = sum(1 for v in wiki_results.values() if v)
        logger.info("--- Wiki seeding: %d/%d succeeded ---", success, len(wiki_results))

    logger.info("=== Seed complete ===")


def main():
    parser = argparse.ArgumentParser(description="Seed VN30 data into the database")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing to DB")
    parser.add_argument("--prices", action="store_true", help="Seed price data only")
    parser.add_argument("--wiki", action="store_true", help="Seed initial wikis only")
    parser.add_argument("--ratios", action="store_true", help="Seed financial ratios only")
    parser.add_argument(
        "--symbols",
        type=str,
        default="",
        help="Comma-separated symbol list (overrides default VN30)",
    )
    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        symbols = VN30_SYMBOLS

    seed_prices = not (args.wiki or args.ratios)
    seed_wiki = not (args.prices or args.ratios)
    seed_ratios = args.ratios

    asyncio.run(_run(symbols, seed_prices, seed_wiki, seed_ratios, args.dry_run))


if __name__ == "__main__":
    main()
