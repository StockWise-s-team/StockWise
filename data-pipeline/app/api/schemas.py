from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── SSE Progress ────────────────────────────────────────────────────────────────

class PipelineProgress(BaseModel):
    task: str  # "seed" | "synthesis"
    phase: str  # "idle" | "running" | "done" | "error"
    progress: float = 0.0  # 0.0 – 1.0
    currentSymbol: Optional[str] = Field(default=None, alias="current_symbol")
    totalSymbols: int = Field(default=0, alias="total_symbols")
    processedSymbols: int = Field(default=0, alias="processed_symbols")
    message: str = ""
    errors: List[str] = Field(default_factory=list)


class PipelineProgressStore:
    _instance: "PipelineProgressStore | None" = None

    def __init__(self):
        self.seed_progress = PipelineProgress(task="seed", phase="idle", message="Ready")
        self.synthesis_progress = PipelineProgress(task="synthesis", phase="idle", message="Ready")

    @classmethod
    def get(cls) -> "PipelineProgressStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reset_seed(self, total: int):
        self.seed_progress = PipelineProgress(
            task="seed", phase="running", total_symbols=total,
            progress=0.0, message="Starting seed…"
        )

    def step_seed(self, symbol: str, processed: int):
        self.seed_progress.currentSymbol = symbol
        self.seed_progress.processedSymbols = processed
        self.seed_progress.progress = processed / max(self.seed_progress.totalSymbols, 1)
        self.seed_progress.message = f"Processing {symbol}…"

    def finish_seed(self, errors: List[str]):
        self.seed_progress.phase = "done"
        self.seed_progress.progress = 1.0
        self.seed_progress.message = f"Done — {self.seed_progress.processedSymbols}/{self.seed_progress.totalSymbols} symbols"
        self.seed_progress.errors = errors

    def fail_seed(self, error: str):
        self.seed_progress.phase = "error"
        self.seed_progress.message = f"Failed: {error}"

    def reset_synthesis(self, total: int):
        self.synthesis_progress = PipelineProgress(
            task="synthesis", phase="running", total_symbols=total,
            progress=0.0, message="Starting synthesis…"
        )

    def step_synthesis(self, symbol: str, processed: int):
        self.synthesis_progress.currentSymbol = symbol
        self.synthesis_progress.processedSymbols = processed
        self.synthesis_progress.progress = processed / max(self.synthesis_progress.totalSymbols, 1)
        self.synthesis_progress.message = f"Analyzing {symbol}…"

    def finish_synthesis(self, errors: List[str]):
        self.synthesis_progress.phase = "done"
        self.synthesis_progress.progress = 1.0
        self.synthesis_progress.message = f"Done — {self.synthesis_progress.processedSymbols}/{self.synthesis_progress.totalSymbols} symbols"
        self.synthesis_progress.errors = errors

    def fail_synthesis(self, error: str):
        self.synthesis_progress.phase = "error"
        self.synthesis_progress.message = f"Failed: {error}"


progress_store = PipelineProgressStore.get()


class NewsSourceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    baseUrl: str = Field(alias="base_url")
    crawlerType: str = Field(alias="crawler_type")
    isActive: bool = Field(alias="is_active")


class NewsSourceToggle(BaseModel):
    isActive: bool = Field(alias="is_active")


class TrackedSymbolAdd(BaseModel):
    symbol: str = Field(..., pattern=r"^[A-Z]{3,5}$")


class CompanyWikiResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    companyName: Optional[str] = Field(default=None, alias="company_name")
    sector: Optional[str] = None
    businessSummary: Optional[str] = Field(default=None, alias="business_summary")
    recentPerformance: Optional[Dict[str, Any]] = Field(
        default=None, alias="recent_performance"
    )
    keyRisks: Optional[List[str]] = Field(default=None, alias="key_risks")
    sentiment: Optional[str] = None
    lastNewsSummary: Optional[str] = Field(default=None, alias="last_news_summary")
    financialsSnapshot: Optional[Dict[str, Any]] = Field(
        default=None, alias="financials_snapshot"
    )
    version: int
    updatedAt: Optional[datetime] = Field(default=None, alias="updated_at")


class SeedRequest(BaseModel):
    symbols: Optional[List[str]] = None
    prices_only: bool = False
    wiki_only: bool = False
    company_only: bool = False
    ratios_only: bool = False
    dry_run: bool = False


class SeedResponse(BaseModel):
    status: str
    symbols_seeded: int
    price_rows: int
    wiki_rows: int
    errors: List[str]


class SynthesisRequest(BaseModel):
    symbols: Optional[List[str]] = None


class SynthesisResponse(BaseModel):
    status: str
    symbols_processed: int
    errors: List[str]


class PipelineStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schedulerRunning: bool = Field(alias="scheduler_running")
    streamA: "StreamStatus" = Field(alias="stream_a")
    streamB: "StreamBStatus" = Field(alias="stream_b")
    synthesis: "SynthesisStatus" = Field(alias="synthesis")
    nextStreamA: Optional[str] = Field(default=None, alias="next_stream_a")
    nextStreamB: Optional[str] = Field(default=None, alias="next_stream_b")
    nextSynthesis: Optional[str] = Field(default=None, alias="next_synthesis")


class StreamStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lastRun: Optional[str] = Field(default=None, alias="last_run")
    status: str
    symbolsProcessed: int = Field(alias="symbols_processed")


class StreamBStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lastRun: Optional[str] = Field(default=None, alias="last_run")
    status: str
    articlesIngested: int = Field(alias="articles_ingested")


class SynthesisStatus(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lastRun: Optional[str] = Field(default=None, alias="last_run")
    status: str
    wikisUpdated: int = Field(alias="wikis_updated")


# ── Pipeline Run History ────────────────────────────────────────────────────────

class PipelineRunSymbolResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    run_id: str
    symbol: str
    status: str
    error_message: Optional[str] = None
    processed_at: str


class PipelineRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    run_type: str
    trigger_type: str
    status: str
    symbols_requested: Optional[int] = None
    symbols_processed: Optional[int] = None
    errors: List[str] = Field(default_factory=list)
    duration_seconds: Optional[int] = None
    started_at: str
    finished_at: Optional[str] = None
    success_count: int = 0
    error_count: int = 0


class PipelineRunDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    run_type: str
    trigger_type: str
    status: str
    symbols_requested: Optional[int] = None
    symbols_processed: Optional[int] = None
    errors: List[str] = Field(default_factory=list)
    duration_seconds: Optional[int] = None
    started_at: str
    finished_at: Optional[str] = None
    symbols_detail: List[PipelineRunSymbolResponse] = Field(default_factory=list)


class PipelineStatsResponse(BaseModel):
    by_type_status: List[Dict[str, Any]] = Field(default_factory=list)
    summary: List[Dict[str, Any]] = Field(default_factory=list)


# ── RabbitMQ peek ──────────────────────────────────────────────────────────────

class RabbitMessage(BaseModel):
    """Một message lấy được từ RabbitMQ."""
    routing_key: str
    exchange: str
    payload: Dict[str, Any]
    payload_size_bytes: int
    redelivered: bool = False


class RabbitPeekResponse(BaseModel):
    """Response cho endpoint /rabbit/recent-messages."""
    exchange: str
    routing_key: str
    queue_used: str
    waited_seconds: float
    fetched_count: int
    messages: List[RabbitMessage]
