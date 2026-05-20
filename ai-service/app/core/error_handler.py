import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    StockWiseAIException,
    LLMUnavailableError,
    ToolExecutionError,
    SymbolNotFoundError,
    DataUnavailableError,
    SafetyViolationError,
)

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI app."""

    @app.exception_handler(StockWiseAIException)
    async def stockwise_ai_exception_handler(request: Request, exc: StockWiseAIException) -> JSONResponse:
        logger.error(
            "StockWiseAIException: %s",
            str(exc),
            extra={"exception_type": type(exc).__name__},
        )
        return JSONResponse(
            status_code=500,
            content={"error": type(exc).__name__, "message": str(exc)},
        )

    @app.exception_handler(LLMUnavailableError)
    async def llm_unavailable_handler(request: Request, exc: LLMUnavailableError) -> JSONResponse:
        logger.error("LLM unavailable: %s", str(exc))
        return JSONResponse(
            status_code=503,
            content={"error": "LLM_UNAVAILABLE", "message": "AI service is temporarily unavailable."},
        )

    @app.exception_handler(ToolExecutionError)
    async def tool_execution_handler(request: Request, exc: ToolExecutionError) -> JSONResponse:
        logger.warning("Tool execution error: %s", str(exc))
        return JSONResponse(
            status_code=500,
            content={"error": "TOOL_FAILED", "message": f"Tool '{exc.tool_name}' failed."},
        )

    @app.exception_handler(SymbolNotFoundError)
    async def symbol_not_found_handler(request: Request, exc: SymbolNotFoundError) -> JSONResponse:
        logger.info("Symbol not found: %s", str(exc))
        return JSONResponse(
            status_code=404,
            content={"error": "SYMBOL_NOT_FOUND", "message": str(exc)},
        )

    @app.exception_handler(DataUnavailableError)
    async def data_unavailable_handler(request: Request, exc: DataUnavailableError) -> JSONResponse:
        logger.warning("Data unavailable: %s", str(exc))
        return JSONResponse(
            status_code=503,
            content={"error": "DATA_UNAVAILABLE", "message": str(exc)},
        )

    @app.exception_handler(SafetyViolationError)
    async def safety_violation_handler(request: Request, exc: SafetyViolationError) -> JSONResponse:
        logger.error("Safety violation: %s", str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": "SAFETY_VIOLATION", "message": "Response blocked due to safety policy."},
        )
