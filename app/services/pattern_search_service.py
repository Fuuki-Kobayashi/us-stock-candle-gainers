"""Pattern search service for reverse-lookup by pattern ID."""

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.candle import PatternResult
from app.models.pattern_search import PatternSearchResult
from app.services import pattern_detector, stock_data


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
    mode = "realdata" if candle_count == 3 else "realdata_2candle"
    pattern_ids_set = set(pattern_ids)

    for ticker in tickers:
        try:
            stock_data.validate_ticker(ticker)
            candles, _atr = stock_data.get_ohlcv(
                ticker, candle_count, confirmed_only=False
            )
            all_patterns = pattern_detector.detect_patterns(candles, mode=mode)

            # Filter by pattern_id
            matched: list[PatternResult] = [
                p for p in all_patterns if p.pattern_id in pattern_ids_set
            ]

            # Exclude tickers with 0 matching patterns
            if not matched:
                continue

            change_pct = (
                (candles[-1].close - candles[-2].close) / candles[-2].close * 100
            )
            results.append(
                PatternSearchResult(
                    ticker=ticker,
                    change_pct=change_pct,
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
