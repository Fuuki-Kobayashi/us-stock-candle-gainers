"""Integration tests for the risk router (POST /risk).

These tests mock yfinance at the service level (app.services.stock_data.yf)
and test through the full HTTP layer using httpx AsyncClient.
"""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


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


# --- Integ-05: test_risk_valid_ticker ---


@patch("app.services.stock_data.yf")
async def test_risk_valid_ticker(
    mock_yf: MagicMock,
    valid_equity_info: dict,
) -> None:
    """POST /risk with valid ticker returns 200 with financial_health and offering_risk."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/risk", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"

    # financial_health structure
    fh = body["financial_health"]
    assert "de_ratio" in fh
    assert "current_ratio" in fh
    assert "profit_margin" in fh
    assert "fcf" in fh
    assert "overall_level" in fh
    assert "summary" in fh

    # offering_risk structure
    orisk = body["offering_risk"]
    assert "cash_runway" in orisk
    assert "dilution" in orisk
    assert "net_income" in orisk
    assert "debt_cash_ratio" in orisk
    assert "overall_level" in orisk
    assert "summary" in orisk


# --- Integ-06: test_risk_financial_health_metrics_complete ---


@patch("app.services.stock_data.yf")
async def test_risk_financial_health_metrics_complete(
    mock_yf: MagicMock,
    valid_equity_info: dict,
) -> None:
    """POST /risk returns metrics with name, value, level, description."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/risk", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()

    # Verify each financial_health metric has all required fields
    fh = body["financial_health"]
    metric_keys = ["de_ratio", "current_ratio", "profit_margin", "fcf"]
    for key in metric_keys:
        metric = fh[key]
        assert "name" in metric, f"{key} missing 'name'"
        assert "value" in metric, f"{key} missing 'value'"
        assert "level" in metric, f"{key} missing 'level'"
        assert "description" in metric, f"{key} missing 'description'"
        assert metric["level"] in ("低", "中", "高"), (
            f"{key} level '{metric['level']}' is invalid"
        )

    # Verify each offering_risk metric has all required fields
    orisk = body["offering_risk"]
    offering_keys = ["cash_runway", "dilution", "net_income", "debt_cash_ratio"]
    for key in offering_keys:
        metric = orisk[key]
        assert "name" in metric, f"{key} missing 'name'"
        assert "value" in metric, f"{key} missing 'value'"
        assert "level" in metric, f"{key} missing 'level'"
        assert "description" in metric, f"{key} missing 'description'"
        assert metric["level"] in ("低", "中", "高"), (
            f"{key} level '{metric['level']}' is invalid"
        )


# --- Integ-10: test_risk_invalid_ticker_returns_400 ---


@patch("app.services.stock_data.yf")
async def test_risk_invalid_ticker_returns_400(
    mock_yf: MagicMock,
) -> None:
    """POST /risk with non-existent ticker returns 400."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    # No quoteType -> TickerNotFoundError from validate_ticker
    mock_ticker.info = {"symbol": "XXXYZZ"}

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/risk", json={"ticker": "XXXYZZ"})

    assert response.status_code == 400
    body = response.json()
    assert "detail" in body
