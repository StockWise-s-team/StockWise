from sqlalchemy import select
from app.db.database import get_db


class MarketRepository:
    async def get_ohlcv(self, symbol: str, limit: int = 30):
        return {
            "symbol": symbol,
            "data": "mock_market_data",
            "message": "MarketRepository: Returns OHLCV data for Text-to-SQL consumption.",
        }

    async def get_latest_price(self, symbol: str):
        return {
            "symbol": symbol,
            "price": 175.20,
            "message": "MarketRepository: Latest closing price.",
        }


market_repo = MarketRepository()
