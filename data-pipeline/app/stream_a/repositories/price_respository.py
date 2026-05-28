import psycopg2
import psycopg2.extras 
import logging
from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Optional

from app.config import settings

from dataclasses import dataclass

# app.stream_a.repositories.price_repository
logger = logging.getLogger(__name__)

# Data classes
@dataclass
class NormalizedPrice:
    symbol: str
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class NormalizedRatio:
    symbol: str
    period: str
    pe_ratio: Optional[Decimal]
    pb_ratio: Optional[Decimal]
    eps: Optional[Decimal]
    roe: Optional[Decimal]
    roa: Optional[Decimal]



class PriceRepository:
    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD
        )
    
    
    def upsert_prices(self, prices: List[NormalizedPrice]) -> int:
        if not prices:
            return 0

        conn = self.get_connection()
        cur = conn.cursor()
        rows_saved = 0

        try:
            for price in prices:
                cur.execute("""
                    INSERT INTO stock_prices
                        (symbol, trade_date, open, high, low, close, volume)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, trade_date) DO UPDATE SET
                        open   = EXCLUDED.open,
                        high   = EXCLUDED.high,
                        low    = EXCLUDED.low,
                        close  = EXCLUDED.close,
                        volume = EXCLUDED.volume
                """, (
                    price.symbol,
                    price.trade_date,
                    price.open,
                    price.high,
                    price.low,
                    price.close,
                    price.volume,
                ))
                rows_saved += 1
            
            conn.commit()
            logger.info(
                f"[PriceRepository] Upserted {rows_saved} price records"
            )
            return rows_saved
        except Exception as e:
            conn.rollback()
            logger.error(f"[PriceRepository] Error upserting prices: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def upsert_ratios(self, ratios: List[NormalizedRatio]) -> int:
        if not ratios:
            return 0
        conn = self.get_connection()
        cur = conn.cursor()
        rows_saved = 0
        try:
            for ratio in ratios:
                cur.execute("""
                    INSERT INTO financial_ratios
                        (symbol, period, pe_ratio, pb_ratio, eps, roe, roa)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, period) DO UPDATE SET
                        pe_ratio = EXCLUDED.pe_ratio,
                        pb_ratio = EXCLUDED.pb_ratio,
                        eps      = EXCLUDED.eps,
                        roe      = EXCLUDED.roe,
                        roa      = EXCLUDED.roa
                """, (
                    ratio.symbol,
                    ratio.period,
                    ratio.pe_ratio,
                    ratio.pb_ratio,
                    ratio.eps,
                    ratio.roe,
                    ratio.roa,
                ))
                rows_saved += 1
            conn.commit()
            logger.info(
                f"[PriceRepository] Upserted {rows_saved} ratio records"
            )
            return rows_saved
        except Exception as e:
            conn.rollback()
            logger.error(
                f"[PriceRepository] Failed to upsert ratios: {e}"
            )
            raise
        finally:
            cur.close()
            conn.close()

    def get_latest_prices(self, symbol: str, limit: int = 30) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT symbol, trade_date, open, high, low, close, volume
                FROM stock_prices
                WHERE symbol = %s
                ORDER BY trade_date DESC
                LIMIT %s
            """, (symbol, limit))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            cur.close()
            conn.close()

    def get_tracked_symbols(self) -> List[str]:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT symbol
                FROM stock_prices
                ORDER BY symbol
            """)
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()