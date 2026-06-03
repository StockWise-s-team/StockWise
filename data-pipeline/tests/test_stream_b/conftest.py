import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch

import pytest


@pytest.fixture
def sample_html_article():
    return """
    <html>
    <head><title>Test Article</title></head>
    <body>
        <nav class="sidebar"><a href="/">Link</a></nav>
        <header><h1>Header Title</h1></header>
        <h1 class="title_news_detail">VNM Reports Record Profit, VPB and HPG Surge</h1>
        <p class="sapo_detail">VNM, VPB, and HPG all posted strong earnings.</p>
        <div id="content_detail">
            <p>VNM's net profit grew 20% in Q1. VPB announced expansion plans. HPG steel output increased.</p>
            <p>Analysts say VNM and VPB are buy-rated. HPG targets 30,000 VND.</p>
            <script>alert('bad');</script>
        </div>
        <div class="tag_stock">
            <a href="#">VNM</a>
            <a href="#">HPG</a>
            <a href="#">VPB</a>
        </div>
        <footer><p>Footer content</p></footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_cafef_article():
    return {
        "title": "VNM and HPG Report Q1 Earnings Beat",
        "content": "<p>VNM reported net profit of 5.6 trillion VND. HPG posted revenue of 40 trillion VND.</p>",
        "excerpt": "Two major stocks post strong results.",
        "url": "https://cafef.vn/vnm-hpg-q1-2026.chn",
        "published_at": "2026-05-28T10:00:00+07:00",
        "symbols": ["VNM", "HPG"],
        "source_name": "cafef",
    }


@pytest.fixture
def sample_vietstock_article():
    return {
        "title": "VPB Announces Capital Raise Plan",
        "content": "<p>VPB plans to raise 5 trillion VND through bond issuance.</p>",
        "excerpt": "VPB strategic move.",
        "url": "https://vietstock.vn/vpb-bond-2026.htm",
        "published_at": "1 giờ trước",
        "symbols": ["VPB"],
        "source_name": "vietstock",
    }


@pytest.fixture
def sample_normalized_article():
    return {
        "title": "VNM Reports Record Profit",
        "content": "VNM reported net profit of 5.6 trillion VND in Q1 2026.",
        "url": "https://cafef.vn/vnm-q1-2026.chn",
        "symbols": ["VNM"],
        "source_id": uuid.uuid4(),
        "published_at": datetime(2026, 5, 28, 10, 0, 0, tzinfo=timezone.utc),
        "crawled_at": datetime(2026, 5, 31, 2, 0, 0, tzinfo=timezone.utc),
    }


@pytest.fixture
def mock_source_row():
    return (uuid.uuid4(),)


@pytest.fixture
def mock_httpx_response():
    response = MagicMock()
    response.status_code = 200
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def mock_qdrant_client():
    client = MagicMock()
    client.get_collection = MagicMock(return_value=True)
    client.create_collection = MagicMock()
    client.upsert = MagicMock()
    return client


@pytest.fixture
def mock_httpx_async_client():
    return AsyncMock()
