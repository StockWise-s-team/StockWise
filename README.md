# StockWise — Hệ Thống Phân Tích & Giao Dịch Chứng Khoán Thông Minh

> **StockWise** is an AI-powered stock analysis and paper trading platform for the Vietnamese stock market.

---

## Architecture Overview

```
┌─────────────┐     ┌────────────────────────────────────────────┐
│   Frontend  │────▶│              api-gateway (8080)             │
│  Next.js 14 │     │         Spring Security + JWT Auth          │
│  Tailwind   │     └───────┬────────┬────────┬──────────────────┘
│  shadcn/ui  │             │        │        │
└─────────────┘     ┌───────▼──┐ ┌───▼────┐ ┌─▼──────────┐
                    │  user    │ │ market │ │ portfolio  │
                    │  (8081)  │ │ (8082) │ │  (8083)    │
                    │  auth    │ │ prices │ │ paper trade│
                    └────┬─────┘ └───┬────┘ └─────┬──────┘
                         │           │            │
                    ┌────▼───────────▼────────────▼─────┐
                    │         Kafka (9092)               │
                    │  market.price.updated              │
                    │  news.raw.ingested                 │
                    └────┬────────────────────┬─────────┘
                         │                    │
                  ┌──────▼──────┐    ┌───────▼────────┐
                  │data-pipeline│    │   ai-service   │
                  │   streams   │    │  FastAPI (8000) │
                  │  A (price)  │    │  LangGraph      │
                  │  B (news)   │    │  Gemini/GPT-4   │
                  └──────┬──────┘    └───────┬────────┘
                         │                   │
                    ┌────▼───────────────────▼────┐
                    │     PostgreSQL (5432)        │
                    │  users | market | portfolio  │
                    │  news_sources | company_wiki │
                    └─────────────────────────────┘

                    ┌──────────────────────────────┐
                    │  Redis (6379) — JWT cache     │
                    │  Qdrant (6333) — news vectors │
                    └──────────────────────────────┘
```

## Service Port Map

| Service | Port | Tech Stack |
|---------|------|-----------|
| frontend | 3000 | Next.js 14, TypeScript, Tailwind, shadcn/ui |
| api-gateway | 8080 | Spring Boot 3, Java 21, Spring Security |
| user-service | 8081 | Spring Boot 3, Java 21, PostgreSQL |
| market-service | 8082 | Spring Boot 3, Java 21, PostgreSQL |
| portfolio-service | 8083 | Spring Boot 3, Java 21, PostgreSQL |
| ai-service | 8000 | Python 3.11, FastAPI, LangGraph |
| data-pipeline | — | Python 3.11, APScheduler, vnstock3 |
| postgres | 5432 | PostgreSQL 16 |
| redis | 6379 | Redis 7 |
| kafka | 9092 | Apache Kafka |
| qdrant | 6333 | Qdrant Vector DB |

## Kafka Topics

| Topic | Producer | Consumer | Payload |
|-------|----------|----------|---------|
| `market.price.updated` | data-pipeline | market-service, portfolio-service | `{ symbol, prices[], ratios[] }` |
| `news.raw.ingested` | data-pipeline | ai-service | `{ article_id, symbol[], text, source }` |
| `portfolio.updated` | portfolio-service | ai-service | `{ user_id, holdings[] }` |
| `wiki.synthesis.requested` | scheduler | synthesis agent | `{ symbols[], trigger_reason }` |

## API Endpoint Summary

| Service | Method | Endpoint | Description |
|---------|--------|----------|-------------|
| user-service | POST | /auth/register | Register new user |
| user-service | POST | /auth/login | Login, returns JWT |
| user-service | POST | /auth/refresh | Refresh JWT token |
| market-service | GET | /market/price/{symbol} | Latest stock price |
| market-service | GET | /market/ratio/{symbol} | Financial ratios |
| market-service | GET | /market/ohlc/{symbol} | OHLCV chart data |
| portfolio-service | GET | /portfolio | User portfolio |
| portfolio-service | POST | /portfolio/order | Place paper trade order |
| portfolio-service | GET | /portfolio/pnl | Profit/Loss summary |
| ai-service | POST | /advisor/chat | AI chat (SSE stream) |
| ai-service | GET | /admin/sources | List news sources |
| ai-service | POST | /admin/sources | Add news source |
| ai-service | PATCH | /admin/sources/{id} | Toggle source active |
| ai-service | GET | /admin/wiki/{symbol} | View company wiki |
| ai-service | GET | /admin/wiki/{symbol}/history | Wiki version history |
| ai-service | POST | /admin/wiki/{symbol}/trigger | Trigger wiki synthesis |

## Karpathy Wiki Pattern

The data-pipeline implements the "Karpathy Wiki Pattern" for maintaining living company state:

1. **Read** current `company_wiki` JSONB from PostgreSQL for a symbol
2. **Merge** new articles + price data with existing wiki via LLM (Gemini Flash)
3. **Write** updated wiki back with `INSERT ... ON CONFLICT (symbol) DO UPDATE`
4. **Log** every version to `company_wiki_history` (append-only, never delete)

The wiki serves as a compressed, always-up-to-date context for the AI advisor.

## Team Setup

### Prerequisites
- Docker & Docker Compose v2
- Git

### Getting Started

```bash
# 1. Clone the repository
git clone <repo-url> stockwise
cd stockwise

# 2. Create .env from template
cp .env.example .env

# 3. Fill in your API keys in .env
#    - GEMINI_API_KEY (required for AI features)
#    - OPENAI_API_KEY (optional, for GPT-4o)
#    - JWT_SECRET (change in production)

# 4. Start all services
docker compose up --build

# 5. Access the application
#    Frontend: http://localhost:3000
#    API Gateway: http://localhost:8080
#    AI Service: http://localhost:8000/docs
```

### Development Workflow

| Team Member | Service Ownership |
|------------|-------------------|
| Backend Dev 1 | api-gateway, user-service |
| Backend Dev 2 | market-service, portfolio-service |
| AI Engineer | ai-service (LangGraph, agents) |
| Data Engineer | data-pipeline (streams A & B, synthesis) |
| Frontend Dev | Next.js frontend |

## Project Structure

```
stockwise/
├── docker-compose.yml
├── .env.example
├── frontend/          # Next.js 14, TypeScript, Tailwind
├── services/
│   ├── api-gateway/   # Spring Boot 3 — auth, routing
│   ├── user-service/  # Spring Boot 3 — user management
│   ├── market-service/ # Spring Boot 3 — market data
│   └── portfolio-service/ # Spring Boot 3 — paper trading
├── ai-service/         # Python FastAPI — AI advisor
├── data-pipeline/      # Python — data ingestion
└── infra/
    ├── postgres/       # DB init scripts
    ├── kafka/          # Topic creation
    └── qdrant/         # Vector DB config
```

## License

Proprietary — University Project
