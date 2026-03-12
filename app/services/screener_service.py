"""Screener service for bulk ticker scanning."""

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.screener import TickerScanResult
from app.services import pattern_detector, stock_data
from app.services.ticker_pattern_service import analyze_ticker_patterns


def scan_tickers(tickers: list[str], candle_count: int = 3) -> list[TickerScanResult]:
    """Scan multiple tickers for candlestick patterns.

    For each ticker: validate -> fetch OHLCV -> detect patterns.
    Errors are caught per-ticker and stored in the result's error field.
    """
    results: list[TickerScanResult] = []

    for ticker in tickers:
        try:
            analysis = analyze_ticker_patterns(
                ticker,
                candle_count,
                validate_ticker=stock_data.validate_ticker,
                get_ohlcv=_get_recent_candles,
                detect_patterns=pattern_detector.detect_patterns,
            )
            results.append(
                TickerScanResult(
                    ticker=ticker,
                    candles=analysis.candles,
                    patterns=analysis.patterns,
                    change_pct=analysis.change_pct,
                )
            )
        except (
            TickerNotFoundError,
            TickerNotEquityError,
            DataFetchError,
            Exception,
        ) as e:
            results.append(TickerScanResult(ticker=ticker, error=str(e)))

    return results


def _get_recent_candles(
    ticker: str, candle_count: int
) -> tuple[list, float | None]:
    """Fetch the most recent candles including the current trading day."""
    return stock_data.get_ohlcv(ticker, candle_count, confirmed_only=False)
