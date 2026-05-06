import psycopg2
import psycopg2.extras
from app.config import settings
from typing import Optional, Dict, Any

class WikiRepository:
    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST, dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD
        )

    def get_wiki(self, symbol: str) -> Optional[Dict[str, Any]]:
        return None

    def upsert_wiki(self, symbol: str, wiki_data: Dict[str, Any]):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO company_wiki (symbol, wiki_data, version, updated_at)
            VALUES (%s, %s::jsonb, 1, NOW())
            ON CONFLICT (symbol) DO UPDATE SET
                wiki_data = EXCLUDED.wiki_data,
                updated_at = NOW(),
                version = company_wiki.version + 1
        """, (symbol, psycopg2.extras.Json(wiki_data)))
        conn.commit()
        cur.close()
        conn.close()
