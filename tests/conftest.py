"""Shared test fixtures for the candlestick pattern tool."""

import pandas as pd
import pytest

from app.models.candle import CandleData

# --- Candle factory functions ---


def make_candle(
    open: float = 100.0,
    high: float = 110.0,
    low: float = 90.0,
    close: float = 105.0,
    volume: int = 1000000,
    date: str = "2024-01-01",
) -> CandleData:
    return CandleData(
        date=date, open=open, high=high, low=low, close=close, volume=volume
    )


def make_bullish_large(base: float = 100.0) -> CandleData:
    return make_candle(open=base, high=base + 12, low=base - 2, close=base + 10)


def make_bearish_large(base: float = 100.0) -> CandleData:
    return make_candle(open=base + 10, high=base + 12, low=base - 2, close=base)


def make_doji(base: float = 100.0) -> CandleData:
    return make_candle(open=base, high=base + 5, low=base - 5, close=base + 0.5)


def make_small_body(base: float = 100.0, bullish: bool = True) -> CandleData:
    close = base + 2 if bullish else base - 2
    return make_candle(open=base, high=base + 5, low=base - 5, close=close)


def make_pin_bar_bullish(base: float = 100.0) -> CandleData:
    return make_candle(open=base + 1, high=base + 2, low=base - 8, close=base + 1.5)


def make_pin_bar_bearish(base: float = 100.0) -> CandleData:
    return make_candle(open=base - 1, high=base + 8, low=base - 2, close=base - 1.5)


def make_marubozu_bullish(base: float = 100.0) -> CandleData:
    return make_candle(open=base, high=base + 10.1, low=base - 0.1, close=base + 10)


def make_marubozu_bearish(base: float = 100.0) -> CandleData:
    return make_candle(open=base + 10, high=base + 10.1, low=base - 0.1, close=base)


@pytest.fixture
def mock_yfinance_history() -> pd.DataFrame:
    """5-day OHLCV DataFrame mimicking yfinance Ticker.history() output."""
    data = {
        "Open": [148.0, 150.0, 149.5, 151.0, 152.0],
        "High": [152.0, 153.0, 151.0, 154.0, 155.0],
        "Low": [147.0, 149.0, 148.5, 150.0, 151.0],
        "Close": [150.0, 149.5, 150.5, 153.0, 154.0],
        "Volume": [1000000, 1200000, 900000, 1100000, 1300000],
    }
    index = pd.date_range("2024-01-10", periods=5, freq="B")
    return pd.DataFrame(data, index=index)


@pytest.fixture
def mock_yfinance_history_1mo() -> pd.DataFrame:
    """1-month OHLCV DataFrame for ATR calculation (20+ rows)."""
    import numpy as np

    rng = np.random.default_rng(42)
    n = 22
    base = 150.0
    opens = base + rng.uniform(-5, 5, n)
    closes = opens + rng.uniform(-3, 3, n)
    highs = [
        max(o, c) + rng.uniform(0.5, 2.0) for o, c in zip(opens, closes, strict=True)
    ]
    lows = [
        min(o, c) - rng.uniform(0.5, 2.0) for o, c in zip(opens, closes, strict=True)
    ]

    data = {
        "Open": opens.tolist(),
        "High": highs,
        "Low": lows,
        "Close": closes.tolist(),
        "Volume": [1000000] * n,
    }
    index = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame(data, index=index)


@pytest.fixture
def mock_yfinance_info_equity() -> dict:
    """yfinance Ticker.info dict for a valid EQUITY with all fields."""
    return {
        "quoteType": "EQUITY",
        "shortName": "Apple Inc.",
        "symbol": "AAPL",
        "shortPercentOfFloat": 0.75,
        "shortRatio": 1.2,
        "sharesShort": 120000000,
        "sharesShortPriorMonth": 115000000,
        "debtToEquity": 150.0,  # 1.5x after /100
        "currentRatio": 1.8,
        "profitMargins": 0.21,
        "freeCashflow": 90000000000,
        "totalCash": 50000000000,
        "totalDebt": 30000000000,
        "netIncomeToCommon": 80000000000,
        "sharesOutstanding": 15000000000,
    }


@pytest.fixture
def mock_yfinance_info_etf() -> dict:
    """yfinance Ticker.info dict for an ETF (quoteType='ETF')."""
    return {
        "quoteType": "ETF",
        "shortName": "SPDR S&P 500",
        "symbol": "SPY",
    }


@pytest.fixture
def mock_yfinance_info_minimal() -> dict:
    """yfinance Ticker.info dict with minimal/missing fields."""
    return {
        "symbol": "UNKNOWN",
    }


@pytest.fixture
def sample_bullish_candles() -> list[CandleData]:
    """3 CandleData objects forming a morning star pattern.

    c0: bearish large body
    c1: small body (doji-like)
    c2: bullish large body closing above c0 midpoint
    """
    return [
        CandleData(
            date="2024-01-10",
            open=150.0,
            high=151.0,
            low=140.0,
            close=141.0,
            volume=1000000,
        ),
        CandleData(
            date="2024-01-11",
            open=141.0,
            high=142.0,
            low=140.0,
            close=141.2,
            volume=800000,
        ),
        CandleData(
            date="2024-01-12",
            open=141.5,
            high=150.0,
            low=141.0,
            close=149.0,
            volume=1200000,
        ),
    ]


@pytest.fixture
def sample_bearish_candles() -> list[CandleData]:
    """3 CandleData objects forming an evening star pattern.

    c0: bullish large body
    c1: small body (doji-like)
    c2: bearish large body closing below c0 midpoint
    """
    return [
        CandleData(
            date="2024-01-10",
            open=140.0,
            high=151.0,
            low=139.0,
            close=150.0,
            volume=1000000,
        ),
        CandleData(
            date="2024-01-11",
            open=150.5,
            high=151.5,
            low=149.5,
            close=150.2,
            volume=800000,
        ),
        CandleData(
            date="2024-01-12",
            open=149.0,
            high=150.0,
            low=140.0,
            close=141.0,
            volume=1200000,
        ),
    ]


@pytest.fixture
def sample_flat_candles() -> list[CandleData]:
    """3 CandleData objects with no discernible pattern."""
    return [
        CandleData(
            date="2024-01-10",
            open=150.0,
            high=150.5,
            low=149.5,
            close=150.1,
            volume=500000,
        ),
        CandleData(
            date="2024-01-11",
            open=150.1,
            high=150.6,
            low=149.6,
            close=150.2,
            volume=500000,
        ),
        CandleData(
            date="2024-01-12",
            open=150.2,
            high=150.7,
            low=149.7,
            close=150.3,
            volume=500000,
        ),
    ]


@pytest.fixture
def healthy_company_info() -> dict:
    """Info dict representing a financially healthy company (all low risk)."""
    return {
        "quoteType": "EQUITY",
        "debtToEquity": 50.0,  # 0.5x after /100 -> low
        "currentRatio": 2.5,  # > 1.5 -> low
        "profitMargins": 0.25,  # > 0.10 -> low
        "freeCashflow": 5000000000,  # > 0 -> low
        "totalCash": 20000000000,
        "totalDebt": 5000000000,
        "netIncomeToCommon": 10000000000,  # positive -> low
        "sharesOutstanding": 1000000000,
    }


@pytest.fixture
def risky_company_info() -> dict:
    """Info dict representing a high-risk company (all high risk)."""
    return {
        "quoteType": "EQUITY",
        "debtToEquity": 350.0,  # 3.5x after /100 -> high
        "currentRatio": 0.5,  # < 1.0 -> high
        "profitMargins": -0.15,  # < 0.0 -> high
        "freeCashflow": -500000000,  # < 0 -> high
        "totalCash": 100000000,
        "totalDebt": 2000000000,
        "netIncomeToCommon": -800000000,  # negative -> high
        "sharesOutstanding": 500000000,
    }
