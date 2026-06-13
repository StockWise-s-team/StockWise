from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.synthesis import merger as merger_module
from app.synthesis.merger import Merger
from app.synthesis.exceptions import LLMParseError, LLMRateLimitError, SynthesisError


class TestMerger:
    @pytest.fixture(autouse=True)
    def mock_genai(self):
        with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
             patch("google.generativeai.configure") as mock_configure:
            mock_model = MagicMock()
            mock_model.generate_content_async = AsyncMock()
            mock_model_cls.return_value = mock_model
            
            mock_resp = MagicMock()
            mock_resp.text = (
                '{"company_name":"Test","sector":"Tech","business_summary":"Summ",'
                '"recent_performance":{"trend":"neutral","notable":""},'
                '"key_risks":[],"sentiment":"neutral","last_news_summary":"",'
                '"financials_snapshot":{"pe":0,"pb":0,"roe":0},"version":2}'
            )
            mock_model.generate_content_async.return_value = mock_resp
            yield mock_model_cls, mock_configure, mock_model

    @pytest.fixture
    def merger(self):
        with patch.object(merger_module, "AsyncOpenAI") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            m = Merger()
            m._client = mock_client
            return m

    @pytest.fixture
    def mock_response(self):
        def _make(content: str):
            msg = MagicMock()
            msg.content = content
            choice = MagicMock()
            choice.message = msg
            resp = MagicMock()
            resp.choices = [choice]
            return resp
        return _make

    @pytest.fixture
    def sample_wiki(self):
        return {
            "symbol": "VNM",
            "company_name": "Vinamilk",
            "sector": "Dairy",
            "business_summary": "Leading dairy company in Vietnam",
            "recent_performance": {"trend": "stable", "notable": "flat"},
            "key_risks": ["Feed cost inflation"],
            "sentiment": "neutral",
            "last_news_summary": "",
            "financials_snapshot": {"pe": 20, "pb": 5, "roe": 0.3},
            "version": 1,
        }

    def test_merge_builds_correct_prompt(self, merger, sample_wiki):
        prompt = merger._build_user_prompt(
            sample_wiki, [{"title": "Q1 profit up"}], [{"trade_date": "2026-05-30"}]
        )
        assert "Vinamilk" in prompt
        assert "VNM" in prompt
        assert "Dairy" in prompt

    @pytest.mark.asyncio
    async def test_merge_calls_llm_with_json_response_format(self, merger, sample_wiki, mock_response):
        mock_resp = mock_response(
            '{"company_name":"Test","sector":"Tech","business_summary":"Summ",'
            '"recent_performance":{"trend":"neutral","notable":""},'
            '"key_risks":[],"sentiment":"neutral","last_news_summary":"",'
            '"financials_snapshot":{"pe":0,"pb":0,"roe":0},"version":2}'
        )
        merger._client.chat.completions.create = AsyncMock(return_value=mock_resp)

        await merger.merge(sample_wiki, [], [], "VNM")

        merger._client.chat.completions.create.assert_called_once()
        call_kwargs = merger._client.chat.completions.create.call_args.kwargs
        assert call_kwargs["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_merge_retries_on_rate_limit(self, merger, sample_wiki, mock_response):
        call_count = [0]

        async def fake_create(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                err = MagicMock()
                err.status_code = 429
                err.message = "Rate limit"
                raise Exception("429 Too Many Requests")
            return mock_response('{"company_name":"Test"}')

        merger._client.chat.completions.create = AsyncMock(side_effect=fake_create)

        with patch.object(merger_module.settings, "DATA_WIKI_FALLBACK_MODEL", ""):
            await merger.merge(sample_wiki, [], [], "VNM")

        assert call_count[0] == 3

    @pytest.mark.asyncio
    async def test_merge_raises_synthesis_error_on_llm_failure(self, merger, sample_wiki):
        merger._client.chat.completions.create = AsyncMock(
            side_effect=Exception("Connection refused")
        )

        with patch.object(merger_module.settings, "DATA_WIKI_FALLBACK_MODEL", ""):
            with pytest.raises(SynthesisError):
                await merger.merge(sample_wiki, [], [], "VNM")

    @pytest.mark.asyncio
    async def test_merge_raises_rate_limit_error_on_429(self, merger, sample_wiki):
        merger._client.chat.completions.create = AsyncMock(
            side_effect=Exception("429 Too Many Requests")
        )

        with patch.object(merger_module.settings, "DATA_WIKI_FALLBACK_MODEL", ""):
            with pytest.raises(LLMRateLimitError):
                await merger.merge(sample_wiki, [], [], "VNM")

    @pytest.mark.asyncio
    async def test_merge_raises_parse_error_on_invalid_json(self, merger, sample_wiki, mock_response):
        merger._client.chat.completions.create = AsyncMock(
            return_value=mock_response("not valid json {")
        )

        with pytest.raises(LLMParseError):
            await merger.merge(sample_wiki, [], [], "VNM")

    @pytest.mark.asyncio
    async def test_merge_raises_parse_error_on_non_dict_json(self, merger, sample_wiki, mock_response):
        merger._client.chat.completions.create = AsyncMock(
            return_value=mock_response('"just a string"')
        )

        with pytest.raises(LLMParseError):
            await merger.merge(sample_wiki, [], [], "VNM")

    @pytest.mark.asyncio
    async def test_merge_fills_missing_required_fields_from_default(self, merger, sample_wiki, mock_response):
        merger._client.chat.completions.create = AsyncMock(
            return_value=mock_response('{"company_name": "Test"}')
        )

        result = await merger.merge(sample_wiki, [], [], "VNM")

        assert "sector" in result
        assert "key_risks" in result
        assert "version" in result

    @pytest.mark.asyncio
    async def test_merge_uses_default_wiki_when_old_wiki_is_none(self, merger, mock_response):
        merger._client.chat.completions.create = AsyncMock(
            return_value=mock_response(
                '{"company_name":"New","sector":"Tech","business_summary":"",'
                '"recent_performance":{"trend":"neutral","notable":""},'
                '"key_risks":[],"sentiment":"neutral","last_news_summary":"",'
                '"financials_snapshot":{"pe":0,"pb":0,"roe":0},"version":1}'
            )
        )

        result = await merger.merge(None, [], [], "NEW")

        assert result["symbol"] == "NEW"
        assert result["company_name"] == "New"

    @pytest.mark.asyncio
    async def test_merge_injects_symbol_into_result(self, merger, sample_wiki, mock_response):
        merger._client.chat.completions.create = AsyncMock(
            return_value=mock_response(
                '{"company_name":"VNM Corp","sector":"Food","business_summary":"",'
                '"recent_performance":{"trend":"neutral","notable":""},'
                '"key_risks":[],"sentiment":"neutral","last_news_summary":"",'
                '"financials_snapshot":{"pe":0,"pb":0,"roe":0},"version":2}'
            )
        )

        result = await merger.merge(sample_wiki, [], [], "VNM")

        assert result["symbol"] == "VNM"
