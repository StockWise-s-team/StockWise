import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import (
    StockWiseAIException,
    LLMUnavailableError,
    ToolExecutionError,
    SymbolNotFoundError,
    DataUnavailableError,
    SafetyViolationError,
)
from app.core.error_handler import register_error_handlers
from fastapi import FastAPI


class TestErrorHandlers:
    """Unit tests for global error handlers."""

    @pytest.fixture
    def app(self):
        """Create test app with error handlers registered."""
        test_app = FastAPI()
        register_error_handlers(test_app)

        @test_app.get("/raise/stockwise")
        async def raise_stockwise():
            raise StockWiseAIException("General error")

        @test_app.get("/raise/llm")
        async def raise_llm():
            raise LLMUnavailableError("Gemini down")

        @test_app.get("/raise/tool")
        async def raise_tool():
            raise ToolExecutionError("wiki_reader", "DB connection lost")

        @test_app.get("/raise/symbol")
        async def raise_symbol():
            raise SymbolNotFoundError("Symbol XYZ not found")

        @test_app.get("/raise/data")
        async def raise_data():
            raise DataUnavailableError("Data is stale")

        @test_app.get("/raise/safety")
        async def raise_safety():
            raise SafetyViolationError("Buy recommendation detected")

        return test_app

    def test_stockwise_exception(self, app):
        """StockWiseAIException returns 500."""
        client = TestClient(app)
        response = client.get("/raise/stockwise")
        assert response.status_code == 500
        assert response.json()["error"] == "StockWiseAIException"

    def test_llm_unavailable(self, app):
        """LLMUnavailableError returns 503."""
        client = TestClient(app)
        response = client.get("/raise/llm")
        assert response.status_code == 503
        assert response.json()["error"] == "LLM_UNAVAILABLE"

    def test_tool_execution_error(self, app):
        """ToolExecutionError returns 500 with tool name."""
        client = TestClient(app)
        response = client.get("/raise/tool")
        assert response.status_code == 500
        assert response.json()["error"] == "TOOL_FAILED"

    def test_symbol_not_found(self, app):
        """SymbolNotFoundError returns 404."""
        client = TestClient(app)
        response = client.get("/raise/symbol")
        assert response.status_code == 404
        assert response.json()["error"] == "SYMBOL_NOT_FOUND"

    def test_data_unavailable(self, app):
        """DataUnavailableError returns 503."""
        client = TestClient(app)
        response = client.get("/raise/data")
        assert response.status_code == 503
        assert response.json()["error"] == "DATA_UNAVAILABLE"

    def test_safety_violation(self, app):
        """SafetyViolationError returns 400."""
        client = TestClient(app)
        response = client.get("/raise/safety")
        assert response.status_code == 400
        assert response.json()["error"] == "SAFETY_VIOLATION"
