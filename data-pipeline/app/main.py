import logging

from fastapi import FastAPI

from app.api.routes import router, set_scheduler

logger = logging.getLogger(__name__)

app = FastAPI(title="StockWise Data Pipeline")
app.include_router(router)

_scheduler = None


@app.on_event("startup")
def startup() -> None:
    global _scheduler
    try:
        from app.scheduler import start_scheduler

        _scheduler = start_scheduler()
        set_scheduler(_scheduler)
        logger.info("Data pipeline scheduler started")
    except Exception:
        logger.exception("Data pipeline scheduler failed to start; API remains available")
        _scheduler = None
        set_scheduler(None)


@app.on_event("shutdown")
def shutdown() -> None:
    if _scheduler is not None:
        _scheduler.shutdown()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
