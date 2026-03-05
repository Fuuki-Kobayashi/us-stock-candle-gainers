"""Stock data service for fetching OHLCV, short interest, and financial info."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.candle import CandleData, ShortInterest


def validate_ticker(ticker: str) -> dict:
    """Validate ticker is a real EQUITY. Returns yfinance info dict.

    Raises TickerNotFoundError if no quoteType.
    Raises TickerNotEquityError if quoteType != 'EQUITY'.
    Raises DataFetchError for network/API errors.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
    except Exception as e:
        raise DataFetchError(f"Failed to fetch ticker info for '{ticker}': {e}") from e

    quote_type = info.get("quoteType")
    if quote_type is None:
        raise TickerNotFoundError(f"Ticker '{ticker}' not found")

    if quote_type != "EQUITY":
        raise TickerNotEquityError(ticker=ticker, quote_type=quote_type)

    return info


def get_ohlcv(
    ticker: str, candle_count: int = 3
) -> tuple[list[CandleData], float | None]:
    """Fetch most recent candles and ATR(14).

    Args:
        ticker: Stock ticker symbol.
        candle_count: Number of candles to return (2 or 3, default 3).

    Returns (candles, atr).
    Uses history(period='5d') for candles (last N rows).
    Uses history(period='1mo') for ATR(14) calculation.
    Wraps any yfinance errors in DataFetchError.
    """
    try:
        t = yf.Ticker(ticker)

        # Fetch candle data (last N rows of 5d history)
        hist_5d = t.history(period="5d")
        last_3 = hist_5d.tail(candle_count)

        candles = []
        for idx, row in last_3.iterrows():
            candle = CandleData(
                date=idx.strftime("%Y-%m-%d"),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
            )
            candles.append(candle)

        # Fetch ATR(14)
        hist_1mo = t.history(period="1mo")
        atr = _calculate_atr(hist_1mo, period=14)

        return candles, atr

    except DataFetchError:
        raise
    except Exception as e:
        raise DataFetchError(f"Failed to fetch OHLCV for '{ticker}': {e}") from e


def _calculate_atr(df: pd.DataFrame, period: int = 14) -> float | None:
    """Calculate Average True Range over the given period."""
    if len(df) < 2:
        return None

    true_ranges: list[float] = []
    closes = df["Close"].values
    highs = df["High"].values
    lows = df["Low"].values

    for i in range(1, len(df)):
        prev_close = float(closes[i - 1])
        high = float(highs[i])
        low = float(lows[i])

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close),
        )
        true_ranges.append(tr)

    if len(true_ranges) < period:
        # Use all available if fewer than period
        return sum(true_ranges) / len(true_ranges) if true_ranges else None

    return sum(true_ranges[-period:]) / period


def get_short_interest(ticker: str) -> ShortInterest | None:
    """Fetch short interest data. Returns None if unavailable."""
    t = yf.Ticker(ticker)
    info = t.info

    short_pct = info.get("shortPercentOfFloat")
    short_ratio = info.get("shortRatio")
    shares_short = info.get("sharesShort")
    shares_short_prior = info.get("sharesShortPriorMonth")

    if all(
        v is None for v in [short_pct, short_ratio, shares_short, shares_short_prior]
    ):
        return None

    return ShortInterest(
        short_percent_of_float=short_pct,
        short_ratio=short_ratio,
        shares_short=shares_short,
        shares_short_prior_month=shares_short_prior,
    )


def get_financial_info(ticker: str) -> dict:
    """Fetch financial info dict for risk analysis.

    Calls validate_ticker first, then returns info dict.
    """
    info = validate_ticker(ticker)
    return info


def get_latest_close(ticker: str) -> float:
    """Get most recent closing price for simulation base_price.

    Uses history(period='5d'), takes last row's Close.
    """
    t = yf.Ticker(ticker)
    hist = t.history(period="5d")
    return float(hist["Close"].iloc[-1])
