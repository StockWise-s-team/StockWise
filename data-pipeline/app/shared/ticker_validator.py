"""Shared ticker validation against the canonical valid_tickers.json list."""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_VALID_TICKERS: set[str] | None = None  # None = not yet loaded


def _get_tickers_path() -> Path:
    # __file__ = .../app/shared/ticker_validator.py
    # parent.parent = .../app
    # parent.parent.parent = .../data-pipeline
    return Path(__file__).parent.parent.parent / "valid_tickers.json"


def load_valid_tickers() -> set[str]:
    global _VALID_TICKERS
    if _VALID_TICKERS is not None:
        return _VALID_TICKERS

    path = _get_tickers_path()
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                _VALID_TICKERS = set(json.load(f))
            logger.info("[TickerValidator] Loaded %d valid tickers from %s", len(_VALID_TICKERS), path)
        except Exception as exc:
            logger.warning("[TickerValidator] Failed to load %s: %s — ticker filter disabled", path, exc)
            _VALID_TICKERS = set()
    else:
        logger.warning("[TickerValidator] valid_tickers.json not found at %s — ticker filter disabled", path)
        _VALID_TICKERS = set()

    return _VALID_TICKERS


def is_valid_ticker(symbol: str) -> bool:
    """Return True if the given symbol is in the canonical ticker list."""
    if not symbol:
        return False
    tickers = load_valid_tickers()
    if not tickers:
        return True  # No filter available, allow all
    return symbol.upper() in tickers
