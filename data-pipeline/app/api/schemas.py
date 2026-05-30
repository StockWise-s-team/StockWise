from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NewsSourceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    baseUrl: str = Field(alias="base_url")
    crawlerType: str = Field(alias="crawler_type")
    isActive: bool = Field(alias="is_active")


class NewsSourceToggle(BaseModel):
    is_active: bool


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
