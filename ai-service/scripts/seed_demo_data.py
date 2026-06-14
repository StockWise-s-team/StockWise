import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import AsyncSessionLocal

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

STATEMENTS = [
    """
    INSERT INTO users (id, email, password_hash, role)
    VALUES (CAST(:user_id AS uuid), 'demo@stockwise.local', 'demo-only', 'ROLE_USER')
    ON CONFLICT (id) DO NOTHING
    """,
    """
    INSERT INTO portfolios (id, user_id, virtual_cash)
    VALUES ('00000000-0000-0000-0000-000000000010', CAST(:user_id AS uuid), 25000000)
    ON CONFLICT (id) DO NOTHING
    """,
    """
    INSERT INTO holdings (portfolio_id, symbol, quantity, avg_price) VALUES
      ('00000000-0000-0000-0000-000000000010', 'FPT', 100, 120000),
      ('00000000-0000-0000-0000-000000000010', 'HPG', 200, 26000)
    ON CONFLICT (portfolio_id, symbol) DO NOTHING
    """,
    """
    INSERT INTO stock_prices (symbol, trade_date, open, high, low, close, volume) VALUES
      ('FPT', '2026-05-30', 131000, 134000, 130500, 133500, 4200000),
      ('HPG', '2026-05-30', 27500, 28100, 27300, 27900, 18500000),
      ('VNM', '2026-05-30', 66500, 67200, 66000, 66900, 3100000)
    ON CONFLICT (symbol, trade_date) DO UPDATE SET close = EXCLUDED.close, volume = EXCLUDED.volume
    """,
    """
    INSERT INTO financial_ratios (symbol, period, pe_ratio, pb_ratio, eps, roe, roa) VALUES
      ('FPT', '2025', 24.10, 6.20, 5539, 0.2850, 0.1220),
      ('HPG', '2025', 15.80, 1.70, 1766, 0.1120, 0.0610),
      ('VNM', '2025', 17.20, 4.10, 3889, 0.2410, 0.1580)
    ON CONFLICT (symbol, period) DO NOTHING
    """,
    """
    INSERT INTO company_wiki (symbol, wiki_data) VALUES
      ('FPT', '{"summary":"FPT hoạt động trong công nghệ, viễn thông và giáo dục."}'),
      ('HPG', '{"summary":"Hòa Phát hoạt động chính trong lĩnh vực thép."}'),
      ('VNM', '{"summary":"Vinamilk hoạt động trong ngành sữa và sản phẩm dinh dưỡng."}')
    ON CONFLICT (symbol) DO NOTHING
    """,
    """
    INSERT INTO news_articles (source_id, title, content, url, symbols, published_at)
    SELECT id, 'FPT công bố cập nhật hoạt động kinh doanh', 'Fixture demo cho advisor.', 'https://demo.stockwise.local/news/fpt', ARRAY['FPT'], NOW()
    FROM news_sources WHERE name = 'CafeF'
    ON CONFLICT (url) DO NOTHING
    """,
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        for statement in STATEMENTS:
            await session.execute(text(statement), {"user_id": DEMO_USER_ID})
        await session.commit()
    print("Seeded explicit StockWise AI demo fixtures for FPT, HPG, and VNM.")


if __name__ == "__main__":
    asyncio.run(seed())
