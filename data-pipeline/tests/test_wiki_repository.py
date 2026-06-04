from unittest.mock import MagicMock, patch

import pytest

from app.synthesis.wiki_repository import WikiRepository


def _make_cursor_mock(fetchone_val=None, fetchall_val=None):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone_val
    cur.fetchall.return_value = fetchall_val or []
    return cur


def _make_conn_mock(cursor):
    conn = MagicMock()
    conn.cursor.return_value = cursor
    return conn


class TestWikiRepository:
    @pytest.fixture
    def repo(self):
        return WikiRepository()

    def test_get_wiki_returns_dict_with_symbol(self, repo):
        cur = _make_cursor_mock(fetchone_val={
            "wiki_data": {
                "company_name": "Vinhomes JSC",
                "sector": "Real Estate",
                "business_summary": "Leading developer",
                "recent_performance": {"trend": "bullish"},
                "key_risks": [],
                "sentiment": "positive",
                "last_news_summary": "Q1 profit up 20%",
                "financials_snapshot": {"pe": 12.5, "pb": 2.1, "roe": 0.18},
            },
            "version": 3,
        })
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        result = repo.get_wiki("VHM")

        assert result["symbol"] == "VHM"
        assert result["version"] == 3
        assert result["company_name"] == "Vinhomes JSC"
        cur.execute.assert_called_once()

    def test_get_wiki_returns_none_when_not_found(self, repo):
        cur = _make_cursor_mock(fetchone_val=None)
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        result = repo.get_wiki("UNKNOWN")

        assert result is None

    def test_upsert_wiki_inserts_new_record(self, repo):
        cur = _make_cursor_mock(fetchone_val=(1,))
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        wiki_data = {"company_name": "Test Corp", "sector": "Tech"}

        with patch.object(repo, "insert_history") as mock_hist:
            repo.upsert_wiki("TEST", wiki_data)

            assert cur.execute.call_count == 1
            conn.commit.assert_called()
            cur.fetchone.assert_called()
            mock_hist.assert_called_once()
            args = mock_hist.call_args[0]
            assert args[0] == "TEST"
            assert args[2] == 1

    def test_upsert_wiki_updates_existing_record_increments_version(self, repo):
        cur = _make_cursor_mock(fetchone_val=(5,))
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        wiki_data = {"company_name": "Updated Corp", "sector": "Finance"}
        repo.upsert_wiki("VHM", wiki_data)

        cur.fetchone.assert_called()

    def test_insert_history_appends_to_history_table(self, repo):
        cur = _make_cursor_mock(fetchone_val=None)
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        wiki_data = {"company_name": "Test", "version": 2}
        repo.insert_history("TEST", wiki_data, 2)

        insert_call = cur.execute.call_args[0][0]
        assert "INSERT INTO company_wiki_history" in insert_call
        conn.commit.assert_called()

    def test_upsert_wiki_calls_insert_history_after_success(self, repo):
        cur = _make_cursor_mock(fetchone_val=(2,))
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        with patch.object(repo, "insert_history", wraps=repo.insert_history) as mock_hist:
            repo.upsert_wiki("ABC", {"company_name": "ABC Corp"})

            mock_hist.assert_called_once()
            args = mock_hist.call_args[0]
            assert args[0] == "ABC"
            assert args[2] == 2

    def test_get_recent_articles_uses_gin_index_query(self, repo):
        cur = _make_cursor_mock(fetchall_val=[])
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        repo.get_recent_articles("VNM")

        query = cur.execute.call_args[0][0]
        assert "symbols @>" in query
        assert "ORDER BY published_at DESC" in query

    def test_get_recent_prices_orders_by_date_desc(self, repo):
        cur = _make_cursor_mock(fetchall_val=[])
        conn = _make_conn_mock(cur)
        repo.get_connection = MagicMock(return_value=conn)

        repo.get_recent_prices("VNM")

        query = cur.execute.call_args[0][0]
        assert "ORDER BY trade_date DESC" in query
