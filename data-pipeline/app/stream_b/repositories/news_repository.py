import psycopg2
import psycopg2.extras
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.config import settings

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NormalizedArticle:
    source_id: str
    title: str
    content: str
    url: str
    symbols: List[str]
    published_at: Optional[datetime]
    crawled_at: str

class NewsRepository:
    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    def insert_article(self, article: NormalizedArticle) -> Optional[str]:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO news_articles
                    (source_id, title, content, url, symbols, published_at, crawled_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                RETURNING id
            """, (
                article.source_id,
                article.title,
                article.content,
                article.url,
                article.symbols,       # psycopg2 tự convert list → array
                article.published_at,
                article.crawled_at,
            ))
            result = cur.fetchone()
            conn.commit()
            if result:
                article_id = str(result[0])
                logger.info(
                    f"[NewsRepository] Inserted article '{article.title[:50]}' "
                    f"(id={article_id}, symbols={article.symbols})"
                )
                return article_id
            else:
                logger.debug(
                    f"[NewsRepository] Skipped duplicate URL: {article.url}"
                )
                return None
        except Exception as e:
            conn.rollback()
            logger.error(
                f"[NewsRepository] Failed to insert article '{article.title[:50]}': {e}"
            )
            raise
        finally:
            cur.close()
            conn.close()

    
    def insert_articles_bulk(self, articles: List[NormalizedArticle]) -> int:
        if not articles:
            return 0
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            data = [
                (
                    a.source_id,
                    a.title,
                    a.content,
                    a.url,
                    a.symbols,
                    a.published_at,
                    a.crawled_at,
                )
                for a in articles
            ]
            cur.execute("""
                INSERT INTO news_articles
                    (source_id, title, content, url, symbols, published_at, crawled_at)
                VALUES %s
                ON CONFLICT (url) DO NOTHING
            """, psycopg2.extras.execute_values(cur, """
                INSERT INTO news_articles
                    (source_id, title, content, url, symbols, published_at, crawled_at)
                VALUES %s
                ON CONFLICT (url) DO NOTHING
            """, data, template=None, page_size=100))
            rows_inserted = cur.rowcount
            conn.commit()
            logger.info(
                f"[NewsRepository] Bulk inserted {rows_inserted} articles"
            )
            return rows_inserted
        except Exception as e:
            conn.rollback()
            logger.error(
                f"[NewsRepository] Failed to bulk insert: {e}"
            )
            raise
        finally:
            cur.close()
            conn.close()

    def mark_embedded(self, url: str) -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE news_articles
                SET is_embedded = true
                WHERE url = %s
            """, (url,))
            rows_updated = cur.rowcount
            conn.commit()
            return rows_updated > 0
        except Exception as e:
            conn.rollback()
            logger.error(f"[NewsRepository] Failed to mark embedded: {e}")
            raise
        finally:
            cur.close()
            conn.close()

    
    def get_unembedded_articles(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT id, source_id, title, content, url, symbols,
                       published_at, crawled_at
                FROM news_articles
                WHERE is_embedded = false
                ORDER BY crawled_at DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def get_articles_by_symbol(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT id, source_id, title, content, url, symbols,
                       published_at, crawled_at
                FROM news_articles
                WHERE %s = ANY(symbols)
                ORDER BY published_at DESC
                LIMIT %s
            """, (symbol, limit))
            return [dict(row) for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()