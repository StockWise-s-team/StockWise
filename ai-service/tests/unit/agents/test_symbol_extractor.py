import pytest

from app.agents.symbol_extractor import (
    extract_symbols_regex,
    extract_symbols_aliases,
    _IGNORED_SYMBOLS,
)


class TestSymbolExtractorRegex:
    """Unit tests for regex-based symbol extraction."""

    def test_extract_single_symbol(self):
        """Extracts a single uppercase symbol."""
        result = extract_symbols_regex("Đánh giá FPT hôm nay")
        assert result == ["FPT"]

    def test_extract_multiple_symbols(self):
        """Extracts multiple symbols from text."""
        result = extract_symbols_regex("So sánh FPT và VIC")
        assert set(result) == {"FPT", "VIC"}

    def test_ignores_common_abbreviations(self):
        """Ignores abbreviations in the ignore list."""
        result = extract_symbols_regex("EPS của FPT là bao nhiêu")
        assert "EPS" not in result
        assert "FPT" in result

    def test_case_insensitive(self):
        """Handles lowercase input by converting to uppercase."""
        result = extract_symbols_regex("đánh giá fpt hôm nay")
        assert "FPT" in result

    def test_no_symbols_returns_empty(self):
        """Returns empty list when no symbols found."""
        result = extract_symbols_regex("thị trường hôm nay thế nào")
        assert result == []

    def test_ignores_single_letters(self):
        """Ignores single letter tokens."""
        result = extract_symbols_regex("A B C FPT")
        assert result == ["FPT"]

    def test_ignores_too_long_tokens(self):
        """Ignores tokens longer than 5 characters."""
        result = extract_symbols_regex("FPT ABCDEF")
        assert "ABCDEF" not in result


class TestSymbolExtractorAliases:
    """Unit tests for alias-based symbol extraction."""

    def test_match_vingroup(self):
        """Matches Vingroup alias to VIC."""
        result = extract_symbols_aliases("Vingroup hôm nay thế nào")
        assert "VIC" in result

    def test_match_hoa_phat(self):
        """Matches Hòa Phát alias to HPG."""
        result = extract_symbols_aliases("Cổ phiếu Hòa Phát có tốt không")
        assert "HPG" in result

    def test_match_vietcombank(self):
        """Matches Vietcombank alias to VCB."""
        result = extract_symbols_aliases("VCB hay Vietcombank đều được")
        assert "VCB" in result

    def test_no_alias_match(self):
        """Returns empty when no aliases match."""
        result = extract_symbols_aliases("thị trường hôm nay")
        assert result == []

    def test_multiple_alias_matches(self):
        """Matches multiple symbols from aliases."""
        result = extract_symbols_aliases("Vingroup và FPT cùng tăng")
        assert "VIC" in result
        assert "FPT" in result
