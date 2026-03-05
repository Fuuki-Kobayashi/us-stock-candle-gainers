"""Unit-02: ScreenerRequest / TickerScanResult / ScreenerResponse model tests (9 tests)."""

import pytest
from pydantic import ValidationError


class TestScreenerRequest:
    def test_screener_request_valid(self) -> None:
        from app.models.screener import ScreenerRequest

        req = ScreenerRequest(tickers=["AAPL", "MSFT"])
        assert req.tickers == ["AAPL", "MSFT"]
        assert req.candle_count == 3  # default

    def test_screener_request_empty_tickers(self) -> None:
        from app.models.screener import ScreenerRequest

        with pytest.raises(ValidationError):
            ScreenerRequest(tickers=[])

    def test_screener_request_max_50_tickers(self) -> None:
        from app.models.screener import ScreenerRequest

        # 50 tickers should be OK
        tickers_50 = [f"T{i}" for i in range(50)]
        req = ScreenerRequest(tickers=tickers_50)
        assert len(req.tickers) == 50

        # 51 tickers should fail
        tickers_51 = [f"T{i}" for i in range(51)]
        with pytest.raises(ValidationError):
            ScreenerRequest(tickers=tickers_51)

    def test_screener_request_default_candle_count(self) -> None:
        from app.models.screener import ScreenerRequest

        req = ScreenerRequest(tickers=["AAPL"])
        assert req.candle_count == 3

    def test_screener_request_candle_count_2_or_3(self) -> None:
        from app.models.screener import ScreenerRequest

        # 2 and 3 are valid
        req2 = ScreenerRequest(tickers=["AAPL"], candle_count=2)
        assert req2.candle_count == 2

        req3 = ScreenerRequest(tickers=["AAPL"], candle_count=3)
        assert req3.candle_count == 3

        # 1 and 4 are invalid
        with pytest.raises(ValidationError):
            ScreenerRequest(tickers=["AAPL"], candle_count=1)

        with pytest.raises(ValidationError):
            ScreenerRequest(tickers=["AAPL"], candle_count=4)


class TestTickerScanResult:
    def test_ticker_scan_result_with_patterns(self) -> None:
        from app.models.screener import TickerScanResult

        from app.models.candle import CandleData, PatternResult

        candle = CandleData(
            date="2024-01-15",
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=1000000,
        )
        pattern = PatternResult(
            type="confirmed",
            name="包み線",
            signal="🔼 強気シグナル",
            description="テスト",
            direction="bullish",
            pattern_candle_count=2,
        )
        result = TickerScanResult(
            ticker="AAPL",
            candles=[candle],
            patterns=[pattern],
            change_pct=2.5,
        )
        assert result.ticker == "AAPL"
        assert len(result.patterns) == 1
        assert result.error is None

    def test_ticker_scan_result_with_error(self) -> None:
        from app.models.screener import TickerScanResult

        result = TickerScanResult(
            ticker="INVALID",
            error="'INVALID' は有効な株式銘柄ではありません。",
        )
        assert result.ticker == "INVALID"
        assert result.error is not None
        assert result.candles == []
        assert result.patterns == []
        assert result.change_pct is None

    def test_ticker_scan_result_with_change_pct(self) -> None:
        from app.models.screener import TickerScanResult

        result = TickerScanResult(
            ticker="AAPL",
            change_pct=-1.23,
        )
        assert result.change_pct == -1.23


class TestScreenerResponse:
    def test_screener_response_counts(self) -> None:
        from app.models.screener import ScreenerResponse, TickerScanResult

        results = [
            TickerScanResult(ticker="AAPL", change_pct=1.0),
            TickerScanResult(ticker="MSFT", change_pct=-0.5),
            TickerScanResult(ticker="INVALID", error="not found"),
        ]
        resp = ScreenerResponse(
            results=results,
            total=3,
            scanned=2,
            errors=1,
        )
        assert resp.total == 3
        assert resp.scanned == 2
        assert resp.errors == 1
        assert len(resp.results) == 3
