"""Screener service for bulk ticker scanning."""

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.screener import TickerScanResult
from app.services import pattern_detector, stock_data


def scan_tickers(tickers: list[str], candle_count: int = 3) -> list[TickerScanResult]:
    """Scan multiple tickers for candlestick patterns.

    For each ticker: validate -> fetch OHLCV -> detect patterns.
    Errors are caught per-ticker and stored in the result's error field.
    """
    results: list[TickerScanResult] = []
    mode = "realdata" if candle_count == 3 else "realdata_2candle"

    for ticker in tickers:
        try:
            stock_data.validate_ticker(ticker)
            candles, _atr = stock_data.get_ohlcv(
                ticker, candle_count, confirmed_only=False
            )
            patterns = pattern_detector.detect_patterns(candles, mode=mode)
            change_pct = (
                (candles[-1].close - candles[-2].close) / candles[-2].close * 100
            )
            results.append(
                TickerScanResult(
                    ticker=ticker,
                    candles=candles,
                    patterns=patterns,
                    change_pct=change_pct,
                )
            )
        except TickerNotFoundError as e:
            results.append(TickerScanResult(ticker=ticker, error=str(e)))
        except TickerNotEquityError as e:
            results.append(TickerScanResult(ticker=ticker, error=str(e)))
        except DataFetchError as e:
            results.append(TickerScanResult(ticker=ticker, error=str(e)))
        except Exception as e:
            results.append(TickerScanResult(ticker=ticker, error=str(e)))

    return results
