import json

import pytest

import app.agents.analyst_agent as analyst_module
import app.agents.master_router as router_module
from app.agents.analyst_agent import LLM_UNAVAILABLE_MESSAGE, AnalystAgent
from app.agents.master_router import MasterRouterAgent
from app.agents.risk_manager_agent import RiskManagerAgent
from app.models.llm_factory import LLMProvider
from app.streaming.sse_manager import SSEManager


class Response:
    def __init__(self, content):
        self.content = content


class SequencedLLM:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    async def ainvoke(self, messages):
        self.calls += 1
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return Response(response)


class StreamingLLM:
    def __init__(self, chunks=None, error=None):
        self.chunks = chunks or []
        self.error = error
        self.prompts = []

    async def astream(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        for chunk in self.chunks:
            yield Response(chunk)


@pytest.mark.asyncio
async def test_router_repairs_malformed_json_once(monkeypatch):
    valid = json.dumps({"intent": "STOCK_OVERVIEW", "symbols": ["FPT"], "requires_portfolio": False})
    llm = SequencedLLM(["not-json", valid])
    monkeypatch.setattr(router_module, "configured_providers", lambda: [LLMProvider.GROQ])
    monkeypatch.setattr(router_module, "get_llm", lambda **kwargs: llm)
    result = await MasterRouterAgent().run({"user_message": "Phan tich FPT"})
    assert result["intent"] == "STOCK_OVERVIEW"
    assert llm.calls == 2


@pytest.mark.asyncio
async def test_router_fails_over_to_next_configured_provider(monkeypatch):
    valid = json.dumps({"intent": "STOCK_OVERVIEW", "symbols": ["FPT"], "requires_portfolio": False})
    failing = SequencedLLM([RuntimeError("down"), RuntimeError("down")])
    healthy = SequencedLLM([valid])
    monkeypatch.setattr(router_module, "configured_providers", lambda: [LLMProvider.GROQ, LLMProvider.OPENAI])
    monkeypatch.setattr(router_module, "get_llm", lambda provider, **kwargs: failing if provider == LLMProvider.GROQ else healthy)
    result = await MasterRouterAgent().run({"user_message": "Phan tich FPT"})
    assert result["intent"] == "STOCK_OVERVIEW"
    assert healthy.calls == 1


@pytest.mark.asyncio
async def test_analyst_streams_tokens(monkeypatch):
    sink = SSEManager("session-1")
    llm = StreamingLLM(["Xin", " chao"])
    monkeypatch.setattr(analyst_module, "configured_providers", lambda: [LLMProvider.GROQ])
    monkeypatch.setattr(analyst_module, "get_streaming_llm", lambda provider: llm)
    answer = await AnalystAgent().generate("fallback", [], sink)
    assert answer == "Xin chao"
    assert llm.prompts[0][0][0] == "system"
    assert llm.prompts[0][1] == ("human", "fallback")
    assert (await sink.queue.get()).event == "token"
    assert (await sink.queue.get()).event == "token"


@pytest.mark.asyncio
async def test_analyst_timeout_uses_grounded_fallback(monkeypatch):
    sink = SSEManager("session-1")
    monkeypatch.setattr(analyst_module, "configured_providers", lambda: [LLMProvider.GROQ])
    monkeypatch.setattr(analyst_module, "get_streaming_llm", lambda provider: StreamingLLM(error=TimeoutError()))
    assert await AnalystAgent().generate("grounded fallback", [], sink) == LLM_UNAVAILABLE_MESSAGE


@pytest.mark.asyncio
async def test_router_unknown_intent_defaults_out_of_scope(monkeypatch):
    invalid = json.dumps({"intent": "STOCK_ANALYSIS", "symbols": ["FPT"], "requires_portfolio": False})
    llm = SequencedLLM([invalid])
    monkeypatch.setattr(router_module, "configured_providers", lambda: [LLMProvider.GROQ])
    monkeypatch.setattr(router_module, "get_llm", lambda **kwargs: llm)
    result = await MasterRouterAgent().run({"user_message": "Phan tich FPT"})
    assert result["intent"] == "OUT_OF_SCOPE"


@pytest.mark.asyncio
async def test_router_merges_llm_symbols_with_deterministic_aliases(monkeypatch):
    valid = json.dumps({"intent": "STOCK_OVERVIEW", "symbols": ["FPT"], "requires_portfolio": False})
    llm = SequencedLLM([valid])
    monkeypatch.setattr(router_module, "configured_providers", lambda: [LLMProvider.GROQ])
    monkeypatch.setattr(router_module, "get_llm", lambda **kwargs: llm)
    result = await MasterRouterAgent().run({"user_message": "So sanh FPT va VIC"})
    assert result["symbols"] == ["FPT", "VIC"]


@pytest.mark.asyncio
async def test_risk_manager_optional_llm_review_is_structured():
    llm = SequencedLLM([json.dumps({"answer": "safe", "risk_flags": [], "has_disclaimer": True, "is_safe": True})])
    review = await RiskManagerAgent().review_with_llm(llm, [("human", "review")])
    assert review.answer == "safe"
    assert review.is_safe is True
