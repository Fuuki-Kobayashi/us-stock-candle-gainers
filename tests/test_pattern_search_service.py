"""Tests for pattern search service."""

from unittest.mock import patch

import pytest
from app.services.pattern_search_service import search_patterns

from app.models.candle import CandleData, PatternResult


def _make_candle(open_: float, high: float, low: float, close: float) -> CandleData:
    """Create test candle data."""
    return CandleData(
        date="2024-01-01",
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=1000000,
    )


def _make_pattern(
    name: str, pattern_id: str, direction: str = "bullish"
) -> PatternResult:
    """Create test pattern result."""
    return PatternResult(
        type="confirmed",
        name=name,
        pattern_id=pattern_id,
        signal="test signal",
        description="test",
        direction=direction,
        pattern_candle_count=3,
    )


class TestSearchPatterns:
    """Unit-03: Pattern search service tests."""

    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    def test_matching_patterns_only(self, mock_sd, mock_pd):
        """Only patterns matching pattern_ids should be returned."""
        candles = [_make_candle(100, 110, 90, 105), _make_candle(105, 115, 95, 110)]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 5.0)
        mock_pd.detect_patterns.return_value = [
            _make_pattern("明けの明星", "morning_star"),
            _make_pattern("赤三兵", "three_red_soldiers"),
        ]

        results = search_patterns(["AAPL"], ["morning_star"])
        assert len(results) == 1
        assert len(results[0].patterns) == 1
        assert results[0].patterns[0].pattern_id == "morning_star"

    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    def test_exclude_no_match_tickers(self, mock_sd, mock_pd):
        """Tickers with 0 matching patterns should be excluded."""
        candles = [_make_candle(100, 110, 90, 105), _make_candle(105, 115, 95, 110)]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 5.0)
        mock_pd.detect_patterns.return_value = [
            _make_pattern("赤三兵", "three_red_soldiers"),
        ]

        results = search_patterns(["AAPL"], ["morning_star"])
        assert len(results) == 0  # No match, excluded

    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    def test_include_error_tickers(self, mock_sd, mock_pd):
        """Error tickers should be included in results."""
        from app.exceptions import TickerNotFoundError

        mock_sd.validate_ticker.side_effect = TickerNotFoundError("INVALID")

        results = search_patterns(["INVALID"], ["morning_star"])
        assert len(results) == 1
        assert results[0].error is not None
        assert results[0].ticker == "INVALID"

    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    def test_change_pct_calculation(self, mock_sd, mock_pd):
        """change_pct should be calculated correctly."""
        candles = [_make_candle(100, 110, 90, 100), _make_candle(100, 115, 95, 110)]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 5.0)
        mock_pd.detect_patterns.return_value = [
            _make_pattern("明けの明星", "morning_star"),
        ]

        results = search_patterns(["AAPL"], ["morning_star"])
        assert results[0].change_pct == pytest.approx(10.0)

    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    def test_response_counts(self, mock_sd, mock_pd):
        """Test with multiple tickers - mixed results."""
        candles = [_make_candle(100, 110, 90, 105), _make_candle(105, 115, 95, 110)]

        def mock_validate(ticker):
            if ticker == "FAIL":
                from app.exceptions import TickerNotFoundError

                raise TickerNotFoundError(ticker)

        def mock_get_ohlcv(ticker, count, confirmed_only=False):
            return (candles, 5.0)

        mock_sd.validate_ticker.side_effect = mock_validate
        mock_sd.get_ohlcv.side_effect = mock_get_ohlcv
        mock_pd.detect_patterns.return_value = [
            _make_pattern("明けの明星", "morning_star"),
        ]

        results = search_patterns(["AAPL", "FAIL", "TSLA"], ["morning_star"])
        # AAPL: match, FAIL: error, TSLA: match
        matched = [r for r in results if r.error is None]
        errors = [r for r in results if r.error is not None]
        assert len(matched) == 2
        assert len(errors) == 1

    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    def test_candle_count_2_mode(self, mock_sd, mock_pd):
        """candle_count=2 should use realdata_2candle mode."""
        candles = [_make_candle(100, 110, 90, 105), _make_candle(105, 115, 95, 110)]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 5.0)
        mock_pd.detect_patterns.return_value = [
            _make_pattern("包み線", "bullish_engulfing"),
        ]

        search_patterns(["AAPL"], ["bullish_engulfing"], candle_count=2)
        mock_pd.detect_patterns.assert_called_once_with(
            candles, mode="realdata_2candle"
        )
