import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PipelineRun:
    id: str
    run_type: str
    trigger_type: str
    status: str
    symbols_requested: Optional[int]
    symbols_processed: Optional[int]
    errors: List[str]
    duration_seconds: Optional[int]
    started_at: datetime
    finished_at: Optional[datetime]


@dataclass
class PipelineRunSymbol:
    id: str
    run_id: str
    symbol: str
    status: str
    error_message: Optional[str]
    processed_at: datetime


class PipelineRunsRepository:
    def get_connection(self):
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    # ── Create ──────────────────────────────────────────────────────────────────

    def create_run(
        self,
        run_type: str,
        trigger_type: str = "scheduled",
        symbols_requested: Optional[int] = None,
    ) -> str:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO pipeline_runs
                    (run_type, trigger_type, status, symbols_requested, symbols_processed)
                VALUES (%s, %s, 'running', %s, 0)
                RETURNING id
            """, (run_type, trigger_type, symbols_requested))
            run_id = str(cur.fetchone()[0])
            conn.commit()
            logger.info("[PipelineRuns] Created run %s (type=%s, trigger=%s)", run_id, run_type, trigger_type)
            return run_id
        except Exception as e:
            conn.rollback()
            logger.error("[PipelineRuns] Failed to create run: %s", e)
            raise
        finally:
            cur.close()
            conn.close()

    def add_symbol_result(
        self,
        run_id: str,
        symbol: str,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO pipeline_run_symbols
                    (run_id, symbol, status, error_message)
                VALUES (%s, %s, %s, %s)
            """, (run_id, symbol, status, error_message))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.warning("[PipelineRuns] Failed to add symbol result for %s: %s", symbol, e)
        finally:
            cur.close()
            conn.close()

    def finish_run(
        self,
        run_id: str,
        status: str,
        errors: Optional[List[str]] = None,
    ) -> None:
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE pipeline_runs
                SET status = %s,
                    errors = %s,
                    finished_at = NOW(),
                    duration_seconds = EXTRACT(EPOCH FROM (NOW() - started_at))::INTEGER,
                    symbols_processed = (
                        SELECT COUNT(DISTINCT symbol) FROM pipeline_run_symbols
                        WHERE run_id = %s AND status = 'success'
                    )
                WHERE id = %s
            """, (status, errors or [], run_id, run_id))
            conn.commit()
            logger.info("[PipelineRuns] Finished run %s with status=%s", run_id, status)
        except Exception as e:
            conn.rollback()
            logger.error("[PipelineRuns] Failed to finish run %s: %s", run_id, e)
        finally:
            cur.close()
            conn.close()

    # ── Read ───────────────────────────────────────────────────────────────────

    def list_runs(
        self,
        run_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            where = []
            params: List[Any] = []
            if run_type:
                where.append("run_type = %s")
                params.append(run_type)
            if status:
                where.append("status = %s")
                params.append(status)
            where_clause = " AND ".join(where) if where else "1=1"

            count_query = f"SELECT COUNT(*) FROM pipeline_runs WHERE {where_clause}"
            cur.execute(count_query, params)
            total = int(cur.fetchone()["count"])

            query = f"SELECT * FROM pipeline_runs WHERE {where_clause} ORDER BY started_at DESC LIMIT %s OFFSET %s"
            cur.execute(query, params + [limit, offset])
            runs = [self._serialize_row(dict(row)) for row in cur.fetchall()]

            return {"runs": runs, "total": total, "limit": limit, "offset": offset}
        except Exception as e:
            logger.error("[PipelineRuns] Failed to list runs: %s", e)
            raise
        finally:
            cur.close()
            conn.close()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("SELECT * FROM pipeline_runs WHERE id = %s", (run_id,))
            row = cur.fetchone()
            if not row:
                return None
            result = self._serialize_row(dict(row))
            cur.execute(
                "SELECT * FROM pipeline_run_symbols WHERE run_id = %s ORDER BY processed_at",
                (run_id,),
            )
            result["symbols_detail"] = [
                self._serialize_symbol_row(dict(r)) for r in cur.fetchall()
            ]
            return result
        except Exception as e:
            logger.error("[PipelineRuns] Failed to get run %s: %s", run_id, e)
            raise
        finally:
            cur.close()
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT
                    run_type,
                    status,
                    COUNT(*) as count,
                    AVG(duration_seconds) as avg_duration,
                    MAX(started_at) as last_run
                FROM pipeline_runs
                WHERE started_at >= NOW() - INTERVAL '7 days'
                GROUP BY run_type, status
                ORDER BY run_type, status
            """)
            by_type_status = [dict(row) for row in cur.fetchall()]

            cur.execute("""
                SELECT
                    run_type,
                    COUNT(*) as total_runs,
                    SUM(symbols_processed) as total_symbols,
                    AVG(duration_seconds) as avg_duration,
                    MIN(started_at) as first_run,
                    MAX(started_at) as last_run
                FROM pipeline_runs
                WHERE started_at >= NOW() - INTERVAL '7 days'
                GROUP BY run_type
            """)
            summary = [dict(row) for row in cur.fetchall()]

            return {
                "by_type_status": by_type_status,
                "summary": summary,
            }
        except Exception as e:
            logger.error("[PipelineRuns] Failed to get stats: %s", e)
            raise
        finally:
            cur.close()
            conn.close()

    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute("""
                SELECT r.*,
                    (SELECT COUNT(DISTINCT symbol) FROM pipeline_run_symbols s WHERE s.run_id = r.id AND s.status = 'success') as success_count,
                    (SELECT COUNT(DISTINCT symbol) FROM pipeline_run_symbols s WHERE s.run_id = r.id AND s.status = 'error') as error_count
                FROM pipeline_runs r
                ORDER BY r.started_at DESC
                LIMIT %s
            """, (limit,))
            return [self._serialize_row(dict(row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error("[PipelineRuns] Failed to get recent runs: %s", e)
            raise
        finally:
            cur.close()
            conn.close()

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _serialize_row(row: Dict[str, Any]) -> Dict[str, Any]:
        row["id"] = str(row["id"])
        if row.get("errors") is None:
            row["errors"] = []
        if row.get("started_at"):
            row["started_at"] = row["started_at"].isoformat()
        if row.get("finished_at"):
            row["finished_at"] = row["finished_at"].isoformat()
        if row.get("created_at"):
            row["created_at"] = row["created_at"].isoformat()
        if "success_count" in row:
            row["success_count"] = int(row["success_count"]) if row["success_count"] is not None else 0
            row["error_count"] = int(row["error_count"]) if row.get("error_count") is not None else 0
        return row

    @staticmethod
    def _serialize_symbol_row(row: Dict[str, Any]) -> Dict[str, Any]:
        row["id"] = str(row["id"])
        row["run_id"] = str(row["run_id"])
        if row.get("processed_at"):
            row["processed_at"] = row["processed_at"].isoformat()
        if row.get("error_message") is None:
            row["error_message"] = None
        return row
