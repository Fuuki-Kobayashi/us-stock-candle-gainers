"""Stock data service for fetching OHLCV, short interest, and financial info."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytz
import yfinance as yf

from app.exceptions import DataFetchError, TickerNotEquityError, TickerNotFoundError
from app.models.candle import CandleData, ShortInterest

US_EASTERN = pytz.timezone("US/Eastern")
MARKET_OPEN_MIN = 9 * 60 + 30  # 9:30 ET
MARKET_CLOSE_MIN = 16 * 60  # 16:00 ET


def _is_market_open() -> bool:
    """Check if US stock market is currently open."""
    now_et = datetime.now(US_EASTERN)
    if now_et.weekday() >= 5:  # Saturday/Sunday
        return False
    minutes = now_et.hour * 60 + now_et.minute
    return MARKET_OPEN_MIN <= minutes < MARKET_CLOSE_MIN


def _drop_intraday_bar(df: pd.DataFrame) -> pd.DataFrame:
    """Drop today's unconfirmed bar if market is still open."""
    if df.empty or not _is_market_open():
        return df
    today = datetime.now(US_EASTERN).date()
    last_date = df.index[-1].date()
    if last_date == today:
        return df.iloc[:-1]
    return df


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
    ticker: str,
    candle_count: int = 3,
    *,
    confirmed_only: bool = True,
) -> tuple[list[CandleData], float | None]:
    """Fetch most recent candles and ATR(14).

    Args:
        ticker: Stock ticker symbol.
        candle_count: Number of candles to return (2 or 3, default 3).
        confirmed_only: If True, exclude today's unconfirmed bar during market hours.

    Returns (candles, atr).
    Uses history(period='5d') for candles (last N rows).
    Uses history(period='1mo') for ATR(14) calculation.
    Wraps any yfinance errors in DataFetchError.
    """
    try:
        t = yf.Ticker(ticker)

        # Fetch candle data
        hist_5d = t.history(period="5d")
        if confirmed_only:
            hist_5d = _drop_intraday_bar(hist_5d)
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
    from datetime import datetime

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

    # Convert epoch seconds to YYYY-MM-DD
    date_si_epoch = info.get("dateShortInterest")
    date_prior_epoch = info.get("sharesShortPreviousMonthDate")
    date_si = (
        datetime.fromtimestamp(date_si_epoch, tz=UTC).strftime("%Y-%m-%d")
        if date_si_epoch
        else None
    )
    date_prior = (
        datetime.fromtimestamp(date_prior_epoch, tz=UTC).strftime("%Y-%m-%d")
        if date_prior_epoch
        else None
    )

    return ShortInterest(
        short_percent_of_float=short_pct * 100 if short_pct is not None else None,
        short_ratio=short_ratio,
        shares_short=shares_short,
        shares_short_prior_month=shares_short_prior,
        date_short_interest=date_si,
        date_short_prior_month=date_prior,
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
