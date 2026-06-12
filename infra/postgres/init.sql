CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'ROLE_USER',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open NUMERIC(20, 2),
    high NUMERIC(20, 2),
    low NUMERIC(20, 2),
    close NUMERIC(20, 2),
    volume BIGINT,
    UNIQUE(symbol, trade_date)
);

CREATE TABLE IF NOT EXISTS financial_ratios (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    period VARCHAR(20),
    pe_ratio NUMERIC(10, 2),
    pb_ratio NUMERIC(10, 2),
    eps NUMERIC(10, 2),
    roe NUMERIC(10, 4),
    roa NUMERIC(10, 4),
    UNIQUE(symbol, period)
);

-- Portfolio
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    virtual_cash NUMERIC(20, 2) DEFAULT 100000000 CHECK (virtual_cash >= 0)
);

CREATE TABLE IF NOT EXISTS holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    avg_price NUMERIC(20, 2),
    UNIQUE(portfolio_id, symbol),
    CHECK (quantity >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    type VARCHAR(4) NOT NULL CHECK(type IN ('BUY', 'SELL')),
    price NUMERIC(20, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'FILLED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT NOW(),
    cancelled_at TIMESTAMP,
    CHECK (price > 0),
    CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    type VARCHAR(4) NOT NULL CHECK(type IN ('BUY', 'SELL')),
    price NUMERIC(20, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    executed_at TIMESTAMP DEFAULT NOW(),
    CHECK (quantity > 0)
);

CREATE OR REPLACE RULE no_update_transactions AS ON UPDATE TO transactions DO INSTEAD NOTHING;
CREATE OR REPLACE RULE no_delete_transactions AS ON DELETE TO transactions DO INSTEAD NOTHING;

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_portfolio_id ON orders(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- News sources (admin-managed list)
CREATE TABLE IF NOT EXISTS news_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    crawler_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(name)
);

INSERT INTO news_sources (name, base_url, crawler_type) VALUES
    ('CafeF', 'https://cafef.vn', 'cafef'),
    ('Vietstock', 'https://vietstock.vn', 'vietstock')
ON CONFLICT DO NOTHING;

-- Company wiki (living state — Karpathy pattern)
CREATE TABLE IF NOT EXISTS company_wiki (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) UNIQUE NOT NULL,
    wiki_data JSONB NOT NULL DEFAULT '{}',
    version INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Wiki version history (append-only — never delete)
CREATE TABLE IF NOT EXISTS company_wiki_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    wiki_data JSONB NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, version)
);

-- Company metadata (fetched from FMP API)
CREATE TABLE IF NOT EXISTS company_info (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap NUMERIC(20, 0),
    business_summary TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- News articles raw store (before embedding)
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES news_sources(id),
    title TEXT NOT NULL,
    content TEXT,
    url VARCHAR(1000) UNIQUE,
    symbols VARCHAR(10)[],
    published_at TIMESTAMP,
    crawled_at TIMESTAMP DEFAULT NOW(),
    is_embedded BOOLEAN DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_news_articles_symbols ON news_articles USING GIN(symbols);
CREATE INDEX IF NOT EXISTS idx_news_articles_published ON news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_company_wiki_symbol ON company_wiki(symbol);

-- Pipeline execution history (append-only)
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_type VARCHAR(20) NOT NULL,  -- 'seed' | 'synthesis' | 'stream_a' | 'stream_b' | 'stream_c'
    trigger_type VARCHAR(20) NOT NULL DEFAULT 'scheduled',  -- 'scheduled' | 'manual' | 'api'
    status VARCHAR(20) NOT NULL DEFAULT 'running',  -- 'running' | 'success' | 'partial' | 'failed'
    symbols_requested INTEGER,
    symbols_processed INTEGER,
    errors TEXT[],  -- array of error messages
    duration_seconds INTEGER,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_type ON pipeline_runs(run_type);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started ON pipeline_runs(started_at DESC);

-- Pipeline run symbols (per-run detail)
CREATE TABLE IF NOT EXISTS pipeline_run_symbols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'success',  -- 'success' | 'error'
    error_message TEXT,
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_run_symbols_run ON pipeline_run_symbols(run_id);

-- Tracked symbols
CREATE TABLE IF NOT EXISTS tracked_symbols (
    symbol VARCHAR(10) PRIMARY KEY
);

-- Seed initial tracked symbols
INSERT INTO tracked_symbols (symbol) VALUES ('FPT'), ('VNM'), ('HPG'), ('VIC'), ('MSN') ON CONFLICT DO NOTHING;

-- Seed initial default user: user@stockwise.com / password123
INSERT INTO users (email, password_hash, role)
VALUES ('user@stockwise.com', '$2b$12$NNq/sYo9M1vREkZ7Q/lWpunpufzAkh60WyS8xpQMk5pZBWvRokzRa', 'ROLE_USER')
ON CONFLICT (email) DO NOTHING;

