import time
from unittest.mock import MagicMock, patch

import pytest

from app.sources.source_repository import SourceRepository, _CACHE_TTL_SECONDS


class TestSourceRepository:
    @pytest.fixture
    def repo(self):
        return SourceRepository()

    @pytest.fixture
    def mock_sources(self):
        import uuid
        return [
            {
                "id": uuid.uuid4(),
                "name": "cafef",
                "base_url": "https://cafef.vn",
                "crawler_type": "sitemap",
                "is_active": True,
            },
            {
                "id": uuid.uuid4(),
                "name": "vietstock",
                "base_url": "https://vietstock.vn",
                "crawler_type": "rss",
                "is_active": True,
            },
        ]

    def test_get_active_sources_returns_news_source_objects(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        result = repo.get_active_sources()

        assert len(result) == 2
        assert result[0].name == "cafef"
        assert result[1].name == "vietstock"
        assert result[0].is_active is True
        mock_cur.execute.assert_called_once()

    def test_get_active_sources_caches_result(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        repo.get_active_sources()
        repo.get_active_sources()

        mock_cur.execute.assert_called_once()

    def test_cache_hit_skips_db_query(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        repo.get_active_sources()
        assert repo._cache is not None
        assert repo._cache_timestamp > 0

        mock_cur.execute.assert_called_once()

    def test_invalidate_clears_cache(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        repo.get_active_sources()
        assert repo._cache is not None

        repo.invalidate()

        assert repo._cache is None
        assert repo._cache_timestamp == 0.0

    def test_invalidate_then_refetch_hits_db(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        repo.get_active_sources()
        repo.invalidate()
        repo.get_active_sources()

        assert mock_cur.execute.call_count == 2

    def test_get_active_sources_empty_db_returns_empty_list(self, repo):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        result = repo.get_active_sources()

        assert result == []
        assert repo._cache == []

    def test_get_active_sources_maps_all_fields(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        result = repo.get_active_sources()

        src = result[0]
        assert src.id == mock_sources[0]["id"]
        assert src.name == mock_sources[0]["name"]
        assert src.base_url == mock_sources[0]["base_url"]
        assert src.crawler_type == mock_sources[0]["crawler_type"]
        assert src.is_active == mock_sources[0]["is_active"]

    def test_cache_expires_after_ttl(self, repo, mock_sources):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_sources
        repo.get_connection = MagicMock(return_value=mock_conn)
        mock_conn.cursor.return_value = mock_cur

        repo.get_active_sources()
        repo._cache_timestamp = time.monotonic() - _CACHE_TTL_SECONDS - 1

        repo.get_active_sources()

        assert mock_cur.execute.call_count == 2

    def test_invalidate_closes_connections(self, repo):
        repo._cache = ["fake"]
        repo._cache_timestamp = time.time()

        repo.invalidate()

        assert repo._cache is None
