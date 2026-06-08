# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

# StockWise Project Rules

Source: `docs/portfolio-svc/documents/kế hoạch.md` (module ownership & contribution rules). StockWise is a Vietnamese-market stock analysis and paper-trading platform built as microservices (Next.js frontend → `api-gateway` → `user-service`, `market-service`, `portfolio-service`, `ai-service`, `data-pipeline`; PostgreSQL, Qdrant, RabbitMQ).

## Module Ownership

Each service has one owner. Do not edit another owner's service without asking first.

| Module | Backend | Owner |
| --- | --- | --- |
| AI Advisor | `ai-service/` | Lead (Tiến) |
| Auth / Gateway | `services/api-gateway/`, `services/user-service/` | Member 2 (Bản) |
| Market Data & Chart | `services/market-service/` | Member 3 (Dũng) |
| Portfolio & Paper Trading | `services/portfolio-service/` | Member 4 (Anh) |
| Data Pipeline & DB | `data-pipeline/`, `infra/postgres/` | Member 5 (Xuân) |

Shared files needing the owner's review before changes: `docker-compose.yml` (Member 5 + Lead), `infra/postgres/init.sql` (Member 5), `README.md` / `frontend/src/app/dashboard/layout.tsx` / `frontend/src/components/ui/` (Lead). In `frontend/src/lib/api.ts` and `types.ts`, only edit your own section and don't rename shared types without agreement.

## Conflict-Avoidance Rules

1. One task per branch; never push directly to `main` (open a PR). Branch prefixes: `ai/`, `auth/`, `market/`, `portfolio/`, `pipeline/`, `frontend/` (shared UI only).
2. Don't modify another member's service, `dashboard/layout.tsx`, navigation, or `components/ui/` without notifying the team.
3. If a backend change alters an API contract, update the frontend types/API client in the same PR (or a linked PR).
4. If you change a DB schema, state the new/changed tables and columns, which services must update, and any seed data.
5. If you change a RabbitMQ payload, notify the producer **and** consumer owners. Don't remove existing fields a consumer uses; new fields should be optional for at least one sprint.
6. Never commit `.env`, API keys, JWT secrets, or database passwords.
7. Inside the Docker network, services call each other by service name (`postgres`, `rabbitmq`, `qdrant`), never `localhost`.

## Contract-First

Before building a full-stack feature, agree the contract: method + path, auth (required/none), request body, response body, status codes, error format, and which frontend page/component uses it. Each RabbitMQ event needs a contract: exchange, routing key, producer, consumer queues, payload, and compatibility notes.

Current messaging map (RabbitMQ; project migrated off Kafka — do not add Kafka):

| Exchange | Routing Key | Consumer Queues |
| --- | --- | --- |
| `market.exchange` | `price.updated` | `market_service_price_q`, `portfolio_service_price_q` |
| `news.exchange` | `raw.ingested` | `ai_service_news_q` |
| `portfolio.exchange` | `updated` | `ai_service_portfolio_q` |
| `wiki.exchange` | `synthesis.requested` | `synthesis_agent_q` |

## Pre-PR Checks

Run the checks for the stack you touched; if a tool is unavailable, say so in the PR.

- Frontend: `npm run lint` && `npm run build` (in `frontend/`)
- Java service: `mvn test` && `mvn package` (in `services/<service>/`)
- AI service / Data pipeline: `python -m compileall app`
- Docker: `docker compose config`

## PR Format

Title: `[AI|AUTH|MARKET|PORTFOLIO|PIPELINE] <summary>`. Description must cover: what changed, files/modules touched, how to test, any API/event/RabbitMQ payload change, screenshots for UI, and remaining risks.