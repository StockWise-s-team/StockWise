from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.synthesis.synthesis_agent import SynthesisAgent


class TestSynthesisAgent:
    @pytest.fixture
    def mock_wiki_repo(self):
        repo = MagicMock()
        repo.get_wiki = MagicMock(return_value=None)
        repo.get_recent_articles = MagicMock(return_value=[])
        repo.get_recent_prices = MagicMock(return_value=[])
        repo.upsert_wiki = MagicMock()
        return repo

    @pytest.fixture
    def mock_merger(self):
        m = MagicMock()
        m.merge = AsyncMock(return_value={
            "company_name": "Test Corp",
            "sector": "Tech",
            "business_summary": "Test",
            "recent_performance": {"trend": "neutral", "notable": ""},
            "key_risks": [],
            "sentiment": "neutral",
            "last_news_summary": "",
            "financials_snapshot": {"pe": 0, "pb": 0, "roe": 0},
            "version": 1,
        })
        return m

    @pytest.mark.asyncio
    async def test_synthesize_calls_merger_with_db_data(
        self, mock_wiki_repo, mock_merger
    ):
        mock_wiki_repo.get_wiki.return_value = {"company_name": "Vinamilk", "version": 1}
        mock_wiki_repo.get_recent_articles.return_value = [{"title": "Q1 results"}]
        mock_wiki_repo.get_recent_prices.return_value = [{"trade_date": "2026-05-30"}]

        agent = SynthesisAgent()
        agent.wiki_repo = mock_wiki_repo
        agent.merger = mock_merger

        await agent.synthesize(["VNM"])

        mock_wiki_repo.get_wiki.assert_called_with("VNM")
        mock_wiki_repo.get_recent_articles.assert_called_with("VNM", limit=20)
        mock_wiki_repo.get_recent_prices.assert_called_with("VNM", limit=5)
        mock_merger.merge.assert_awaited_once()
        mock_wiki_repo.upsert_wiki.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesize_per_symbol_error_isolation(
        self, mock_wiki_repo, mock_merger
    ):
        mock_wiki_repo.get_recent_articles.side_effect = [
            [{"title": "VNM news"}],
            RuntimeError("DB error for HPG"),
        ]
        mock_wiki_repo.get_recent_prices.return_value = []
        mock_merger.merge.side_effect = [
            AsyncMock(return_value={"version": 1}),
            RuntimeError("LLM failed"),
        ]

        agent = SynthesisAgent()
        agent.wiki_repo = mock_wiki_repo
        agent.merger = mock_merger

        await agent.synthesize(["VNM", "HPG"])

        assert mock_merger.merge.call_count == 1
        mock_wiki_repo.upsert_wiki.assert_called_once()

    @pytest.mark.asyncio
    async def test_synthesize_logs_completion(self, mock_wiki_repo, mock_merger):
        agent = SynthesisAgent()
        agent.wiki_repo = mock_wiki_repo
        agent.merger = mock_merger

        with patch("app.synthesis.synthesis_agent.logger") as mock_logger:
            await agent.synthesize(["VNM"])

            info_calls = [c for c in mock_logger.info.call_args_list]
            assert any("Starting synthesis" in str(c) for c in info_calls)
            assert any("Completed synthesis" in str(c) for c in info_calls)

    @pytest.mark.asyncio
    async def test_synthesize_skips_when_no_symbols(self, mock_wiki_repo):
        agent = SynthesisAgent()
        agent.wiki_repo = mock_wiki_repo

        with patch("app.synthesis.synthesis_agent.logger") as mock_logger:
            await agent.synthesize([])

        mock_wiki_repo.get_wiki.assert_not_called()
        mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_synthesize_calls_upsert_after_merge(
        self, mock_wiki_repo, mock_merger
    ):
        merged_result = {
            "company_name": "Vinamilk",
            "sector": "Dairy",
            "business_summary": "Leading dairy",
            "recent_performance": {"trend": "bullish", "notable": ""},
            "key_risks": [],
            "sentiment": "positive",
            "last_news_summary": "Q1 profit up",
            "financials_snapshot": {"pe": 20, "pb": 5, "roe": 0.3},
            "version": 2,
        }
        mock_merger.merge = AsyncMock(return_value=merged_result)

        agent = SynthesisAgent()
        agent.wiki_repo = mock_wiki_repo
        agent.merger = mock_merger

        await agent.synthesize(["VNM"])

        mock_wiki_repo.upsert_wiki.assert_called_once_with("VNM", merged_result)
