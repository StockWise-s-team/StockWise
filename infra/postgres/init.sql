CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS market;
CREATE SCHEMA IF NOT EXISTS portfolio;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'USER',
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
    roa NUMERIC(10, 4)
);

-- Portfolio
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    virtual_cash NUMERIC(20, 2) DEFAULT 100000000
);

CREATE TABLE IF NOT EXISTS holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id),
    symbol VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    avg_price NUMERIC(20, 2)
);

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id),
    symbol VARCHAR(10) NOT NULL,
    type VARCHAR(4) CHECK(type IN ('BUY', 'SELL')),
    price NUMERIC(20, 2),
    quantity INTEGER,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- News sources (admin-managed list)
CREATE TABLE IF NOT EXISTS news_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    crawler_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO news_sources (name, base_url, crawler_type) VALUES
    ('CafeF', 'https://cafef.vn', 'cafef'),
    ('Vietstock', 'https://vietstock.vn', 'vietstock'),
    ('Reuters VN', 'https://www.reuters.com/world/asia-pacific', 'reuters_vn')
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
    created_at TIMESTAMP DEFAULT NOW()
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
