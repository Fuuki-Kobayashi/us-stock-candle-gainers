"""Pattern search service for reverse-lookup by pattern ID."""

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.candle import PatternResult
from app.models.pattern_search import PatternSearchResult
from app.services import pattern_detector, stock_data
from app.services.ticker_pattern_service import analyze_ticker_patterns


def search_patterns(
    tickers: list[str],
    pattern_ids: list[str],
    candle_count: int = 3,
) -> list[PatternSearchResult]:
    """Search for specific patterns across multiple tickers.

    For each ticker: validate -> fetch OHLCV -> detect patterns -> filter by pattern_id.
    Tickers with 0 matching patterns are excluded from results.
    Error tickers are always included.
    """
    results: list[PatternSearchResult] = []
    pattern_ids_set = set(pattern_ids)

    for ticker in tickers:
        try:
            analysis = analyze_ticker_patterns(
                ticker,
                candle_count,
                validate_ticker=stock_data.validate_ticker,
                get_ohlcv=_get_recent_candles,
                detect_patterns=pattern_detector.detect_patterns,
            )

            # Filter by pattern_id
            matched: list[PatternResult] = [
                p for p in analysis.patterns if p.pattern_id in pattern_ids_set
            ]

            # Exclude tickers with 0 matching patterns
            if not matched:
                continue

            results.append(
                PatternSearchResult(
                    ticker=ticker,
                    change_pct=analysis.change_pct,
                    patterns=matched,
                )
            )
        except (
            TickerNotFoundError,
            TickerNotEquityError,
            DataFetchError,
            Exception,
        ) as e:
            results.append(
                PatternSearchResult(
                    ticker=ticker,
                    patterns=[],
                    error=str(e),
                )
            )

    return results


def _get_recent_candles(
    ticker: str, candle_count: int
) -> tuple[list, float | None]:
    """Fetch the most recent candles including the current trading day."""
    return stock_data.get_ohlcv(ticker, candle_count, confirmed_only=False)
