import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras

from app.config import settings

logger = logging.getLogger(__name__)

WIKI_SCHEMA = {
    "symbol": str,
    "company_name": str,
    "sector": str,
    "business_summary": str,
    "recent_performance": dict,
    "key_risks": list,
    "sentiment": str,
    "last_news_summary": str,
    "financials_snapshot": dict,
    "version": int,
}


class WikiRepository:
    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    def get_wiki(self, symbol: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                "SELECT wiki_data, version FROM company_wiki WHERE symbol = %s",
                (symbol,),
            )
            row = cur.fetchone()
            if row is None:
                logger.debug("[WikiRepository] No wiki found for %s", symbol)
                return None
            wiki = dict(row["wiki_data"])
            wiki["symbol"] = symbol
            wiki["version"] = row["version"]
            return wiki
        except Exception as e:
            logger.error("[WikiRepository] Failed to get wiki for %s: %s", symbol, e)
            raise
        finally:
            cur.close()
            conn.close()

    def upsert_wiki(self, symbol: str, wiki_data: Dict[str, Any]) -> None:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO company_wiki (symbol, wiki_data, version, updated_at)
                VALUES (%s, %s::jsonb, 1, NOW())
                ON CONFLICT (symbol) DO UPDATE SET
                    wiki_data = EXCLUDED.wiki_data,
                    updated_at = NOW(),
                    version = company_wiki.version + 1
                RETURNING version
            """, (symbol, psycopg2.extras.Json(wiki_data)))
            result = cur.fetchone()
            conn.commit()
            new_version = result[0] if result else 1
            self.insert_history(symbol, wiki_data, new_version)
            logger.info("[WikiRepository] Upserted wiki for %s (version %d)", symbol, new_version)
        except Exception as e:
            conn.rollback()
            logger.error("[WikiRepository] Failed to upsert wiki for %s: %s", symbol, e)
            raise
        finally:
            cur.close()
            conn.close()

    def insert_history(self, symbol: str, wiki_data: Dict[str, Any], version: int) -> None:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO company_wiki_history (symbol, wiki_data, version, created_at)
                VALUES (%s, %s::jsonb, %s, NOW())
            """, (symbol, psycopg2.extras.Json(wiki_data), version))
            conn.commit()
            logger.debug(
                "[WikiRepository] Inserted history for %s (version %d)", symbol, version
            )
        except Exception as e:
            conn.rollback()
            logger.error(
                "[WikiRepository] Failed to insert history for %s: %s", symbol, e
            )
            raise
        finally:
            cur.close()
            conn.close()

    def get_recent_articles(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(
                """
                SELECT id, title, content, url, symbols, published_at, crawled_at
                FROM news_articles
                WHERE %s = ANY(symbols)
                ORDER BY published_at DESC NULLS LAST
                LIMIT %s
            """,
                (symbol, limit),
            )
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error("[WikiRepository] Failed to get articles for %s: %s", symbol, e)
            raise
        finally:
            cur.close()
            conn.close()

    def get_recent_prices(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
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
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error("[WikiRepository] Failed to get prices for %s: %s", symbol, e)
            raise
        finally:
            cur.close()
            conn.close()
