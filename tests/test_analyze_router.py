"""Integration tests for the analyze router (POST /analyze).

These tests mock yfinance at the service level (app.services.stock_data.yf)
and test through the full HTTP layer using httpx AsyncClient.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_history_df() -> pd.DataFrame:
    """5-day OHLCV DataFrame mimicking yfinance Ticker.history() output."""
    data = {
        "Open": [148.0, 150.0, 149.5, 151.0, 152.0],
        "High": [152.0, 153.0, 151.0, 154.0, 155.0],
        "Low": [147.0, 149.0, 148.5, 150.0, 151.0],
        "Close": [150.0, 149.5, 150.5, 153.0, 154.0],
        "Volume": [1000000, 1200000, 900000, 1100000, 1300000],
    }
    index = pd.date_range("2024-01-10", periods=5, freq="B")
    return pd.DataFrame(data, index=index)


@pytest.fixture
def mock_history_1mo_df() -> pd.DataFrame:
    """1-month DataFrame for ATR calculation (22 rows)."""
    n = 22
    data = {
        "Open": [150.0] * n,
        "High": [155.0] * n,
        "Low": [145.0] * n,
        "Close": [152.0] * n,
        "Volume": [1000000] * n,
    }
    index = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame(data, index=index)


@pytest.fixture
def valid_equity_info() -> dict:
    """yfinance info dict for a valid EQUITY with all required fields."""
    return {
        "quoteType": "EQUITY",
        "shortName": "Apple Inc.",
        "symbol": "AAPL",
        "shortPercentOfFloat": 0.75,
        "shortRatio": 1.2,
        "sharesShort": 120000000,
        "sharesShortPriorMonth": 115000000,
        "debtToEquity": 150.0,
        "currentRatio": 1.8,
        "profitMargins": 0.21,
        "freeCashflow": 90000000000,
        "totalCash": 50000000000,
        "totalDebt": 30000000000,
        "netIncomeToCommon": 80000000000,
        "sharesOutstanding": 15000000000,
    }


def _make_history_side_effect(hist_5d: pd.DataFrame, hist_1mo: pd.DataFrame):
    """Create a side_effect function for Ticker.history() calls.

    get_ohlcv calls history() twice: once with period='5d', once with period='1mo'.
    """

    def history_side_effect(period: str = "5d", **kwargs):
        if period == "1mo":
            return hist_1mo
        return hist_5d

    return history_side_effect


# --- Integ-01: test_analyze_realdata_mode ---


@patch("app.services.stock_data.yf")
async def test_analyze_realdata_mode(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    mock_history_1mo_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with ticker only returns realdata mode with 3 candles."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    mock_ticker.history.side_effect = _make_history_side_effect(
        mock_history_df, mock_history_1mo_df
    )

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["mode"] == "realdata"
    assert len(body["candles"]) == 3
    assert isinstance(body["atr"], float)
    assert body["short_interest"] is not None
    assert "short_percent_of_float" in body["short_interest"]


# --- Integ-02: test_analyze_simulation_predicted_mode ---


@patch("app.services.stock_data.yf")
async def test_analyze_simulation_predicted_mode(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with change1+change2 returns simulation_predicted mode."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    # get_latest_close uses history(period="5d")
    mock_ticker.history.return_value = mock_history_df

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={"ticker": "AAPL", "change1": 5.0, "change2": -3.0},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["mode"] == "simulation_predicted"
    assert len(body["candles"]) == 2
    assert isinstance(body["base_price"], float)
    assert body["atr"] is None
    assert body["short_interest"] is None
    # Simulated candles have volume=0
    for candle in body["candles"]:
        assert candle["volume"] == 0


# --- Integ-03: test_analyze_simulation_confirmed_mode ---


@patch("app.services.stock_data.yf")
async def test_analyze_simulation_confirmed_mode(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with change1+change2+change3 returns simulation_confirmed."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    mock_ticker.history.return_value = mock_history_df

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={
                "ticker": "AAPL",
                "change1": 5.0,
                "change2": -3.0,
                "change3": 8.0,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["mode"] == "simulation_confirmed"
    assert len(body["candles"]) == 3
    assert isinstance(body["base_price"], float)


# --- Integ-04: test_analyze_change1_only_fallback_to_realdata ---


@patch("app.services.stock_data.yf")
async def test_analyze_change1_only_fallback_to_realdata(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    mock_history_1mo_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with only change1 falls back to realdata mode."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    mock_ticker.history.side_effect = _make_history_side_effect(
        mock_history_df, mock_history_1mo_df
    )

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={"ticker": "AAPL", "change1": 5.0},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "realdata"


# --- Integ-08: test_analyze_empty_ticker_returns_error ---


async def test_analyze_empty_ticker_returns_error() -> None:
    """POST /analyze with empty ticker returns 422 validation error."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": ""})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


# --- Integ-09: test_analyze_invalid_ticker_returns_400 ---


@patch("app.services.stock_data.yf")
async def test_analyze_invalid_ticker_returns_400(
    mock_yf: MagicMock,
) -> None:
    """POST /analyze with non-existent ticker returns 400."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    # No quoteType -> TickerNotFoundError from validate_ticker
    mock_ticker.info = {"symbol": "XXXYZZ"}

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "XXXYZZ"})

    assert response.status_code == 400
    body = response.json()
    assert "detail" in body


# --- Integ-11: test_analyze_api_error_returns_500 ---


@patch("app.services.stock_data.yf")
async def test_analyze_api_error_returns_500(
    mock_yf: MagicMock,
) -> None:
    """POST /analyze with yfinance exception returns 500."""
    mock_yf.Ticker.side_effect = Exception("Network error")

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body
