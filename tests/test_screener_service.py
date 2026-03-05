"""Unit-03: screener_service.scan_tickers tests (12 tests)."""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.candle import CandleData, PatternResult


def _make_candles(
    close_prev: float = 100.0, close_last: float = 105.0
) -> list[CandleData]:
    """Create a minimal 3-candle list for testing."""
    return [
        CandleData(
            date="2024-01-10", open=98.0, high=102.0, low=97.0, close=99.0, volume=100
        ),
        CandleData(
            date="2024-01-11",
            open=99.0,
            high=close_prev + 2,
            low=98.0,
            close=close_prev,
            volume=100,
        ),
        CandleData(
            date="2024-01-12",
            open=close_prev,
            high=close_last + 2,
            low=close_prev - 1,
            close=close_last,
            volume=100,
        ),
    ]


def _make_candles_2(
    close_prev: float = 100.0, close_last: float = 105.0
) -> list[CandleData]:
    """Create a minimal 2-candle list for testing."""
    return [
        CandleData(
            date="2024-01-11",
            open=99.0,
            high=close_prev + 2,
            low=98.0,
            close=close_prev,
            volume=100,
        ),
        CandleData(
            date="2024-01-12",
            open=close_prev,
            high=close_last + 2,
            low=close_prev - 1,
            close=close_last,
            volume=100,
        ),
    ]


def _make_pattern() -> PatternResult:
    return PatternResult(
        type="confirmed",
        name="テストパターン",
        signal="🔼 強気シグナル",
        description="テスト",
        direction="bullish",
        pattern_candle_count=2,
    )


class TestScanTickers:
    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_single_valid_ticker(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles(100.0, 105.0)
        patterns = [_make_pattern()]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.5)
        mock_pd.detect_patterns.return_value = patterns

        results = scan_tickers(["AAPL"])
        assert len(results) == 1
        assert results[0].ticker == "AAPL"
        assert results[0].candles == candles
        assert results[0].patterns == patterns
        assert results[0].change_pct is not None
        assert results[0].error is None

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_multiple_tickers(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles()
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        results = scan_tickers(["AAPL", "MSFT", "GOOGL"])
        assert len(results) == 3
        assert results[0].ticker == "AAPL"
        assert results[1].ticker == "MSFT"
        assert results[2].ticker == "GOOGL"

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_invalid_ticker_continues(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles()

        def validate_side_effect(ticker: str) -> None:
            if ticker == "INVALID":
                raise TickerNotFoundError(ticker)

        mock_sd.validate_ticker.side_effect = validate_side_effect
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        results = scan_tickers(["AAPL", "INVALID", "MSFT"])
        assert len(results) == 3
        assert results[0].error is None
        assert results[1].error is not None
        assert results[2].error is None

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_ticker_not_found_error(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        mock_sd.validate_ticker.side_effect = TickerNotFoundError("XYZ")

        results = scan_tickers(["XYZ"])
        assert len(results) == 1
        assert results[0].error is not None
        assert "XYZ" in results[0].error

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_ticker_not_equity_error(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        mock_sd.validate_ticker.side_effect = TickerNotEquityError("SPY", "ETF")

        results = scan_tickers(["SPY"])
        assert len(results) == 1
        assert results[0].error is not None
        assert "SPY" in results[0].error

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_data_fetch_error(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.side_effect = DataFetchError("timeout")

        results = scan_tickers(["AAPL"])
        assert len(results) == 1
        assert results[0].error is not None

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_scan_unexpected_exception(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.side_effect = RuntimeError("something unexpected")

        results = scan_tickers(["AAPL"])
        assert len(results) == 1
        assert results[0].error is not None

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_change_pct_calculation(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles(close_prev=100.0, close_last=105.0)
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        results = scan_tickers(["AAPL"])
        # change_pct = (105 - 100) / 100 * 100 = 5.0
        assert results[0].change_pct == pytest.approx(5.0)

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_change_pct_with_candle_count_2(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles_2(close_prev=200.0, close_last=190.0)
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 1.5)
        mock_pd.detect_patterns.return_value = []

        results = scan_tickers(["AAPL"], candle_count=2)
        # change_pct = (190 - 200) / 200 * 100 = -5.0
        assert results[0].change_pct == pytest.approx(-5.0)

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_all_tickers_error(self, mock_sd: MagicMock, mock_pd: MagicMock) -> None:
        from app.services.screener_service import scan_tickers

        mock_sd.validate_ticker.side_effect = TickerNotFoundError("BAD")

        results = scan_tickers(["BAD1", "BAD2", "BAD3"])
        assert len(results) == 3
        assert all(r.error is not None for r in results)

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_detect_patterns_mode_realdata(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles()
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        scan_tickers(["AAPL"], candle_count=3)
        mock_pd.detect_patterns.assert_called_with(candles, mode="realdata")

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    def test_detect_patterns_mode_realdata_2candle(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.services.screener_service import scan_tickers

        candles = _make_candles_2()
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 1.5)
        mock_pd.detect_patterns.return_value = []

        scan_tickers(["AAPL"], candle_count=2)
        mock_pd.detect_patterns.assert_called_with(candles, mode="realdata_2candle")
