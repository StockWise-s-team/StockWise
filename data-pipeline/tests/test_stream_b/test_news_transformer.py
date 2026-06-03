import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.stream_b.transformers.news_transformer import NewsTransformer
from app.stream_b.exceptions import SourceMapError, TransformError


class TestStripHtml:
    def test_strips_all_tags(self):
        t = NewsTransformer()
        html = "<p>Hello <strong>World</strong></p>"
        assert t._strip_html(html) == "Hello World"

    def test_preserves_text_spacing(self):
        t = NewsTransformer()
        html = "<p>First</p><p>Second</p>"
        assert "First" in t._strip_html(html)
        assert "Second" in t._strip_html(html)

    def test_removes_scripts_and_styles(self):
        t = NewsTransformer()
        html = "<script>alert('x')</script><p>Text</p><style>.c{color:red}</style>"
        assert "alert" not in t._strip_html(html)
        assert "Text" in t._strip_html(html)

    def test_removes_nav_header_footer(self):
        t = NewsTransformer()
        html = (
            "<nav>NavContent</nav>"
            "<p>Body</p>"
            "<header>HeaderContent</header>"
            "<footer>FooterContent</footer>"
        )
        result = t._strip_html(html)
        assert "NavContent" not in result
        assert "HeaderContent" not in result
        assert "FooterContent" not in result
        assert "Body" in result

    def test_empty_string_returns_empty(self):
        t = NewsTransformer()
        assert t._strip_html("") == ""
        assert t._strip_html(None) == ""

    def test_multiple_whitespace_collapsed(self):
        t = NewsTransformer()
        html = "<p>Hello    World</p>"
        assert "  " not in t._strip_html(html)


class TestExtractSymbols:
    def test_extracts_simple_3char_symbols(self):
        t = NewsTransformer()
        text = "VNM HPG FPT are all up today."
        symbols = t._extract_symbols(text)
        assert "VNM" in symbols
        assert "HPG" in symbols
        assert "FPT" in symbols

    def test_extracts_4char_symbols(self):
        t = NewsTransformer()
        text = "VN30 index includes ACB and EIB."
        symbols = t._extract_symbols(text)
        assert "ACB" in symbols
        assert "EIB" in symbols

    def test_extracts_dot_vn_suffix(self):
        t = NewsTransformer()
        text = "VNM.VN and HPG.VN rally."
        symbols = t._extract_symbols(text)
        assert "VNM" in symbols
        assert "HPG" in symbols

    def test_extracts_colon_suffix(self):
        t = NewsTransformer()
        text = "ACB:VN and BID:BC."
        symbols = t._extract_symbols(text)
        assert "ACB" in symbols
        assert "BID" in symbols

    def test_deduplicates(self):
        t = NewsTransformer()
        text = "VNM VNM VNM reported results."
        symbols = t._extract_symbols(text)
        assert symbols.count("VNM") == 1

    def test_filters_common_words(self):
        t = NewsTransformer()
        text = "THE AND FOR THIS THAT WITH HAVE HAS NOT ARE WERE."
        symbols = t._extract_symbols(text)
        assert "THE" not in symbols
        assert "AND" not in symbols

    def test_filters_vnindex_hsx_hnx(self):
        t = NewsTransformer()
        text = "VNIndex VN30 HNX HSX are all up."
        symbols = t._extract_symbols(text)
        assert "VNINDEX" not in symbols
        assert "VN30" not in symbols
        assert "HNX" not in symbols
        assert "HSX" not in symbols

    def test_case_insensitive(self):
        t = NewsTransformer()
        text = "vnm and hpg reported."
        symbols = t._extract_symbols(text)
        assert "VNM" in symbols
        assert "HPG" in symbols

    def test_empty_text(self):
        t = NewsTransformer()
        assert t._extract_symbols("") == []
        assert t._extract_symbols("No symbols here.") == []

    def test_vnd_ticker_not_filtered_by_currency_code(self):
        """
        VND is a valid stock ticker (VNDIRECT Securities) in valid_tickers.json.
        It must NOT be filtered out by the CURRENCY_CODES exclusion,
        which is meant only for the VND currency abbreviation.
        """
        t = NewsTransformer()
        text = "VND reported net profit of 2,508 billion VND in 2025."
        symbols = t._extract_symbols(text)
        assert "VND" in symbols, "VND ticker should be extracted despite being in CURRENCY_CODES"

    def test_other_currency_codes_still_filtered(self):
        """
        Currency codes not in valid_tickers.json are filtered out by is_valid_ticker.
        The CURRENCY_CODES set is a safety net for symbols that pass ticker
        validation but are known currencies (only relevant if they appear in
        valid_tickers.json by mistake).
        """
        t = NewsTransformer()
        # EUR is not a stock ticker — not in valid_tickers.json
        # so is_valid_ticker returns False before CURRENCY_CODES is reached.
        text = "Stock surged 5% to 100 EUR per share."
        symbols = t._extract_symbols(text)
        assert "EUR" not in symbols

    def test_vnd_mixed_with_real_currency_context(self):
        """
        When VND appears in a context that clearly means currency (e.g. '100 VND'),
        it should still be extracted as ticker because it IS a valid ticker
        in the canonical list. The CURRENCY_CODES filter should not override
        the explicit valid_tickers.json list.
        """
        t = NewsTransformer()
        text = "Công ty Cổ phần Chứng khoán VNDIRECT (VND) đạt lợi nhuận 2,508 tỷ đồng, tăng 20.1%."
        symbols = t._extract_symbols(text)
        assert "VND" in symbols


class TestTransform:
    def test_transform_single_article(
        self, sample_cafef_article, mock_source_row
    ):
        with patch.object(
            NewsTransformer, "_resolve_source_id", return_value=mock_source_row[0]
        ):
            t = NewsTransformer()
            result = t.transform(sample_cafef_article)

        assert result.title == sample_cafef_article["title"]
        assert result.url == sample_cafef_article["url"]
        assert result.source_id == str(mock_source_row[0])
        assert result.crawled_at is not None

    def test_transform_strips_html_in_content(self, sample_cafef_article, mock_source_row):
        with patch.object(
            NewsTransformer, "_resolve_source_id", return_value=mock_source_row[0]
        ):
            t = NewsTransformer()
            result = t.transform(sample_cafef_article)
        assert "<p>" not in result.content
        assert "VNM" in result.content

    def test_transform_list(self, sample_cafef_article, sample_vietstock_article, mock_source_row):
        with patch.object(
            NewsTransformer, "_resolve_source_id", return_value=mock_source_row[0]
        ):
            t = NewsTransformer()
            results = t.transform([sample_cafef_article, sample_vietstock_article])
        assert len(results) == 2
        assert all(hasattr(r, "title") for r in results)

    def test_transform_extracts_symbols_from_content(
        self, sample_cafef_article, mock_source_row
    ):
        with patch.object(
            NewsTransformer, "_resolve_source_id", return_value=mock_source_row[0]
        ):
            t = NewsTransformer()
            result = t.transform(sample_cafef_article)
        assert len(result.symbols) > 0

    def test_transform_prefers_direct_symbols(self, mock_source_row):
        """When crawler provides symbols directly, those are used."""
        article = {
            "title": "Direct symbol test",
            "content": "<p>Content mentions VPB and HPG in text.</p>",
            "excerpt": "",
            "url": "https://cafef.vn/test.chn",
            "published_at": "2026-06-01T10:00:00Z",
            "symbols": ["ACB", "FPT"],  # crawler-provided
            "source_name": "cafef",
        }
        with patch.object(
            NewsTransformer, "_resolve_source_id", return_value=mock_source_row[0]
        ):
            t = NewsTransformer()
            result = t.transform(article)
        # Should use the crawler's symbols, not the ones from text
        assert set(result.symbols) == {"ACB", "FPT"}

    def test_transform_raises_on_missing_source(
        self, sample_cafef_article
    ):
        with patch.object(NewsTransformer, "_resolve_source_id", side_effect=SourceMapError("cafef")):
            t = NewsTransformer()
            with pytest.raises(TransformError):
                t.transform(sample_cafef_article)


class TestParsePublishedAt:
    def test_parses_iso_string(self):
        result = NewsTransformer._parse_published_at("2026-05-28T10:00:00+07:00")
        assert result is not None
        assert result.year == 2026

    def test_parses_datetime(self):
        dt = datetime(2026, 5, 28, tzinfo=timezone.utc)
        result = NewsTransformer._parse_published_at(dt)
        assert result == dt

    def test_returns_none_for_empty(self):
        assert NewsTransformer._parse_published_at(None) is None
        assert NewsTransformer._parse_published_at("") is None

    def test_returns_none_for_invalid(self):
        assert NewsTransformer._parse_published_at("not-a-date") is None
