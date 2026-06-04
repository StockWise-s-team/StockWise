import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router, set_scheduler
from app.scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_scheduler_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_instance
    sched = start_scheduler()
    _scheduler_instance = sched
    set_scheduler(sched)
    logger.info("Scheduler started — Stream A, B, Synthesis queued every 4h")
    yield
    logger.info("Shutting down scheduler on FastAPI shutdown...")
    sched.shutdown(wait=True)


app = FastAPI(
    title="StockWise Data Pipeline",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


def main():
    logger.info("Starting StockWise data-pipeline (FastAPI + Scheduler)...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
