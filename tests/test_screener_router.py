"""Integration tests for the screener router (Integ-01~04: 11 tests).

Tests mock stock_data and pattern_detector at the service level
and test through the full HTTP layer using httpx AsyncClient.
"""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.exceptions import DataFetchError, TickerNotFoundError
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


def _make_pattern() -> PatternResult:
    return PatternResult(
        type="confirmed",
        name="テストパターン",
        signal="強気シグナル",
        description="テスト",
        direction="bullish",
        pattern_candle_count=2,
    )


# --- Integ-01: GET /screener page ---


class TestScreenerPage:
    @pytest.mark.asyncio
    async def test_screener_page_returns_html(self) -> None:
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/screener")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]


# --- Integ-02: POST /screener normal ---


class TestScreenerAPI:
    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_scan_single_ticker(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles()
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = [_make_pattern()]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/screener", json={"tickers": ["AAPL"]})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["scanned"] == 1
        assert data["errors"] == 0
        assert len(data["results"]) == 1
        assert data["results"][0]["ticker"] == "AAPL"

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_scan_multiple_tickers(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles()
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/screener", json={"tickers": ["AAPL", "MSFT", "GOOGL"]}
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert data["scanned"] == 3

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_scan_with_candle_count_2(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles()[:2]
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 1.5)
        mock_pd.detect_patterns.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/screener", json={"tickers": ["AAPL"], "candle_count": 2}
            )
        assert resp.status_code == 200

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_response_has_all_fields(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles()
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/screener", json={"tickers": ["AAPL"]})
        data = resp.json()
        assert "results" in data
        assert "total" in data
        assert "scanned" in data
        assert "errors" in data

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_ticker_result_has_change_pct(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles(100.0, 110.0)
        mock_sd.validate_ticker.return_value = None
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/screener", json={"tickers": ["AAPL"]})
        data = resp.json()
        assert data["results"][0]["change_pct"] is not None


# --- Integ-03: POST /screener validation errors ---


class TestScreenerValidation:
    @pytest.mark.asyncio
    async def test_empty_tickers_returns_422(self) -> None:
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/screener", json={"tickers": []})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_over_50_tickers_returns_422(self) -> None:
        from app.main import app

        tickers = [f"T{i}" for i in range(51)]
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/screener", json={"tickers": tickers})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_candle_count_returns_422(self) -> None:
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/screener", json={"tickers": ["AAPL"], "candle_count": 4}
            )
        assert resp.status_code == 422


# --- Integ-04: POST /screener partial success ---


class TestScreenerPartialSuccess:
    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_invalid_ticker_in_mix(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles()

        def validate_side_effect(ticker: str) -> None:
            if ticker == "INVALID":
                raise TickerNotFoundError(ticker)

        mock_sd.validate_ticker.side_effect = validate_side_effect
        mock_sd.get_ohlcv.return_value = (candles, 2.0)
        mock_pd.detect_patterns.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/screener", json={"tickers": ["AAPL", "INVALID", "MSFT"]}
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert data["scanned"] == 2
        assert data["errors"] == 1
        assert data["results"][1]["error"] is not None

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_all_invalid_tickers(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        mock_sd.validate_ticker.side_effect = TickerNotFoundError("BAD")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/screener", json={"tickers": ["BAD1", "BAD2"]})
        assert resp.status_code == 200
        data = resp.json()
        assert data["errors"] == data["total"]
        assert all(r["error"] is not None for r in data["results"])

    @patch("app.services.screener_service.pattern_detector")
    @patch("app.services.screener_service.stock_data")
    @pytest.mark.asyncio
    async def test_data_fetch_error_partial(
        self, mock_sd: MagicMock, mock_pd: MagicMock
    ) -> None:
        from app.main import app

        candles = _make_candles()

        def validate_side_effect(ticker: str) -> None:
            pass

        call_count = 0

        def ohlcv_side_effect(ticker: str, candle_count: int = 3) -> tuple:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise DataFetchError("timeout")
            return (candles, 2.0)

        mock_sd.validate_ticker.side_effect = validate_side_effect
        mock_sd.get_ohlcv.side_effect = ohlcv_side_effect
        mock_pd.detect_patterns.return_value = []

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/screener", json={"tickers": ["AAPL", "FAIL", "MSFT"]}
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["errors"] == 1
        assert data["results"][0]["error"] is None
        assert data["results"][1]["error"] is not None
        assert data["results"][2]["error"] is None
