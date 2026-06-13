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
    PipelineProgress,
    PipelineRunResponse,
    PipelineRunDetailResponse,
    PipelineRunSymbolResponse,
    PipelineStatsResponse,
    PipelineStatus,
    SeedRequest,
    SeedResponse,
    SynthesisRequest,
    SynthesisResponse,
    TrackedSymbolAdd,
    progress_store,
)
from app.config import settings
from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository
from app.config import settings as _cfg
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
    import json
    from datetime import datetime
    _log_path = "d:/StockWise/debug-07e1c9.log"
    _log_id = f"log_{int(datetime.now().timestamp()*1000)}"
    try:
        with open(_log_path, "a") as _f:
            _f.write(json.dumps({
                "id": _log_id, "timestamp": int(datetime.now().timestamp()*1000),
                "location": "routes.py:list_news_sources:entry",
                "message": "GET /news-sources entry",
                "runId": "hypothesis-test", "hypothesisId": "H1+H2+H3",
                "data": {}
            }) + "\n")
    except: pass
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT id, name, base_url, crawler_type, is_active FROM news_sources ORDER BY name")
        rows = cur.fetchall()
        sources = [NewsSourceResponse(
            id=str(row["id"]), name=row["name"],
            base_url=row["base_url"], crawler_type=row["crawler_type"],
            is_active=row["is_active"]
        ) for row in rows]
        _src_ids = [str(row["id"]) for row in rows]
        _src_count = len(sources)
        try:
            with open(_log_path, "a") as _f:
                _f.write(json.dumps({
                    "id": f"{_log_id}_exit", "timestamp": int(datetime.now().timestamp()*1000),
                    "location": "routes.py:list_news_sources:exit",
                    "message": f"GET /news-sources returning {_src_count} sources (ALL)",
                    "runId": "hypothesis-test", "hypothesisId": "H1+H2+H3",
                    "data": {"source_count": _src_count, "source_ids": _src_ids}
                }) + "\n")
        except: pass
        return sources
    finally:
        cur.close()
        conn.close()


@router.patch("/news-sources/{source_id}", response_model=NewsSourceResponse)
def toggle_source(source_id: str, body: NewsSourceToggle):
    import json
    from datetime import datetime
    _log_path = "d:/StockWise/debug-07e1c9.log"
    _log_id = f"log_{int(datetime.now().timestamp()*1000)}"
    _entry_ts = int(datetime.now().timestamp()*1000)

    def _w(loc, msg, hid, extra=None):
        try:
            d = {"id": f"{_log_id}_{loc}", "timestamp": int(datetime.now().timestamp()*1000),
                 "location": f"routes.py:toggle_source:{loc}", "message": msg,
                 "runId": "hypothesis-test", "hypothesisId": hid}
            if extra:
                d["data"] = extra
            with open(_log_path, "a") as _f:
                _f.write(json.dumps(d) + "\n")
        except: pass

    _w("entry", "PATCH toggle_source entry", "H1+H2+H3",
       {"source_id": source_id, "body_isActive": body.isActive})

    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute(
            "UPDATE news_sources SET is_active = %s WHERE id = %s RETURNING *",
            (body.isActive, source_id),
        )
        row = cur.fetchone()
        _w("after_update", "After UPDATE, row fetched", "H1+H2",
           {"row": dict(row) if row else None, "source_id": source_id, "is_active": body.isActive})
        conn.commit()
        if not row:
            _w("not_found", "Source not found in DB", "H1",
               {"source_id": source_id})
            raise HTTPException(status_code=404, detail="Source not found")
        SourceRepository().invalidate()
        _w("before_response", "Returning NewsSourceResponse", "H2",
           {"id": str(row["id"]), "name": row["name"], "is_active": row["is_active"]})
        return NewsSourceResponse(
            id=str(row["id"]),
            name=row["name"],
            base_url=row["base_url"],
            crawler_type=row["crawler_type"],
            is_active=row["is_active"],
        )
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        _w("exception", f"PATCH exception: {type(e).__name__}: {e}", "H1+H2+H3",
           {"source_id": source_id, "isActive": body.isActive})
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
        _w("finally", "toggle_source cleanup done", "H1+H2+H3", {})


# ── Tracked Symbols ────────────────────────────────────────────────────────────

@router.get("/tracked-symbols", response_model=List[str])
def list_tracked_symbols():
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT symbol FROM tracked_symbols ORDER BY symbol")
        rows = cur.fetchall()
        return [r[0] for r in rows]
    finally:
        cur.close()
        conn.close()


@router.post("/tracked-symbols", response_model=dict, status_code=201)
def add_tracked_symbol(body: TrackedSymbolAdd, background_tasks: BackgroundTasks):
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO tracked_symbols (symbol) VALUES (%s) ON CONFLICT DO NOTHING",
            (body.symbol,),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    async def _run():
        from app.synthesis.synthesis_agent import SynthesisAgent
        from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository
        from app.scripts.seed import (
            _seed_company_info,
            _seed_financial_ratios,
            _seed_prices,
        )

        run_repo = PipelineRunsRepository()
        run_id = None
        symbol = body.symbol
        try:
            run_id = run_repo.create_run(
                run_type="synthesis",
                trigger_type="tracked_symbol",
                symbols_requested=1,
            )
        except Exception as e:
            logger.error("[API/tracked-symbols] Failed to create run record: %s", e)

        # ── Auto-seed company info, ratios, and prices for new symbol ──
        try:
            logger.info("[API/tracked-symbols] Auto-seeding company info for %s", symbol)
            _seed_company_info([symbol])
        except Exception as e:
            logger.warning("[API/tracked-symbols] Company info seed failed for %s: %s", symbol, e)

        try:
            logger.info("[API/tracked-symbols] Auto-seeding financial ratios for %s", symbol)
            _seed_financial_ratios([symbol])
        except Exception as e:
            logger.warning("[API/tracked-symbols] Financial ratios seed failed for %s: %s", symbol, e)

        try:
            logger.info("[API/tracked-symbols] Auto-seeding price data for %s", symbol)
            _seed_prices([symbol])
        except Exception as e:
            logger.warning("[API/tracked-symbols] Price seed failed for %s: %s", symbol, e)

        # ── Now run synthesis with the freshly seeded data ──
        agent = SynthesisAgent()
        try:
            await agent.synthesize([symbol])
            logger.info("[API/tracked-symbols] Synthesis done for %s", symbol)
            if run_id:
                run_repo.add_symbol_result(run_id, symbol, "success")
        except Exception as e:
            logger.error("[API/tracked-symbols] Synthesis failed for %s: %s", symbol, e)
            if run_id:
                run_repo.add_symbol_result(run_id, symbol, "error", str(e))
        finally:
            if run_id:
                run_repo.finish_run(run_id, "success")

    background_tasks.add_task(_run)
    return {"symbol": body.symbol}


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

@router.get("/company-wiki")
def list_wikis(limit: int = 50, offset: int = 0, search: str = ""):
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        search_pattern = f"%{search}%" if search else None

        if search_pattern:
            cur.execute(
                "SELECT COUNT(*) FROM company_wiki WHERE symbol ILIKE %s OR wiki_data->>'company_name' ILIKE %s",
                (search_pattern, search_pattern),
            )
            total = int(cur.fetchone()["count"])

            cur.execute("""
                SELECT symbol, wiki_data, version, updated_at
                FROM company_wiki
                WHERE symbol ILIKE %s OR wiki_data->>'company_name' ILIKE %s
                ORDER BY updated_at DESC NULLS LAST
                LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, limit, offset))
        else:
            cur.execute("SELECT COUNT(*) FROM company_wiki")
            total = int(cur.fetchone()["count"])

            cur.execute("""
                SELECT symbol, wiki_data, version, updated_at
                FROM company_wiki
                ORDER BY updated_at DESC NULLS LAST
                LIMIT %s OFFSET %s
            """, (limit, offset))
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
        return {"wikis": results, "total": total, "limit": limit, "offset": offset}
    finally:
        cur.close()
        conn.close()


@router.get("/company-wiki/{symbol}", response_model=CompanyWikiResponse, response_model_by_alias=False)
def get_wiki(symbol: str):
    repo = WikiRepository()
    wiki = repo.get_wiki(symbol)
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found")
    return CompanyWikiResponse(**wiki)


# ── Seed ───────────────────────────────────────────────────────────────────────

@router.post("/scripts/seed", response_model=SeedResponse)
def trigger_seed(body: SeedRequest, background_tasks: BackgroundTasks):
    from app.stream_a.repositories.price_repository import PriceRepository
    if body.symbols is None:
        price_repo = PriceRepository()
        symbols = price_repo.get_tracked_symbols()
        if not symbols:
            symbols = _cfg.get_vn30_symbols()
    else:
        symbols = body.symbols
    progress_store.reset_seed(len(symbols))

    def _run():
        _seed_sync(body, progress_store)

    background_tasks.add_task(_run)
    return SeedResponse(
        status="started",
        symbols_seeded=0,
        price_rows=0,
        wiki_rows=0,
        errors=[],
    )


def _seed_sync(body: SeedRequest, progress) -> None:
    import time
    from app.scripts.seed import (
        _get_connection,
        _upsert_prices,
        _seed_company_info,
        _seed_financial_ratios,
        PRICE_DAYS,
    )
    from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository

    run_repo = PipelineRunsRepository()
    run_id = None

    symbols = body.symbols if body.symbols is not None else _cfg.get_vn30_symbols()

    try:
        run_id = run_repo.create_run(
            run_type="seed",
            trigger_type="api",
            symbols_requested=len(symbols),
        )
    except Exception as e:
        logger.error("[API/seed] Failed to create DB run record: %s", e)
        run_id = None

    vnstock.config.API_KEY = settings.VNSTOCK_API_KEY or ""

    processed = 0
    all_errors = []

    def _do_prices():
        nonlocal processed, all_errors
        today = date.today()
        end_date = today.isoformat()
        start_date = (today - timedelta(days=PRICE_DAYS + 7)).isoformat()

        batch_size = 18
        for batch_start in range(0, len(symbols), batch_size):
            batch = symbols[batch_start : batch_start + batch_size]
            if batch_start > 0:
                logger.info("[API/seed] Rate limit pause -- sleeping 65s...")
                progress.seed_progress.message = "Rate limit pause -- sleeping 65s..."
                time.sleep(65)

            for i, symbol in enumerate(batch):
                success = False
                for attempt in range(3):
                    try:
                        q = vnstock.Quote(source="kbs", symbol=symbol)
                        df = q.ohlcv(start=start_date, end=end_date)
                        rows = df.tail(PRICE_DAYS)
                        if rows.empty:
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
                            logger.error("[API/seed] Failed for %s: %s", symbol, e)
                            break
                processed += 1
                progress.step_seed(symbol, processed)
                if success:
                    if run_id:
                        run_repo.add_symbol_result(run_id, symbol, "success")
                else:
                    err_msg = f"{symbol}: failed after retries"
                    all_errors.append(err_msg)
                    if run_id:
                        run_repo.add_symbol_result(run_id, symbol, "error", err_msg)

    def _do_company():
        nonlocal all_errors
        logger.info("[API/seed] Seeding company info for %d symbols", len(symbols))
        try:
            results = _seed_company_info(symbols, dry_run=body.dry_run)
            for sym, ok in results.items():
                if not ok:
                    err_msg = f"{sym}: company info failed"
                    all_errors.append(err_msg)
                    if run_id:
                        run_repo.add_symbol_result(run_id, sym, "error", err_msg)
                elif run_id:
                    run_repo.add_symbol_result(run_id, sym, "success")
        except Exception as e:
            logger.error("[API/seed] Company info seeding failed: %s", e)
            all_errors.append(f"company_info: {e}")

    def _do_ratios():
        nonlocal all_errors
        logger.info("[API/seed] Seeding financial ratios for %d symbols", len(symbols))
        try:
            results = _seed_financial_ratios(symbols, dry_run=body.dry_run)
            for sym, ok in results.items():
                if not ok:
                    err_msg = f"{sym}: ratios failed"
                    all_errors.append(err_msg)
                    if run_id:
                        run_repo.add_symbol_result(run_id, sym, "error", err_msg)
                elif run_id:
                    run_repo.add_symbol_result(run_id, sym, "success")
        except Exception as e:
            logger.error("[API/seed] Ratios seeding failed: %s", e)
            all_errors.append(f"ratios: {e}")

    def _do_wiki():
        nonlocal processed, all_errors
        agent = SynthesisAgent()
        for symbol in symbols:
            try:
                import asyncio
                results = asyncio.run(agent.synthesize([symbol]))
                result = results[0] if results else None
                if result and result.success:
                    logger.info("[API/seed] Seeded wiki for %s", symbol)
                    if body.wiki_only:
                        processed += 1
                        progress.step_seed(symbol, processed)
                    else:
                        progress.seed_progress.currentSymbol = symbol
                        progress.seed_progress.message = f"Processing {symbol} wiki..."
                    if run_id:
                        run_repo.add_symbol_result(run_id, symbol, "success")
                else:
                    err_msg = f"{symbol}/wiki: {result.error if result else 'no synthesis result'}"
                    logger.error("[API/seed] Failed wiki for %s: %s", symbol, err_msg)
                    all_errors.append(err_msg)
                    progress.seed_progress.errors.append(err_msg)
                    if run_id:
                        run_repo.add_symbol_result(run_id, symbol, "error", err_msg)
            except Exception as e:
                logger.error("[API/seed] Failed wiki for %s: %s", symbol, e)
                err_msg = f"{symbol}/wiki: {e}"
                all_errors.append(err_msg)
                progress.seed_progress.errors.append(err_msg)
                if run_id:
                    run_repo.add_symbol_result(run_id, symbol, "error", err_msg)

    try:
        if body.company_only:
            _do_company()
        elif body.ratios_only:
            _do_ratios()
        elif body.prices_only:
            _do_prices()
        elif body.wiki_only:
            _do_wiki()
        else:
            _do_prices()
            _do_company()
            _do_ratios()
            _do_wiki()
    except Exception as e:
        logger.error("[API/seed] Unhandled exception in seed sync: %s", e)
        progress.seed_progress.errors.append(f"Fatal: {e}")
        all_errors.append(f"Fatal: {e}")
    finally:
        if run_id:
            final_status = "success" if not all_errors else "partial"
            run_repo.finish_run(run_id, final_status, all_errors)
        progress.finish_seed(progress.seed_progress.errors)


# ── Synthesis ─────────────────────────────────────────────────────────────────

@router.post("/synthesis/trigger", response_model=SynthesisResponse)
def trigger_synthesis(body: SynthesisRequest, background_tasks: BackgroundTasks):
    from app.stream_a.repositories.price_repository import PriceRepository
    if body.symbols is None:
        price_repo = PriceRepository()
        symbols = price_repo.get_tracked_symbols()
        if not symbols:
            symbols = _cfg.get_vn30_symbols()
    else:
        symbols = body.symbols
    progress_store.reset_synthesis(len(symbols))

    async def _run():
        from app.pipeline_runs.pipeline_runs_repository import PipelineRunsRepository
        run_repo = PipelineRunsRepository()
        run_id = None
        all_errors = []

        try:
            run_id = run_repo.create_run(
                run_type="synthesis",
                trigger_type="api",
                symbols_requested=len(symbols),
            )
        except Exception as e:
            logger.error("[API/synthesis] Failed to create DB run record: %s", e)
            run_id = None

        agent = SynthesisAgent()
        processed = 0
        try:
            for symbol in symbols:
                try:
                    results = await agent.synthesize([symbol])
                    result = results[0] if results else None
                    if result and result.success:
                        logger.info("[API/synthesis] Synthesized %s", symbol)
                        processed += 1
                        progress_store.step_synthesis(symbol, processed)
                        if run_id:
                            run_repo.add_symbol_result(run_id, symbol, "success")
                    else:
                        err_msg = f"{symbol}: {result.error if result else 'no synthesis result'}"
                        logger.error("[API/synthesis] Failed %s: %s", symbol, err_msg)
                        all_errors.append(err_msg)
                        progress_store.synthesis_progress.errors.append(err_msg)
                        if run_id:
                            run_repo.add_symbol_result(run_id, symbol, "error", err_msg)
                except Exception as e:
                    logger.error("[API/synthesis] Failed %s: %s", symbol, e)
                    err_msg = f"{symbol}: {e}"
                    all_errors.append(err_msg)
                    progress_store.synthesis_progress.errors.append(err_msg)
                    if run_id:
                        run_repo.add_symbol_result(run_id, symbol, "error", err_msg)
        except Exception as e:
            logger.error("[API/synthesis] Unhandled exception: %s", e)
            all_errors.append(f"Fatal: {e}")
            progress_store.synthesis_progress.errors.append(f"Fatal: {e}")
        finally:
            if run_id:
                final_status = "success" if not all_errors else "partial"
                run_repo.finish_run(run_id, final_status, all_errors)
            progress_store.finish_synthesis(progress_store.synthesis_progress.errors)

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


# ── SSE Progress Stream ────────────────────────────────────────────────────────

@router.get("/pipeline/progress")
def pipeline_progress():
    """
    Server-Sent Events stream — pushes progress updates for seed/synthesis tasks.
    Each event is a JSON line:  data: {...}\n\n
    """

    async def event_generator():
        import asyncio, json

        pending_tasks = set()

        while True:
            seed = progress_store.seed_progress
            synth = progress_store.synthesis_progress

            for prog in [seed, synth]:
                if prog.phase == "idle":
                    continue
                key = f"{prog.task}:{prog.phase}"
                if key not in pending_tasks:
                    pending_tasks.add(key)
                    dumped = prog.model_dump()
                    yield f"data: {json.dumps(dumped)}\n\n"

            # Only close stream when BOTH tasks have settled (done/error)
            seed_done = seed.phase in ("done", "error")
            synth_done = synth.phase in ("done", "error")

            if pending_tasks and seed_done and synth_done:
                # Send final terminal event for each settled task
                for prog in [seed, synth]:
                    if prog.phase != "idle":
                        dumped = prog.model_dump()
                        yield f"data: {json.dumps(dumped)}\n\n"
                return

            await asyncio.sleep(1.5)

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/pipeline/progress/poll")
def pipeline_progress_poll():
    """Polling fallback — returns current progress state as JSON."""
    def _dump(p):
        d = p.model_dump()
        d["current_symbol"] = d.pop("currentSymbol")
        d["total_symbols"] = d.pop("totalSymbols")
        d["processed_symbols"] = d.pop("processedSymbols")
        return d

    return {
        "seed": _dump(progress_store.seed_progress),
        "synthesis": _dump(progress_store.synthesis_progress),
    }


# ── Pipeline Run History ────────────────────────────────────────────────────────

@router.get("/pipeline/runs")
def list_pipeline_runs(
    run_type: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List recent pipeline execution history with pagination."""
    repo = PipelineRunsRepository()
    return repo.list_runs(run_type=run_type, status=status, limit=limit, offset=offset)


@router.get("/pipeline/runs/stats", response_model=PipelineStatsResponse)
def pipeline_run_stats():
    """Get aggregated statistics from recent runs."""
    repo = PipelineRunsRepository()
    return repo.get_stats()


@router.get("/pipeline/runs/recent", response_model=List[PipelineRunResponse])
def recent_pipeline_runs(limit: int = 10):
    """Get N most recent pipeline runs."""
    repo = PipelineRunsRepository()
    return repo.get_recent_runs(limit=limit)


@router.get("/pipeline/runs/{run_id}", response_model=PipelineRunDetailResponse)
def get_pipeline_run(run_id: str):
    """Get detail of a specific pipeline run, including per-symbol results."""
    repo = PipelineRunsRepository()
    run = repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    return run
