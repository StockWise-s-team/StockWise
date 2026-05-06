# Task: Scaffold StockWise Project Repository

You are an expert software architect. Your task is to scaffold a complete, ready-to-develop monorepo for the **StockWise** project based on the context below. 

**CRITICAL CONSTRAINTS:**
- Every service must follow **Single Responsibility Principle (SRP)** — one class/module = one responsibility
- Every service must be **Open/Closed Principle (OCP)** compliant — use interfaces and abstract classes so features can be extended without modifying existing code
- All services run inside Docker — every service must have a working `Dockerfile`
- Root `docker-compose.yml` must start the ENTIRE system with `docker compose up`
- Do NOT generate business logic — generate **structure, boilerplate, interfaces, config, and wiring** only
- Every file must compile/run without errors (even if it just returns mock data)

---

## Repository Structure to Create

```
stockwise/
├── docker-compose.yml                  # Root: starts all services + infra
├── .env.example                        # All env vars template
├── .gitignore
├── README.md
│
├── frontend/                           # Next.js 14, TypeScript, Tailwind
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx               # Landing / redirect to /dashboard
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   └── register/page.tsx
│       │   └── dashboard/
│       │       ├── layout.tsx
│       │       ├── page.tsx           # Overview
│       │       ├── portfolio/page.tsx
│       │       ├── sandbox/page.tsx
│       │       └── advisor/page.tsx   # AI chat + agent thoughts stream
│       ├── components/
│       │   ├── ui/                    # shadcn/ui re-exports
│       │   ├── charts/
│       │   │   └── OHLCChart.tsx      # Recharts candlestick (stub)
│       │   └── advisor/
│       │       └── AgentThoughtStream.tsx  # SSE consumer component
│       ├── lib/
│       │   ├── api.ts                 # Axios client, base URL from env
│       │   └── types.ts               # Shared TypeScript types
│       └── hooks/
│           └── useSSE.ts              # Custom hook for SSE stream
│
├── services/
│   │
│   ├── api-gateway/                   # Spring Boot 3, Java 21
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/main/java/com/stockwise/gateway/
│   │       ├── ApiGatewayApplication.java
│   │       ├── config/
│   │       │   ├── SecurityConfig.java        # Spring Security + JWT
│   │       │   ├── CorsConfig.java
│   │       │   └── KafkaConfig.java
│   │       ├── filter/
│   │       │   └── JwtAuthenticationFilter.java
│   │       ├── security/
│   │       │   ├── JwtTokenProvider.java      # Interface
│   │       │   └── JwtTokenProviderImpl.java
│   │       └── controller/
│   │           └── HealthController.java
│   │
│   ├── user-service/                  # Spring Boot 3, Java 21
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/main/java/com/stockwise/user/
│   │       ├── UserServiceApplication.java
│   │       ├── config/
│   │       │   └── SecurityConfig.java
│   │       ├── domain/
│   │       │   ├── entity/User.java           # @Entity
│   │       │   └── repository/UserRepository.java
│   │       ├── application/
│   │       │   ├── port/in/                   # Use case interfaces (OCP)
│   │       │   │   ├── RegisterUserUseCase.java
│   │       │   │   └── AuthenticateUserUseCase.java
│   │       │   ├── port/out/
│   │       │   │   └── UserPersistencePort.java
│   │       │   └── service/
│   │       │       └── UserService.java       # implements use case interfaces
│   │       ├── adapter/
│   │       │   ├── in/web/
│   │       │   │   └── AuthController.java    # POST /auth/register, /auth/login, /auth/refresh
│   │       │   └── out/persistence/
│   │       │       └── UserPersistenceAdapter.java
│   │       └── dto/
│   │           ├── RegisterRequest.java
│   │           ├── LoginRequest.java
│   │           └── AuthResponse.java          # { accessToken, refreshToken }
│   │
│   ├── market-service/                # Spring Boot 3, Java 21
│   │   ├── Dockerfile
│   │   ├── pom.xml
│   │   └── src/main/java/com/stockwise/market/
│   │       ├── MarketServiceApplication.java
│   │       ├── domain/
│   │       │   ├── entity/
│   │       │   │   ├── StockPrice.java        # symbol, date, open, high, low, close, volume
│   │       │   │   └── FinancialRatio.java    # PE, PB, EPS, ROE, ROA
│   │       │   └── repository/
│   │       │       ├── StockPriceRepository.java
│   │       │       └── FinancialRatioRepository.java
│   │       ├── application/
│   │       │   ├── port/in/
│   │       │   │   ├── GetStockPriceUseCase.java
│   │       │   │   └── GetFinancialRatioUseCase.java
│   │       │   └── service/
│   │       │       └── MarketService.java
│   │       ├── adapter/
│   │       │   └── in/web/
│   │       │       └── MarketController.java  # GET /market/price/{symbol}, /market/ratio/{symbol}, /market/ohlc/{symbol}
│   │       └── kafka/
│   │           └── MarketDataConsumer.java    # Listens to market.price.updated topic
│   │
│   └── portfolio-service/             # Spring Boot 3, Java 21
│       ├── Dockerfile
│       ├── pom.xml
│       └── src/main/java/com/stockwise/portfolio/
│           ├── PortfolioServiceApplication.java
│           ├── domain/
│           │   ├── entity/
│           │   │   ├── Portfolio.java         # userId, virtualCash (default 100M VND)
│           │   │   ├── Holding.java           # portfolioId, symbol, quantity, avgPrice
│           │   │   └── Transaction.java       # BUY/SELL, price, quantity, timestamp
│           │   └── repository/
│           │       ├── PortfolioRepository.java
│           │       ├── HoldingRepository.java
│           │       └── TransactionRepository.java
│           ├── application/
│           │   ├── port/in/
│           │   │   ├── GetPortfolioUseCase.java
│           │   │   ├── PlaceOrderUseCase.java  # Paper trading
│           │   │   └── GetPnLUseCase.java
│           │   └── service/
│           │       └── PortfolioService.java
│           ├── adapter/
│           │   └── in/web/
│           │       └── PortfolioController.java  # GET /portfolio, POST /portfolio/order, GET /portfolio/pnl
│           └── kafka/
│               └── PriceUpdateListener.java   # Recalculate P&L on price updates
│
├── ai-service/                        # Python 3.11, FastAPI, LangGraph
│   ├── Dockerfile
│   ├── requirements.txt               # fastapi, uvicorn, langgraph, langchain, google-generativeai, openai, sse-starlette, sqlalchemy, psycopg2
│   ├── pyproject.toml
│   ├── .env.example
│   └── app/
│       ├── main.py                    # FastAPI app, CORS, routers
│       ├── config.py                  # Settings via pydantic-settings
│       ├── api/
│       │   └── v1/
│       │       ├── router.py
│       │       └── endpoints/
│       │           ├── advisor.py     # POST /advisor/chat → SSE stream
│       │           └── health.py
│       ├── agents/
│       │   ├── base_agent.py          # Abstract base class (OCP)
│       │   ├── master_router.py       # Routes to sub-agents via LangGraph
│       │   ├── analyst_agent.py       # Technical analysis, charting data
│       │   ├── risk_manager_agent.py  # Review & filter advice
│       │   └── synthesis_agent.py    # Batch: news → company wiki state
│       ├── graph/
│       │   └── advisor_graph.py      # LangGraph StateGraph definition
│       ├── tools/
│       │   ├── base_tool.py           # Abstract Tool (OCP — extend to add tools)
│       │   ├── web_search_tool.py
│       │   ├── text_to_sql_tool.py
│       │   ├── wiki_reader_tool.py
│       │   ├── calculator_tool.py
│       │   └── charting_tool.py
│       ├── models/
│       │   ├── llm_factory.py         # Factory pattern: returns Gemini or GPT-4o
│       │   └── schemas.py             # Pydantic request/response schemas
│       └── db/
│           ├── database.py            # SQLAlchemy engine
│           └── repositories/
│               └── market_repo.py    # Read market data for Text-to-SQL
│
├── data-pipeline/                     # Python 3.11, APScheduler — dual-stream ingestion
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                    # Entry point, starts scheduler
│       ├── config.py                  # pydantic-settings, all env vars
│       ├── scheduler.py               # APScheduler — fires both streams every 4h
│       │
│       ├── sources/                   # Source list management (DB-driven, admin API)
│       │   ├── source_repository.py   # Read news_sources table from PostgreSQL
│       │   └── models.py              # NewsSource(id, name, url, type, active)
│       │
│       ├── stream_a/                  # Structured market data
│       │   ├── fetchers/
│       │   │   ├── base_fetcher.py    # Abstract BaseFetcher (OCP — extend per provider)
│       │   │   ├── vnstock_fetcher.py # Fetch OHLCV via vnstock3
│       │   │   └── ck_api_fetcher.py  # Fetch financial ratios from CK API
│       │   └── transformers/
│       │       ├── base_transformer.py
│       │       └── price_transformer.py  # Normalize, validate, deduplicate
│       │
│       ├── stream_b/                  # Unstructured news + events
│       │   ├── crawlers/
│       │   │   ├── base_crawler.py    # Abstract BaseCrawler (OCP — add new sources here)
│       │   │   ├── cafef_crawler.py
│       │   │   ├── vietstock_crawler.py
│       │   │   └── reuters_vn_crawler.py
│       │   ├── transformers/
│       │   │   ├── base_transformer.py
│       │   │   └── news_transformer.py  # Clean HTML, extract text, chunk by ~500 tokens
│       │   └── embedder.py            # Call embedding API → upsert Qdrant news_chunks
│       │
│       ├── synthesis/                 # Karpathy Wiki Pattern
│       │   ├── synthesis_agent.py     # Orchestrator: read wiki → merge → write
│       │   ├── wiki_repository.py     # Read/upsert company_wiki JSONB in PostgreSQL
│       │   ├── merger.py              # LLM call: diff old_wiki vs new_data → merged JSON
│       │   └── prompts.py             # System prompts for merge LLM call
│       │
│       └── kafka/
│           ├── producer.py            # Publish to market.price.updated, news.raw.ingested
│           └── topics.py              # Topic name constants
│
└── infra/
    ├── postgres/
    │   └── init.sql                   # Create schemas: users, market, portfolio
    ├── kafka/
    │   └── topics.sh                  # Create Kafka topics on startup
    └── qdrant/
        └── collections.json           # Qdrant collection config (optional)
```

---

## Specific Generation Instructions

### 1. `docker-compose.yml` (ROOT — most important file)

Generate a complete `docker-compose.yml` with these services:

**Infrastructure:**
- `postgres`: image `postgres:16-alpine`, port `5432`, volume, env POSTGRES_DB/USER/PASSWORD, healthcheck
- `redis`: image `redis:7-alpine`, port `6379`, healthcheck
- `zookeeper`: image `confluentinc/cp-zookeeper:7.6.0`
- `kafka`: image `confluentinc/cp-kafka:7.6.0`, port `9092`, depends on zookeeper, env KAFKA_ADVERTISED_LISTENERS
- `qdrant`: image `qdrant/qdrant:latest`, port `6333`, volume (optional)

**Application services** (all `build: context: ./path`, depends_on infrastructure with condition `service_healthy`):
- `api-gateway`: port `8080`
- `user-service`: port `8081`
- `market-service`: port `8082`
- `portfolio-service`: port `8083`
- `ai-service`: port `8000`
- `data-pipeline`: no exposed port (background worker)
- `frontend`: port `3000`, depends on `api-gateway`

All services share a network `stockwise-net`. All use `env_file: .env`.

### 2. `.env.example`

Include ALL variables:
```
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=stockwise
POSTGRES_USER=stockwise
POSTGRES_PASSWORD=stockwise_dev_password

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-256-bit-secret-change-in-production
JWT_ACCESS_TOKEN_EXPIRY_MS=900000
JWT_REFRESH_TOKEN_EXPIRY_MS=604800000

# AI APIs
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# Service URLs (internal Docker network)
USER_SERVICE_URL=http://user-service:8081
MARKET_SERVICE_URL=http://market-service:8082
PORTFOLIO_SERVICE_URL=http://portfolio-service:8083
AI_SERVICE_URL=http://ai-service:8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_AI_SERVICE_URL=http://localhost:8000
```

### 3. Spring Boot Services — `pom.xml` dependencies

Each Spring Boot service must include:
```xml
spring-boot-starter-web
spring-boot-starter-data-jpa
spring-boot-starter-security
spring-kafka
postgresql (runtime)
lombok
spring-boot-starter-validation
spring-boot-starter-actuator
```

### 4. Python Services — `requirements.txt`

**ai-service:**
```
fastapi==0.111.0
uvicorn[standard]==0.30.0
langgraph==0.1.19
langchain==0.2.6
langchain-google-genai==1.0.7
langchain-openai==0.1.14
sse-starlette==2.1.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
pydantic-settings==2.3.1
redis==5.0.7
```

**data-pipeline:**
```
apscheduler==3.10.4
vnstock3==0.3.0
kafka-python==2.0.2
psycopg2-binary==2.9.9
httpx==0.27.0
beautifulsoup4==4.12.3
lxml==5.2.2
pydantic-settings==2.3.1
google-generativeai==0.7.2
qdrant-client==1.9.1
langchain-text-splitters==0.2.2
```

### 5. OCP Pattern Example to Follow (apply across ALL services)

In Python (ai-service tools):
```python
# base_tool.py
from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    """Abstract base — extend to add new tools without modifying existing code (OCP)"""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @abstractmethod
    async def execute(self, input: str) -> Any: ...
```

In Java (use-case interfaces):
```java
// RegisterUserUseCase.java
public interface RegisterUserUseCase {
    AuthResponse register(RegisterRequest request);
}
// UserService.java
@Service
public class UserService implements RegisterUserUseCase, AuthenticateUserUseCase {
    // implementation
}
```

### 7. Karpathy Wiki Pattern — Key Stubs to Generate

**`data-pipeline/app/synthesis/merger.py`** — LLM merge call:
```python
# Takes: old_wiki (dict), new_articles (list[str]), new_price_data (dict)
# Returns: merged_wiki (dict) — same schema, evolved values
# LLM prompt: "Here is the current wiki state for {symbol}. 
#   Here are new articles and price data from the last 4 hours.
#   Update ONLY the fields that have materially changed.
#   Preserve fields that are still accurate. Return valid JSON only."
# Model: Gemini 1.5 Flash (cheap, fast for batch)
```

**`data-pipeline/app/synthesis/wiki_repository.py`** — upsert pattern:
```python
# Uses INSERT ... ON CONFLICT (symbol) DO UPDATE SET
#   wiki_data = EXCLUDED.wiki_data,
#   updated_at = NOW(),
#   version = company_wiki.version + 1
# Keeps version history in company_wiki_history table (append-only log)
```

**`infra/postgres/init.sql`** — add these tables to the schema:

```sql
-- News sources (admin-managed list)
CREATE TABLE news_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  base_url VARCHAR(500) NOT NULL,
  crawler_type VARCHAR(50) NOT NULL,  -- 'cafef' | 'vietstock' | 'reuters_vn'
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO news_sources (name, base_url, crawler_type) VALUES
  ('CafeF', 'https://cafef.vn', 'cafef'),
  ('Vietstock', 'https://vietstock.vn', 'vietstock'),
  ('Reuters VN', 'https://www.reuters.com/world/asia-pacific', 'reuters_vn');

-- Company wiki (living state — Karpathy pattern)
CREATE TABLE company_wiki (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol VARCHAR(10) UNIQUE NOT NULL,
  wiki_data JSONB NOT NULL DEFAULT '{}',
  version INTEGER DEFAULT 1,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Wiki version history (append-only — never delete)
CREATE TABLE company_wiki_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol VARCHAR(10) NOT NULL,
  wiki_data JSONB NOT NULL,
  version INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- News articles raw store (before embedding)
CREATE TABLE news_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID REFERENCES news_sources(id),
  title TEXT NOT NULL,
  content TEXT,
  url VARCHAR(1000) UNIQUE,
  symbols VARCHAR(10)[],         -- extracted company tickers mentioned
  published_at TIMESTAMP,
  crawled_at TIMESTAMP DEFAULT NOW(),
  is_embedded BOOLEAN DEFAULT false
);

CREATE INDEX idx_news_articles_symbols ON news_articles USING GIN(symbols);
CREATE INDEX idx_news_articles_published ON news_articles(published_at DESC);
CREATE INDEX idx_company_wiki_symbol ON company_wiki(symbol);
```

**Company wiki JSON schema** (example for VNM):
```json
{
  "symbol": "VNM",
  "company_name": "Vinamilk",
  "sector": "Consumer Staples",
  "business_summary": "...",
  "recent_performance": {
    "trend": "sideways",
    "notable": "Q2 revenue beat estimates by 3%"
  },
  "key_risks": ["input cost pressure", "FX exposure"],
  "sentiment": "neutral",
  "last_news_summary": "...",
  "financials_snapshot": {
    "pe": 14.2, "pb": 2.1, "roe": 0.32
  },
  "updated_at": "2025-05-06T04:00:00Z",
  "version": 12
}
```

**Qdrant collection schema** for news_chunks:
```python
# Collection: "news_chunks"
# Vector size: 768 (text-embedding-004) or 1536 (text-embedding-3-small)
# Payload fields:
{
  "article_id": "uuid",
  "symbol": "VNM",           # ticker mentioned (for filtered search)
  "source": "cafef",
  "title": "...",
  "chunk_text": "...",
  "published_at": 1715000000  # unix timestamp for range filter
}
# Agent query: filter by symbol + date range, then semantic search
```

### 8. Admin API for Source Management

Add to `ai-service` (or a separate `admin-service` if team prefers):

```
GET    /admin/sources          — list all news sources
POST   /admin/sources          — add new source { name, base_url, crawler_type }
PATCH  /admin/sources/{id}     — toggle is_active
DELETE /admin/sources/{id}     — soft delete (set is_active=false)
GET    /admin/wiki/{symbol}    — inspect current wiki state
GET    /admin/wiki/{symbol}/history — list version history
POST   /admin/wiki/{symbol}/trigger — manually trigger synthesis for one company
```

These endpoints are **admin-only** (role=ADMIN in JWT claims).

**`frontend/src/hooks/useSSE.ts`** — SSE hook that connects to ai-service:
```typescript
// Hook that opens EventSource to /advisor/chat/stream
// Yields { type: 'thought' | 'answer', content: string } events
// Closes connection on unmount
```

**`ai-service/app/graph/advisor_graph.py`** — LangGraph stub:
```python
# StateGraph with nodes: router → analyst → risk_manager → respond
# Edges: conditional routing based on intent
# Returns EventStream of agent thoughts
```

**`infra/postgres/init.sql`** — Full schema:
```sql
-- Schema: users
CREATE TABLE users (id UUID PRIMARY KEY, email VARCHAR UNIQUE, password_hash VARCHAR, role VARCHAR, created_at TIMESTAMP);

-- Schema: market  
CREATE TABLE stock_prices (id SERIAL, symbol VARCHAR(10), trade_date DATE, open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC, volume BIGINT);
CREATE TABLE financial_ratios (id SERIAL, symbol VARCHAR(10), period VARCHAR, pe_ratio NUMERIC, pb_ratio NUMERIC, eps NUMERIC, roe NUMERIC, roa NUMERIC);

-- Schema: portfolio
CREATE TABLE portfolios (id UUID PRIMARY KEY, user_id UUID REFERENCES users(id), virtual_cash NUMERIC DEFAULT 100000000);
CREATE TABLE holdings (id UUID PRIMARY KEY, portfolio_id UUID REFERENCES portfolios(id), symbol VARCHAR(10), quantity INTEGER, avg_price NUMERIC);
CREATE TABLE transactions (id UUID PRIMARY KEY, portfolio_id UUID REFERENCES portfolios(id), symbol VARCHAR(10), type VARCHAR(4), price NUMERIC, quantity INTEGER, executed_at TIMESTAMP);
```

---

## README.md Content to Generate

Include:
1. Project overview (Vietnamese + English)
2. Architecture diagram (ASCII)
3. Team setup: how to clone, copy `.env.example` → `.env`, fill API keys, `docker compose up`
4. Service port map table
5. Kafka topics table:

| Topic | Producer | Consumer | Payload |
|---|---|---|---|
| `market.price.updated` | data-pipeline stream A | market-service, portfolio-service | `{ symbol, prices[], ratios }` |
| `news.raw.ingested` | data-pipeline stream B | ai-service embedder | `{ article_id, symbol[], text, source }` |
| `portfolio.updated` | portfolio-service | ai-service (context) | `{ user_id, holdings[] }` |
| `wiki.synthesis.requested` | scheduler | synthesis agent | `{ symbols[], trigger_reason }` |
6. Development workflow: which service each team member owns
7. API endpoint summary table per service

---

## Final Checklist Before Finishing

Before declaring done, verify:
- [ ] `docker-compose.yml` has ALL 11 services (5 infra + 6 app)
- [ ] Every service folder has a `Dockerfile`
- [ ] `.env.example` has ALL required variables
- [ ] `infra/postgres/init.sql` creates ALL tables including `news_sources`, `company_wiki`, `company_wiki_history`, `news_articles`
- [ ] `news_sources` table is pre-seeded with CafeF, Vietstock, Reuters VN rows
- [ ] `data-pipeline/app/stream_a/` and `stream_b/` are separate modules (SRP)
- [ ] `data-pipeline/app/synthesis/merger.py` has the LLM merge stub
- [ ] `data-pipeline/app/synthesis/wiki_repository.py` uses INSERT ... ON CONFLICT upsert
- [ ] Every abstract class in Python has `ABC` + `@abstractmethod` (OCP)
- [ ] Every Spring Boot service has the Hexagonal Architecture folders: `domain/`, `application/port/`, `adapter/`
- [ ] Qdrant `news_chunks` collection config documented in `infra/qdrant/collections.json`
- [ ] Admin source management endpoints stubbed (role=ADMIN guard)
- [ ] `README.md` is complete with Kafka topics table and wiki pattern explanation
- [ ] No file is completely empty — every file has at minimum a working stub

Generate all files now.