"""Unit tests for stock_data service. All yfinance calls are mocked."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.candle import ShortInterest
from app.services.stock_data import (
    get_financial_info,
    get_latest_close,
    get_ohlcv,
    get_short_interest,
    validate_ticker,
)


def _make_history_df(rows: int = 5) -> pd.DataFrame:
    """Helper to create a realistic OHLCV DataFrame."""
    dates = pd.date_range("2026-02-25", periods=rows, freq="B")
    data = {
        "Open": [100.0 + i for i in range(rows)],
        "High": [105.0 + i for i in range(rows)],
        "Low": [95.0 + i for i in range(rows)],
        "Close": [102.0 + i for i in range(rows)],
        "Volume": [1000000 + i * 100000 for i in range(rows)],
    }
    return pd.DataFrame(data, index=dates)


# Unit-01: get_ohlcv returns 3 candles and ATR as float
@patch("app.services.stock_data.yf")
def test_get_ohlcv_returns_three_candles_and_atr(mock_yf: MagicMock) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    # history(period="5d") for candles, history(period="1mo") for ATR
    mock_ticker.history.side_effect = [
        _make_history_df(5),  # 5d -> last 3 rows
        _make_history_df(20),  # 1mo -> ATR(14)
    ]

    candles, atr = get_ohlcv("AAPL")

    assert len(candles) == 3
    assert isinstance(atr, float)


# Unit-02: Each candle has complete fields with correct types
@patch("app.services.stock_data.yf")
def test_get_ohlcv_candle_fields_complete(mock_yf: MagicMock) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.history.side_effect = [
        _make_history_df(5),
        _make_history_df(20),
    ]

    candles, _ = get_ohlcv("AAPL")

    for candle in candles:
        assert isinstance(candle.date, str)
        assert isinstance(candle.open, float)
        assert isinstance(candle.high, float)
        assert isinstance(candle.low, float)
        assert isinstance(candle.close, float)
        assert isinstance(candle.volume, int)


# Unit-03: get_short_interest returns ShortInterest when data available
@patch("app.services.stock_data.yf")
def test_get_short_interest_returns_data(mock_yf: MagicMock) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = {
        "shortPercentOfFloat": 0.05,
        "shortRatio": 2.5,
        "sharesShort": 5000000,
        "sharesShortPriorMonth": 4500000,
    }

    result = get_short_interest("AAPL")

    assert isinstance(result, ShortInterest)
    assert result.short_percent_of_float == 5.0
    assert result.short_ratio == 2.5
    assert result.shares_short == 5000000
    assert result.shares_short_prior_month == 4500000


# Unit-04: get_short_interest returns None when data unavailable
@patch("app.services.stock_data.yf")
def test_get_short_interest_returns_none_when_unavailable(
    mock_yf: MagicMock,
) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = {"quoteType": "EQUITY"}

    result = get_short_interest("AAPL")

    assert result is None


# Unit-05: validate_ticker with empty/invalid ticker raises TickerNotFoundError
@patch("app.services.stock_data.yf")
def test_validate_ticker_empty_raises_error(mock_yf: MagicMock) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = {}  # No quoteType

    with pytest.raises(TickerNotFoundError):
        validate_ticker("")


# Unit-06: validate_ticker with non-EQUITY raises TickerNotEquityError
@patch("app.services.stock_data.yf")
def test_validate_ticker_not_equity_raises_error(mock_yf: MagicMock) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = {"quoteType": "ETF"}

    with pytest.raises(TickerNotEquityError) as exc_info:
        validate_ticker("SPY")

    assert exc_info.value.ticker == "SPY"
    assert exc_info.value.quote_type == "ETF"


# Unit-07: get_financial_info with invalid ticker raises TickerNotFoundError
@patch("app.services.stock_data.yf")
def test_get_financial_info_invalid_ticker_raises_error(
    mock_yf: MagicMock,
) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = {}  # No quoteType

    with pytest.raises(TickerNotFoundError):
        get_financial_info("INVALID")


# Unit-08: get_ohlcv wraps network errors in DataFetchError
@patch("app.services.stock_data.yf")
def test_get_ohlcv_network_error_raises_data_fetch_error(
    mock_yf: MagicMock,
) -> None:
    mock_yf.Ticker.side_effect = Exception("Network error")

    with pytest.raises(DataFetchError):
        get_ohlcv("AAPL")


# Unit-09: get_latest_close returns float
@patch("app.services.stock_data.yf")
def test_get_latest_close_returns_float(mock_yf: MagicMock) -> None:
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.history.return_value = _make_history_df(5)

    result = get_latest_close("AAPL")

    assert isinstance(result, float)
    # Last row Close = 102.0 + 4 = 106.0
    assert result == 106.0
