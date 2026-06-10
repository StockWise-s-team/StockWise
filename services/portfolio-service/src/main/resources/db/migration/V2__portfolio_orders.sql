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

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_portfolio_id ON orders(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
