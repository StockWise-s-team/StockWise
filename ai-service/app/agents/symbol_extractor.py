import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


_SYMBOL_ALIASES: dict[str, list[str]] | None = None
_IGNORED_SYMBOLS = {
    "AI", "CEO", "EPS", "PE", "PB", "ROE", "ROA", "RSI", "MACD", "OK", "US", "UK",
    "NAY", "SO", "VA", "CO", "KHONG", "KHONG", "DAU", "TANG", "GIAM", "MUA", "BAN",
    "HOI", "TUC", "PHI", "TAY", "BAC", "NAM", "DONG", "TAY", "TRUNG", "CAO", "THAP",
    "MOI", "CU", "MOI", "THE", "CHO", "PHI", "TIN", "TUC", "THI", "TRUONG",
}


def _load_aliases() -> dict[str, list[str]]:
    """Load symbol aliases from JSON file."""
    global _SYMBOL_ALIASES
    if _SYMBOL_ALIASES is None:
        alias_path = Path(__file__).parent.parent / "data" / "symbol_aliases.json"
        with open(alias_path, "r", encoding="utf-8") as f:
            _SYMBOL_ALIASES = json.load(f)
    return _SYMBOL_ALIASES


def extract_symbols_regex(text: str) -> list[str]:
    """Extract potential stock symbols using regex pattern.

    Args:
        text: User message text.

    Returns:
        List of uppercase 2-5 letter candidates.
    """
    candidates = re.findall(r"\b([A-Z]{2,5})\b", text.upper())
    return [c for c in candidates if c not in _IGNORED_SYMBOLS]


def extract_symbols_aliases(text: str) -> list[str]:
    """Extract symbols by matching company name aliases.

    Args:
        text: User message text.

    Returns:
        List of matched stock symbols.
    """
    aliases = _load_aliases()
    matched = []
    text_lower = text.lower()
    for symbol, alias_list in aliases.items():
        for alias in alias_list:
            if alias.lower() in text_lower:
                matched.append(symbol)
                break
    return list(set(matched))


async def validate_symbols(symbols: list[str], session: AsyncSession) -> list[str]:
    """Validate symbols against the database.

    Args:
        symbols: List of candidate symbols.
        session: Async SQLAlchemy session.

    Returns:
        List of symbols that exist in stock_prices table.
    """
    if not symbols:
        return []

    from sqlalchemy import text

    placeholders = ", ".join(f":sym_{i}" for i in range(len(symbols)))
    query = text(f"SELECT DISTINCT symbol FROM stock_prices WHERE symbol IN ({placeholders})")
    params = {f"sym_{i}": sym.upper() for i, sym in enumerate(symbols)}

    result = await session.execute(query, params)
    valid = [row[0] for row in result.fetchall()]
    return valid


async def extract_symbols(text: str, session: AsyncSession) -> list[str]:
    """Full symbol extraction pipeline: regex + aliases + DB validation.

    Args:
        text: User message text.
        session: Async SQLAlchemy session.

    Returns:
        List of validated stock symbols found in the message.
    """
    regex_symbols = extract_symbols_regex(text)
    alias_symbols = extract_symbols_aliases(text)
    candidates = list(set(regex_symbols + alias_symbols))
    return await validate_symbols(candidates, session)
