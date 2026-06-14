import re
import logging
from datetime import date
from time import monotonic
from typing import Any
import unicodedata

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.analyst_agent import AnalystAgent
from app.agents.risk_manager_agent import RiskManagerAgent
from app.config import settings
from app.db.repositories.chat_repo import ChatRepository
from app.db.repositories.content_repo import ContentRepository
from app.db.repositories.tracked_symbols_repo import TrackedSymbolsRepository
from app.graph.graph_config import get_advisor_graph, get_graph_config
from app.graph.state import AdvisorState
from app.models.schemas import ChatRequest, Citation, ToolResult
from app.services.data_providers import create_market_provider, create_portfolio_provider
from app.services.news_retriever import create_news_retriever
from app.services.prompt_context_builder import PromptContextBuilder
from app.streaming.sse_manager import SSEManager
from app.tools.calculator_tool import CalculatorTool
from app.tools.charting_tool import ChartingTool
from app.tools.market_data_tool import MarketDataTool
from app.tools.news_search_tool import NewsSearchTool
from app.tools.portfolio_reader_tool import PortfolioReaderTool
from app.tools.tracked_symbols_tool import TrackedSymbolsTool
from app.tools.tool_registry import ToolRegistry
from app.tools.wiki_reader_tool import WikiReaderTool

logger = logging.getLogger(__name__)


class AdvisorService:
    SYMBOL_SCOPED_TOOLS = {"market_data", "wiki_reader", "news_search", "charting"}

    def __init__(self, db: AsyncSession, sink: SSEManager):
        self.sink = sink
        self.market_provider = create_market_provider(db)
        self.chat_repo = ChatRepository(db)
        content_repo = ContentRepository(db)
        self.registry = ToolRegistry(
            [
                MarketDataTool(self.market_provider),
                WikiReaderTool(content_repo),
                NewsSearchTool(create_news_retriever(content_repo)),
                PortfolioReaderTool(create_portfolio_provider(db)),
                TrackedSymbolsTool(TrackedSymbolsRepository(db)),
                CalculatorTool(),
                ChartingTool(self.market_provider),
            ]
        )

    async def process(self, request: ChatRequest, user_id: str) -> None:
        started_at = monotonic()
        session_id = self.sink.session_id
        await self.chat_repo.get_or_create_session(session_id, user_id, request.message[:120])
        history = await self.chat_repo.load_history(session_id, settings.AI_MAX_HISTORY_MESSAGES)
        await self.chat_repo.add_message(session_id, user_id, "user", request.message)
        await self.sink.emit_thought("Đang phân loại yêu cầu.", node="router")

        result = await get_advisor_graph().ainvoke(
            self._initial_state(request, user_id, history),
            config=get_graph_config(session_id, runtime=self),
        )
        results = [ToolResult.model_validate(item) for item in result.get("tool_results", [])]
        answer = result["final_answer"]
        risk_flags = result.get("risk_flags", [])
        citations = [Citation.model_validate(item) for item in result.get("citations", [])]
        freshness = result.get("data_freshness", {})
        await self.chat_repo.add_message(
            session_id,
            user_id,
            "assistant",
            answer,
            {"intent": result["intent"], "symbols": result.get("symbols", []), "risk_flags": risk_flags},
        )
        await self.sink.emit_final(
            answer=answer,
            intent=result["intent"],
            symbols=result.get("symbols", []),
            citations=citations or self._citations(results),
            risk_flags=risk_flags,
            has_disclaimer=result.get("has_disclaimer", False),
            data_mode=result.get("data_mode", self._data_mode()),
            data_freshness=freshness or self._freshness(results),
        )
        logger.info(
            "Advisor turn completed",
            extra={"session_id": session_id, "intent": result["intent"], "latency_ms": int((monotonic() - started_at) * 1000)},
        )

    async def validate_symbols(self, candidates: list[str]) -> list[str]:
        validated: list[str] = []
        for symbol in sorted(set(candidates)):
            try:
                if await self.market_provider.get_latest_price(symbol):
                    validated.append(symbol)
            except Exception as exc:
                logger.warning("Symbol validation failed for %s: %s", symbol, exc)
                return []
        return validated

    async def execute_tool(self, tool_name: str, state: AdvisorState) -> ToolResult | list[ToolResult]:
        tool = self.registry.get(tool_name)
        if tool_name in self.SYMBOL_SCOPED_TOOLS:
            symbols = state.get("symbols") or []
            if not symbols:
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    error_code="MISSING_SYMBOL",
                    error_message="No validated symbol available for this request.",
                )
            results = []
            for symbol in symbols:
                results.append(await self._execute_single_tool(tool, tool_name, {"symbol": symbol}))
            return results

        tool_input = self._tool_input(tool_name, state)
        return await self._execute_single_tool(tool, tool_name, tool_input)

    async def _execute_single_tool(self, tool: Any, tool_name: str, tool_input: dict[str, Any]) -> ToolResult:
        await self.sink.emit_tool_call(tool_name, tool_input)
        result = await tool.execute(tool_input)
        await self.sink.emit_tool_result(
            tool_name,
            "Đã truy xuất dữ liệu." if result.success else (result.error_message or "Không có dữ liệu."),
        )
        if tool_name == "charting" and result.success:
            await self.sink.emit_chart_data(result.data)
        return result

    async def generate_answer(self, state: AdvisorState) -> str:
        results = [ToolResult.model_validate(item) for item in state.get("tool_results", [])]
        draft = PromptContextBuilder().build_answer(
            state.get("intent", ""),
            state.get("symbols") or state.get("requested_symbols", []),
            results,
            user_message=state.get("user_message", ""),
            conversation_history=state.get("conversation_history", []),
        )
        return await AnalystAgent().generate(
            draft,
            [item.model_dump(mode="json") for item in results],
            self.sink,
        )

    def sanitize_answer(self, state: AdvisorState) -> dict[str, Any]:
        results = [ToolResult.model_validate(item) for item in state.get("tool_results", [])]
        risk_flags = list(state.get("risk_flags", []))
        if state.get("intent") not in {"GREETING", "OUT_OF_SCOPE"} and not any(item.success for item in results):
            risk_flags.append("INSUFFICIENT_DATA")
        review = RiskManagerAgent().review(
            state.get("final_answer", ""),
            state.get("user_message", ""),
            state.get("intent", ""),
            risk_flags,
        )
        freshness = self._freshness(results)
        return {
            "final_answer": review.answer,
            "risk_flags": self._add_stale_flag(review.risk_flags, freshness),
            "is_safe": review.is_safe,
            "has_disclaimer": review.has_disclaimer,
            "citations": [item.model_dump(mode="json") for item in self._citations(results)],
            "data_freshness": freshness,
            "data_mode": self._data_mode(),
            "thoughts": ["Risk Manager: da ap dung chinh sach an toan."],
        }

    def _initial_state(self, request: ChatRequest, user_id: str, history: list[dict[str, str]]) -> AdvisorState:
        return {
            "user_message": request.message,
            "user_id": user_id,
            "session_id": self.sink.session_id,
            "conversation_history": history,
            "intent": "",
            "symbols": [],
            "requested_symbols": [],
            "requires_portfolio": False,
            "planned_tools": [],
            "tool_results": [],
            "portfolio_context": None,
            "thoughts": [],
            "streaming_tokens": [],
            "risk_flags": [],
            "is_safe": True,
            "has_disclaimer": False,
            "final_answer": "",
            "citations": [],
            "data_mode": self._data_mode(),
            "data_freshness": {},
            "error": None,
        }

    def _tool_input(self, tool_name: str, state: AdvisorState) -> dict[str, Any]:
        if tool_name in {"market_data", "wiki_reader", "news_search", "charting"}:
            return {"symbol": (state.get("symbols") or [""])[0]}
        if tool_name == "portfolio_reader":
            return {"user_id": state["user_id"]}
        if tool_name == "tracked_symbols_reader":
            return {"user_id": state["user_id"]}
        if tool_name == "calculator":
            return self._calculation_input(state["user_message"])
        return {}

    def _calculation_input(self, message: str) -> dict[str, Any]:
        normalized = self._normalized(message)
        numbers = [float(item.replace(",", ".")) for item in re.findall(r"\d+(?:[.,]\d+)?", message)]

        buy = self._number_after(normalized, ["mua", "gia mua"])
        sell = self._number_after(normalized, ["ban", "gia ban"])
        quantity = self._quantity(normalized)
        if buy is not None and sell is not None and quantity is not None:
            return {"operation": "pnl", "quantity": quantity, "buy_price": buy, "sell_price": sell}

        if any(phrase in normalized for phrase in ["phan tram", "ty suat", "return"]) and len(numbers) >= 2:
            return {"operation": "return_pct", "buy_price": numbers[0], "sell_price": numbers[1]}

        if any(phrase in normalized for phrase in ["mua duoc", "so co phieu", "position"]) and len(numbers) >= 2:
            return {"operation": "position_sizing", "budget": numbers[0], "price": numbers[1]}

        if any(phrase in normalized for phrase in ["phi", "thue", "tax", "fee"]) and len(numbers) >= 2:
            side = "sell" if "ban" in normalized else "buy"
            return {"operation": "fee_tax", "quantity": numbers[0], "price": numbers[1], "side": side}

        if len(numbers) >= 3:
            return {"operation": "pnl", "quantity": numbers[0], "buy_price": numbers[1], "sell_price": numbers[2]}
        return {"operation": "pnl"}

    def _normalized(self, value: str) -> str:
        decomposed = unicodedata.normalize("NFD", value or "")
        return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").lower()

    def _number_after(self, message: str, labels: list[str]) -> float | None:
        for label in labels:
            match = re.search(rf"\b{re.escape(label)}\s+(\d+(?:[.,]\d+)?)", message)
            if match:
                return float(match.group(1).replace(",", "."))
        return None

    def _quantity(self, message: str) -> float | None:
        patterns = [
            r"\bvoi\s+(\d+(?:[.,]\d+)?)\s*(?:co|cp|co phieu)?\b",
            r"\b(\d+(?:[.,]\d+)?)\s*(?:co|cp|co phieu)\b",
            r"\bso luong\s+(\d+(?:[.,]\d+)?)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return float(match.group(1).replace(",", "."))
        return None

    def _citations(self, results: list[ToolResult]) -> list[Citation]:
        citations: list[Citation] = []
        seen: set[str] = set()
        for result in results:
            for citation in result.citations:
                if citation.reference not in seen:
                    seen.add(citation.reference)
                    citations.append(citation)
        return citations

    def _freshness(self, results: list[ToolResult]) -> dict[str, str | None]:
        freshness: dict[str, str | None] = {}
        for result in results:
            freshness.update(result.freshness)
        return freshness

    def _add_stale_flag(self, flags: list[str], freshness: dict[str, str | None]) -> list[str]:
        market_updated_at = freshness.get("market_updated_at")
        if market_updated_at:
            try:
                market_date = date.fromisoformat(market_updated_at[:10])
            except ValueError:
                logger.warning("Invalid market_updated_at value: %s", market_updated_at)
                return sorted(set(flags))
            if (date.today() - market_date).days > settings.AI_STALE_AFTER_DAYS:
                flags.append("STALE_DATA")
        return sorted(set(flags))

    def _data_mode(self) -> str:
        return "demo" if settings.AI_DATA_MODE == "demo" else "live"
