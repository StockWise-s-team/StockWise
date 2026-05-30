import logging
from datetime import date, timedelta
from typing import List

import psycopg2
import psycopg2.extras
import vnstock
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.api.schemas import (
    CompanyWikiResponse,
    NewsSourceResponse,
    NewsSourceToggle,
    PipelineStatus,
    SeedRequest,
    SeedResponse,
    SynthesisRequest,
    SynthesisResponse,
    TrackedSymbolAdd,
)
from app.config import settings
from app.scripts.seed import VN30_SYMBOLS
from app.sources.source_repository import SourceRepository
from app.synthesis.synthesis_agent import SynthesisAgent
from app.synthesis.wiki_repository import WikiRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["pipeline"])

_scheduler_ref: "BackgroundScheduler | None" = None  # injected from main.py


def set_scheduler(scheduler) -> None:
    global _scheduler_ref
    _scheduler_ref = scheduler


def _get_conn():
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )


# ── News Sources ────────────────────────────────────────────────────────────────

@router.get("/news-sources", response_model=List[NewsSourceResponse])
def list_news_sources():
    repo = SourceRepository()
    sources = repo.get_active_sources()
    return [NewsSourceResponse(**s.__dict__) for s in sources]


@router.patch("/news-sources/{source_id}", response_model=NewsSourceResponse)
def toggle_source(source_id: str, body: NewsSourceToggle):
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            "UPDATE news_sources SET is_active = %s WHERE id = %s RETURNING *",
            (body.is_active, source_id),
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            raise HTTPException(status_code=404, detail="Source not found")
        SourceRepository().invalidate()
        return NewsSourceResponse(
            id=row["id"],
            name=row["name"],
            base_url=row["base_url"],
            crawler_type=row["crawler_type"],
            is_active=row["is_active"],
        )
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# ── Tracked Symbols ────────────────────────────────────────────────────────────

@router.get("/tracked-symbols", response_model=List[str])
def list_tracked_symbols():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT symbol FROM stock_prices ORDER BY symbol")
        rows = cur.fetchall()
        return [r[0] for r in rows]
    finally:
        cur.close()
        conn.close()


@router.post("/tracked-symbols", response_model=dict, status_code=201)
def add_tracked_symbol(body: TrackedSymbolAdd):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO tracked_symbols (symbol) VALUES (%s) ON CONFLICT DO NOTHING",
            (body.symbol,),
        )
        conn.commit()
        return {"symbol": body.symbol}
    finally:
        cur.close()
        conn.close()


@router.delete("/tracked-symbols/{symbol}", status_code=204)
def remove_tracked_symbol(symbol: str):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM tracked_symbols WHERE symbol = %s", (symbol,)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ── Company Wiki ────────────────────────────────────────────────────────────────

@router.get("/company-wiki", response_model=List[CompanyWikiResponse])
def list_wikis():
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT symbol, wiki_data, version, updated_at
            FROM company_wiki
            ORDER BY updated_at DESC NULLS LAST
        """)
        rows = cur.fetchall()
        results = []
        for row in rows:
            data = dict(row["wiki_data"]) if row["wiki_data"] else {}
            results.append(CompanyWikiResponse(
                symbol=row["symbol"],
                company_name=data.get("company_name"),
                sector=data.get("sector"),
                business_summary=data.get("business_summary"),
                recent_performance=data.get("recent_performance"),
                key_risks=data.get("key_risks"),
                sentiment=data.get("sentiment"),
                last_news_summary=data.get("last_news_summary"),
                financials_snapshot=data.get("financials_snapshot"),
                version=row["version"],
                updated_at=row["updated_at"],
            ))
        return results
    finally:
        cur.close()
        conn.close()


@router.get("/company-wiki/{symbol}", response_model=CompanyWikiResponse)
def get_wiki(symbol: str):
    repo = WikiRepository()
    wiki = repo.get_wiki(symbol)
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found")
    return CompanyWikiResponse(**wiki)


# ── Seed ───────────────────────────────────────────────────────────────────────

@router.post("/scripts/seed", response_model=SeedResponse)
def trigger_seed(body: SeedRequest, background_tasks: BackgroundTasks):
    errors: List[str] = []

    def _run():
        _seed_sync(body, errors)

    background_tasks.add_task(_run)
    return SeedResponse(
        status="started",
        symbols_seeded=0,
        price_rows=0,
        wiki_rows=0,
        errors=[],
    )


def _seed_sync(body: SeedRequest, errors: List[str]) -> None:
    import time
    from app.scripts.seed import _get_connection, _upsert_prices, PRICE_DAYS

    vnstock.config.API_KEY = settings.VNSTOCK_API_KEY or ""
    symbols = body.symbols or VN30_SYMBOLS

    if body.prices_only or (not body.prices_only and not body.wiki_only):
        today = date.today()
        end_date = today.isoformat()
        start_date = (today - timedelta(days=PRICE_DAYS + 7)).isoformat()

        batch_size = 18
        for batch_start in range(0, len(symbols), batch_size):
            batch = symbols[batch_start : batch_start + batch_size]
            if batch_start > 0:
                logger.info("[API/seed] Rate limit pause — sleeping 65s...")
                time.sleep(65)

            for symbol in batch:
                success = False
                for attempt in range(3):
                    try:
                        q = vnstock.Quote(source="kbs", symbol=symbol)
                        df = q.ohlcv(start=start_date, end=end_date)
                        rows = df.tail(PRICE_DAYS)
                        if rows.empty:
                            errors.append(f"{symbol}: no price data")
                            success = True
                            break
                        rows_list = rows.rename(columns=lambda c: c.lower()).to_dict("records")
                        for r in rows_list:
                            r["time"] = r.get("time")
                        _upsert_prices(symbol, rows_list, body.dry_run)
                        logger.info("[API/seed] Seeded prices for %s", symbol)
                        time.sleep(3)
                        success = True
                        break
                    except (SystemExit, Exception) as e:
                        err_str = str(e)
                        if "Rate limit" in err_str or "giới hạn" in err_str or "quota" in err_str.lower():
                            wait = 60 * (attempt + 1)
                            logger.warning("[API/seed] Rate limited for %s, waiting %ds (attempt %d)", symbol, wait, attempt + 1)
                            time.sleep(wait)
                        else:
                            errors.append(f"{symbol}: {e}")
                            logger.error("[API/seed] Failed for %s: %s", symbol, e)
                            break
                if not success and not any(symbol in e for e in errors):
                    errors.append(f"{symbol}: max retries exceeded")

    if body.wiki_only or (not body.prices_only and not body.wiki_only):
        import asyncio
        agent = SynthesisAgent()
        for symbol in symbols:
            try:
                asyncio.run(agent.synthesize([symbol]))
                logger.info("[API/seed] Seeded wiki for %s", symbol)
            except Exception as e:
                errors.append(f"{symbol}/wiki: {e}")
                logger.error("[API/seed] Failed wiki for %s: %s", symbol, e)


# ── Synthesis ─────────────────────────────────────────────────────────────────

@router.post("/synthesis/trigger", response_model=SynthesisResponse)
def trigger_synthesis(body: SynthesisRequest, background_tasks: BackgroundTasks):
    errors: List[str] = []

    def _run():
        import asyncio
        symbols = body.symbols or VN30_SYMBOLS
        agent = SynthesisAgent()
        for symbol in symbols:
            try:
                asyncio.run(agent.synthesize([symbol]))
                logger.info("[API/synthesis] Synthesized %s", symbol)
            except Exception as e:
                errors.append(f"{symbol}: {e}")
                logger.error("[API/synthesis] Failed %s: %s", symbol, e)

    background_tasks.add_task(_run)
    return SynthesisResponse(
        status="started",
        symbols_processed=0,
        errors=[],
    )


# ── Pipeline Status ────────────────────────────────────────────────────────────

@router.get("/pipeline/status", response_model=PipelineStatus)
def pipeline_status():
    sched = _scheduler_ref
    if sched is None:
        raise HTTPException(status_code=503, detail="Scheduler not available")

    jobs = {j.id: j for j in sched.get_jobs()}
    fmt = "%Y-%m-%dT%H:%M:%S"

    def next_dt(job_id: str):
        j = jobs.get(job_id)
        if j and j.next_run_time:
            return j.next_run_time.strftime(fmt)
        return None

    return PipelineStatus(
        scheduler_running=sched.running,
        stream_a={"last_run": None, "status": "idle", "symbols_processed": 0},
        stream_b={"last_run": None, "status": "idle", "articles_ingested": 0},
        synthesis={"last_run": None, "status": "idle", "wikis_updated": 0},
        next_stream_a=next_dt("stream_a"),
        next_stream_b=next_dt("stream_b"),
        next_synthesis=next_dt("synthesis"),
    )
