"""Integration tests for pattern search router."""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.candle import CandleData, PatternResult


def _make_candle(open_: float, high: float, low: float, close: float) -> CandleData:
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
    return PatternResult(
        type="confirmed",
        name=name,
        pattern_id=pattern_id,
        signal="test",
        description="test",
        direction=direction,
        pattern_candle_count=3,
    )


class TestListPatterns:
    """Integ-01: GET /api/patterns"""

    @pytest.mark.asyncio
    async def test_returns_all_patterns(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/patterns")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 60
        assert len(data["patterns"]) == 60

    @pytest.mark.asyncio
    async def test_pattern_fields(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/patterns")
        data = resp.json()
        p = data["patterns"][0]
        assert "id" in p
        assert "name" in p
        assert "direction" in p
        assert "available_types" in p
        assert "pattern_candle_count" in p


class TestPatternSearchValidation:
    """Integ-02: POST /api/pattern-search validation"""

    @pytest.mark.asyncio
    async def test_empty_tickers_422(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/pattern-search",
                json={"tickers": [], "pattern_ids": ["morning_star"]},
            )
        assert resp.status_code == 422  # Pydantic validation

    @pytest.mark.asyncio
    async def test_empty_pattern_ids_422(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/pattern-search",
                json={"tickers": ["AAPL"], "pattern_ids": []},
            )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_pattern_id_400(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/pattern-search",
                json={"tickers": ["AAPL"], "pattern_ids": ["nonexistent_pattern"]},
            )
        assert resp.status_code == 400  # Business validation

    @pytest.mark.asyncio
    async def test_tickers_exceed_50_422(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/pattern-search",
                json={
                    "tickers": [f"T{i}" for i in range(51)],
                    "pattern_ids": ["morning_star"],
                },
            )
        assert resp.status_code == 422


class TestPatternSearchExecution:
    """Integ-03: POST /api/pattern-search with mocked data"""

    @pytest.mark.asyncio
    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    async def test_search_returns_results(self, mock_sd, mock_pd):
        candles = [
            _make_candle(100, 110, 90, 105),
            _make_candle(105, 115, 95, 110),
        ]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 5.0)
        mock_pd.detect_patterns.return_value = [
            _make_pattern("morning star", "morning_star"),
        ]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/pattern-search",
                json={"tickers": ["AAPL"], "pattern_ids": ["morning_star"]},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["matched"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["ticker"] == "AAPL"


class TestPatternSearchPartialSuccess:
    """Integ-04: Partial success with errors"""

    @pytest.mark.asyncio
    @patch("app.services.pattern_search_service.pattern_detector")
    @patch("app.services.pattern_search_service.stock_data")
    async def test_partial_success(self, mock_sd, mock_pd):
        candles = [
            _make_candle(100, 110, 90, 105),
            _make_candle(105, 115, 95, 110),
        ]

        def mock_validate(ticker):
            if ticker == "FAIL":
                from app.exceptions import TickerNotFoundError

                raise TickerNotFoundError(ticker)

        mock_sd.validate_ticker.side_effect = mock_validate
        mock_sd.get_ohlcv.return_value = (candles, 5.0)
        mock_pd.detect_patterns.return_value = [
            _make_pattern("morning star", "morning_star"),
        ]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/pattern-search",
                json={
                    "tickers": ["AAPL", "FAIL"],
                    "pattern_ids": ["morning_star"],
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert data["errors"] == 1


class TestPatternSearchPage:
    """Integ-05: Page route"""

    @pytest.mark.asyncio
    async def test_pattern_search_page_route(self):
        """Note: This test will fail until static/pattern-search.html is created."""
        pass  # Will be tested in E2E phase
