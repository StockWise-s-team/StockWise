CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);

INSERT INTO users (id, email, password_hash, role, full_name, created_at)
VALUES (
    '00000000-0000-0000-0000-00000000ad10',
    'admin@stockwise.local',
    crypt('password123', gen_salt('bf', 10)),
    'ROLE_ADMIN',
    'StockWise Admin',
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = 'ROLE_ADMIN',
    full_name = EXCLUDED.full_name;

INSERT INTO portfolios (id, user_id, virtual_cash)
VALUES (
    '00000000-0000-0000-0000-00000000ad20',
    '00000000-0000-0000-0000-00000000ad10',
    100000000
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO tracked_symbols (symbol) VALUES
    ('FPT'),
    ('HPG'),
    ('VNM')
ON CONFLICT (symbol) DO NOTHING;

-- Seed default user selections for admin user
INSERT INTO user_tracked_symbols (user_id, symbol)
VALUES
    ('00000000-0000-0000-0000-00000000ad10', 'FPT'),
    ('00000000-0000-0000-0000-00000000ad10', 'HPG'),
    ('00000000-0000-0000-0000-00000000ad10', 'VNM')
ON CONFLICT DO NOTHING;

INSERT INTO user_news_sources (user_id, source_id)
SELECT '00000000-0000-0000-0000-00000000ad10'::UUID, id
FROM news_sources
ON CONFLICT DO NOTHING;

INSERT INTO stock_prices (symbol, trade_date, open, high, low, close, volume) VALUES
    ('FPT', '2026-05-30', 131000, 134000, 130500, 133500, 4200000),
    ('HPG', '2026-05-30', 27500, 28100, 27300, 27900, 18500000),
    ('VNM', '2026-05-30', 66500, 67200, 66000, 66900, 3100000)
ON CONFLICT (symbol, trade_date) DO UPDATE SET
    open = EXCLUDED.open,
    high = EXCLUDED.high,
    low = EXCLUDED.low,
    close = EXCLUDED.close,
    volume = EXCLUDED.volume;

INSERT INTO financial_ratios (symbol, period, pe_ratio, pb_ratio, eps, roe, roa) VALUES
    ('FPT', '2025', 24.10, 6.20, 5539, 0.2850, 0.1220),
    ('HPG', '2025', 15.80, 1.70, 1766, 0.1120, 0.0610),
    ('VNM', '2025', 17.20, 4.10, 3889, 0.2410, 0.1580)
ON CONFLICT (symbol, period) DO UPDATE SET
    pe_ratio = EXCLUDED.pe_ratio,
    pb_ratio = EXCLUDED.pb_ratio,
    eps = EXCLUDED.eps,
    roe = EXCLUDED.roe,
    roa = EXCLUDED.roa;

INSERT INTO company_info (symbol, company_name, sector, industry, market_cap, business_summary) VALUES
    ('FPT', 'FPT Corporation', 'Technology', 'IT Services', 195000000000000, 'Vietnam technology, telecom, and education group.'),
    ('HPG', 'Hoa Phat Group', 'Materials', 'Steel', 165000000000000, 'Vietnam steel and industrial manufacturing group.'),
    ('VNM', 'Vinamilk', 'Consumer Staples', 'Dairy Products', 140000000000000, 'Vietnam dairy and nutrition company.')
ON CONFLICT (symbol) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    sector = EXCLUDED.sector,
    industry = EXCLUDED.industry,
    market_cap = EXCLUDED.market_cap,
    business_summary = EXCLUDED.business_summary,
    updated_at = NOW();

INSERT INTO company_wiki (symbol, wiki_data) VALUES
    ('FPT', '{"summary":"FPT operates in technology, telecom, and education."}'),
    ('HPG', '{"summary":"Hoa Phat operates primarily in steel and industrial manufacturing."}'),
    ('VNM', '{"summary":"Vinamilk operates in dairy and nutrition products."}')
ON CONFLICT (symbol) DO UPDATE SET
    wiki_data = EXCLUDED.wiki_data,
    updated_at = NOW();

INSERT INTO holdings (portfolio_id, symbol, quantity, avg_price) VALUES
    ('00000000-0000-0000-0000-00000000ad20', 'FPT', 100, 120000),
    ('00000000-0000-0000-0000-00000000ad20', 'HPG', 200, 26000)
ON CONFLICT (portfolio_id, symbol) DO NOTHING;
