from typing import Literal

from pydantic import BaseModel


class CandleData(BaseModel):
    """OHLCV candlestick data for a single trading day."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class PatternResult(BaseModel):
    """Detected candlestick pattern result."""

    type: str  # "confirmed" or "predicted"
    name: str  # Japanese pattern name
    signal: str  # Signal with emoji
    description: str  # Japanese description
    required_third: str | None = None  # 3rd candle condition (predicted only)
    direction: Literal["bullish", "bearish"]
    pattern_candle_count: Literal[1, 2, 3]


class ShortInterest(BaseModel):
    """Short interest data for a ticker."""

    short_percent_of_float: float | None = None
    short_ratio: float | None = None
    shares_short: int | None = None
    shares_short_prior_month: int | None = None
