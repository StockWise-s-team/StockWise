import pytest

import httpx

from app.services.news_retriever import HybridNewsRetriever, QdrantNewsRetriever, hashed_embedding


class FakeRetriever:
    def __init__(self, articles=None, error=None):
        self.articles = articles or []
        self.error = error

    async def search(self, symbol, limit):
        if self.error:
            raise self.error
        return self.articles


@pytest.mark.asyncio
async def test_hybrid_news_retriever_falls_back_on_error():
    fallback = [{"title": "SQL article"}]
    retriever = HybridNewsRetriever(FakeRetriever(error=RuntimeError("qdrant down")), FakeRetriever(fallback))
    assert await retriever.search("FPT", 5) == fallback


@pytest.mark.asyncio
async def test_hybrid_news_retriever_falls_back_on_empty_collection():
    fallback = [{"title": "SQL article"}]
    retriever = HybridNewsRetriever(FakeRetriever([]), FakeRetriever(fallback))
    assert await retriever.search("FPT", 5) == fallback


@pytest.mark.asyncio
async def test_qdrant_retriever_applies_symbol_and_date_filters():
    captured = {}

    def handler(request):
        captured.update(request.read() and __import__("json").loads(request.content))
        return httpx.Response(200, json={"result": []})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    await QdrantNewsRetriever(client).search("fpt", 5)
    assert captured["filter"]["must"][0] == {"key": "symbols", "match": {"any": ["FPT"]}}
    assert captured["filter"]["must"][1]["key"] == "published_at"
    await client.aclose()


def test_hashed_embedding_is_deterministic():
    assert hashed_embedding("FPT", 16) == hashed_embedding("FPT", 16)
