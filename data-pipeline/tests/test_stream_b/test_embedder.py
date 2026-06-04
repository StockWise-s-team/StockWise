import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.stream_b.embedder import Embedder, COLLECTION_NAME, TEXT_SPLITTER


class TestEmbedder:
    @pytest.fixture
    def mock_qdrant(self):
        return MagicMock()

    @pytest.fixture
    def embedder(self, mock_qdrant):
        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            mock_settings.QDRANT_HOST = "localhost"
            mock_settings.QDRANT_PORT = 6333
            return Embedder(qdrant_client=mock_qdrant)

    def test_ensure_collection_creates_if_missing(self, mock_qdrant):
        mock_qdrant.get_collection.side_effect = Exception("Not found")

        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)
            e._embedding_dim = 1536
            e.ensure_collection()

        mock_qdrant.create_collection.assert_called_once()
        call_args = mock_qdrant.create_collection.call_args
        assert call_args.kwargs["collection_name"] == COLLECTION_NAME
        assert call_args.kwargs["vectors_config"].size == 1536

    def test_ensure_collection_skips_if_exists(self, mock_qdrant):
        mock_qdrant.get_collection.return_value = True

        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)
            e.ensure_collection()

        mock_qdrant.create_collection.assert_not_called()

    def test_embed_batch_local_falls_back(self, mock_qdrant):
        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "local"
            mock_settings.OPENAI_API_KEY = ""
            mock_settings.EMBEDDING_DIM = 384
            e = Embedder(qdrant_client=mock_qdrant)
            e._embedding_dim = 384

            with patch.object(e, "_embed_local", return_value=[[0.1] * 384]):
                result = e._embed_batch(["some text"])

        assert result == [[0.1] * 384]

    def test_embed_batch_openai(self, mock_qdrant):
        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)

            with patch.object(e, "_embed_openai", return_value=[[0.2] * 1536]):
                result = e._embed_batch(["some text"])

        assert result == [[0.2] * 1536]

    def test_embed_and_upsert_empty_articles(self, mock_qdrant):
        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)

            count = e.embed_and_upsert([])
        assert count == 0

    def test_embed_and_upsert_calls_upsert(self, mock_qdrant):
        mock_qdrant.get_collection.return_value = True

        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)
            e._embedding_dim = 1536

            with patch.object(e, "_embed_batch", return_value=[[0.1] * 1536]):
                count = e.embed_and_upsert([{
                    "url": "https://cafef.vn/test",
                    "title": "Test Article",
                    "content": "Short content.",
                    "symbols": ["VNM"],
                    "source_id": uuid.uuid4(),
                }])

        assert count == 1
        mock_qdrant.upsert.assert_called_once()
        points = mock_qdrant.upsert.call_args.kwargs["points"]
        assert len(points) == 1
        assert points[0].payload["title"] == "Test Article"
        assert points[0].payload["symbols"] == ["VNM"]

    def test_embed_and_upsert_chunks_long_content(self, mock_qdrant):
        mock_qdrant.get_collection.return_value = True

        long_content = " ".join([f"Paragraph {i} with some text." for i in range(50)])

        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)
            e._embedding_dim = 1536

            embed_count = [0]
            def fake_embed(texts):
                embed_count[0] += len(texts)
                return [[0.1] * 1536] * len(texts)

            with patch.object(e, "_embed_batch", side_effect=fake_embed):
                count = e.embed_and_upsert([{
                    "url": "https://cafef.vn/long",
                    "title": "Long Article",
                    "content": long_content,
                    "symbols": ["HPG"],
                    "source_id": uuid.uuid4(),
                }])

        assert count > 1
        assert embed_count[0] == count

    def test_embed_and_upsert_uses_title_if_no_content(self, mock_qdrant):
        mock_qdrant.get_collection.return_value = True

        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)
            e._embedding_dim = 1536

            with patch.object(e, "_embed_batch", return_value=[[0.1] * 1536]):
                count = e.embed_and_upsert([{
                    "url": "https://cafef.vn/no-content",
                    "title": "Only Title",
                    "content": "",
                    "symbols": [],
                    "source_id": uuid.uuid4(),
                }])

        assert count == 1
        points = mock_qdrant.upsert.call_args.kwargs["points"]
        assert points[0].payload["content"] == "Only Title"

    def test_resolve_dim_openai(self, mock_qdrant):
        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "openai"
            mock_settings.OPENAI_API_KEY = "fake-key"
            mock_settings.EMBEDDING_DIM = 1536
            e = Embedder(qdrant_client=mock_qdrant)
            assert e._resolve_dim() == 1536

    def test_resolve_dim_local(self, mock_qdrant):
        with patch("app.stream_b.embedder.settings") as mock_settings:
            mock_settings.EMBEDDING_MODEL = "local"
            mock_settings.OPENAI_API_KEY = ""
            mock_settings.EMBEDDING_DIM = 384
            e = Embedder(qdrant_client=mock_qdrant)
            assert e._resolve_dim() == 384

    def test_make_point_id_deterministic(self):
        id1 = Embedder._make_point_id("https://example.com/article", 0)
        id2 = Embedder._make_point_id("https://example.com/article", 0)
        id3 = Embedder._make_point_id("https://example.com/article", 1)
        assert id1 == id2
        assert id1 != id3
        assert len(id1) == 32


class TestTextSplitter:
    def test_splits_long_text(self):
        text = "Chunk one. " * 100
        chunks = TEXT_SPLITTER.split_text(text)
        assert len(chunks) > 1

    def test_overlap_less_than_chunk_size(self):
        text = "\n\n".join([f"Paragraph {i} with unique content number {i}." for i in range(30)])
        chunks = TEXT_SPLITTER.split_text(text)
        assert len(chunks) > 1
        for i in range(len(chunks) - 1):
            assert chunks[i] != chunks[i + 1]
