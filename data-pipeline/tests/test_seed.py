from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scripts.seed import (
    VN30_SYMBOLS,
    _safe_float,
    _seed_financial_ratios,
    _seed_news_sources,
    _upsert_prices,
    _validate_db_connection,
)


class TestSafeFloat:
    def test_returns_float_for_valid_string(self):
        assert _safe_float("123.45") == 123.45

    def test_returns_float_for_number(self):
        assert _safe_float(99.9) == 99.9

    def test_returns_none_for_none(self):
        assert _safe_float(None) is None

    def test_returns_none_for_empty_string(self):
        assert _safe_float("") is None

    def test_returns_none_for_none_string(self):
        assert _safe_float("None") is None

    def test_returns_none_for_invalid_string(self):
        assert _safe_float("abc") is None


class TestValidateDbConnection:
    def test_returns_true_when_connection_succeeds(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()

        with patch("app.scripts.seed.psycopg2.connect", return_value=mock_conn):
            mock_conn.cursor.return_value = mock_cur

            result = _validate_db_connection()

            assert result is True
            mock_cur.execute.assert_called_once()
            mock_cur.close.assert_called_once()
            mock_conn.close.assert_called_once()

    def test_returns_false_when_connection_fails(self):
        with patch("app.scripts.seed.psycopg2.connect", side_effect=Exception("Connection refused")):
            result = _validate_db_connection()
            assert result is False


class TestUpsertPrices:
    def test_returns_zero_for_empty_rows(self):
        result = _upsert_prices("VNM", [], dry_run=True)
        assert result == 0

    def test_returns_count_in_dry_run(self):
        rows = [
            {"date": "2026-05-30", "close": "95000", "open": "94000", "high": "96000", "low": "93500", "volume": 1000000}
        ]
        result = _upsert_prices("VNM", rows, dry_run=True)
        assert result == 1

    def test_upserts_to_db_when_not_dry_run(self):
        rows = [
            {"date": "2026-05-30", "close": "95000", "open": "94000", "high": "96000", "low": "93500", "volume": 1000000}
        ]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch("app.scripts.seed._get_connection", return_value=mock_conn):
            result = _upsert_prices("VNM", rows, dry_run=False)

        assert result == 1
        assert mock_cur.execute.call_count == 1
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_skips_rows_missing_trade_date_or_close(self):
        rows = [
            {"date": None, "close": "95000"},
            {"date": "2026-05-29", "close": None},
        ]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch("app.scripts.seed._get_connection", return_value=mock_conn):
            result = _upsert_prices("VNM", rows, dry_run=False)

        assert result == 0

    def test_inserts_prices_with_correct_parameters(self):
        rows = [
            {"date": "2026-05-30", "close": "95000", "open": "94000", "high": "96000", "low": "93500", "volume": 1000000}
        ]
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch("app.scripts.seed._get_connection", return_value=mock_conn):
            _upsert_prices("VNM", rows, dry_run=False)

        assert mock_cur.execute.called
        params = mock_cur.execute.call_args[0][1]
        assert params[0] == "VNM"
        assert params[1] == "2026-05-30"


class TestSeedNewsSources:
    def test_dry_run_logs_and_returns(self):
        result = _seed_news_sources(dry_run=True)
        assert result == 3

    def test_inserts_into_db(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch("app.scripts.seed._get_connection", return_value=mock_conn):
            _seed_news_sources(dry_run=False)

        mock_cur.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cur.close.assert_called_once()


class TestSeedFinancialRatios:
    def test_dry_run_returns_true_without_api_call(self):
        with patch("app.scripts.seed.settings") as mock_settings:
            mock_settings.VNSTOCK_API_KEY = "test_key"
            result = _seed_financial_ratios(["VNM"], dry_run=True)
            assert result == {"VNM": True}

    def test_dry_run_returns_false_for_each_symbol(self):
        with patch("app.scripts.seed.settings") as mock_settings:
            mock_settings.VNSTOCK_API_KEY = "test_key"
            result = _seed_financial_ratios(["VNM", "HPG"], dry_run=True)
            assert result == {"VNM": True, "HPG": True}

    def test_inserts_ratios_into_db(self):
        import pandas as pd

        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        mock_df = pd.DataFrame({
            "item": ["P/E", "P/B", "ROE (%)", "ROA (%)"],
            "2024": [20.5, 3.2, 0.18, 0.09],
        })

        mock_finance = MagicMock()
        mock_finance.ratio.return_value = mock_df

        with patch("app.scripts.seed.settings") as mock_settings:
            mock_settings.VNSTOCK_API_KEY = "test_key"

            with patch("vnstock.api.financial.Finance", return_value=mock_finance), \
                 patch("app.scripts.seed._get_connection", return_value=mock_conn):
                result = _seed_financial_ratios(["VNM"], dry_run=False)

                assert result == {"VNM": True}
                mock_conn.commit.assert_called()

    def test_handles_api_error_gracefully(self):
        with patch("app.scripts.seed.settings") as mock_settings:
            mock_settings.VNSTOCK_API_KEY = "test_key"

            with patch("vnstock.api.financial.Finance", side_effect=Exception("Network error")):
                result = _seed_financial_ratios(["VNM"], dry_run=False)

                assert result == {"VNM": False}


class TestVn30Symbols:
    def test_contains_no_duplicates(self):
        assert len(VN30_SYMBOLS) == len(set(VN30_SYMBOLS))

    def test_contains_known_symbols(self):
        for sym in ["VNM", "VCB", "HPG", "SSI", "TCB"]:
            assert sym in VN30_SYMBOLS

    def test_all_are_non_empty_strings(self):
        assert all(isinstance(s, str) and len(s) > 0 for s in VN30_SYMBOLS)

    def test_default_list_count(self):
        assert len(VN30_SYMBOLS) >= 30


class TestSeedPricesVnstock:
    def test_skips_empty_dataframe_result(self):
        """When vnstock returns empty df, _seed_prices returns 0 count for that symbol."""
        import app.scripts.seed as seed_mod

        mock_df = MagicMock()
        mock_df.empty = True
        mock_df.tail.return_value = mock_df

        mock_vn = MagicMock()
        mock_vn.stock.price_historical.return_value = mock_df

        with patch.dict("sys.modules", {"vnstock": mock_vn}):
            with patch("app.scripts.seed._upsert_prices", return_value=0) as mock_up:
                import importlib
                importlib.reload(seed_mod)
                result = seed_mod._seed_prices(["VNM"], dry_run=False)
                assert result["VNM"] == 0
