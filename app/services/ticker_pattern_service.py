"""Shared helpers for ticker-based candlestick pattern analysis."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.models.candle import CandleData, PatternResult

ValidateTicker = Callable[[str], dict]
GetOhlcv = Callable[..., tuple[list[CandleData], float | None]]
DetectPatterns = Callable[..., list[PatternResult]]


@dataclass(frozen=True, slots=True)
class TickerPatternAnalysis:
    """Shared analysis payload for ticker pattern workflows."""

    candles: list[CandleData]
    patterns: list[PatternResult]
    change_pct: float


def get_detection_mode(candle_count: int) -> str:
    """Resolve the pattern detector mode for the requested candle count."""
    return "realdata" if candle_count == 3 else "realdata_2candle"


def calculate_change_pct(candles: list[CandleData]) -> float:
    """Calculate the latest close change percentage from the last two candles."""
    previous_close = candles[-2].close
    latest_close = candles[-1].close
    return (latest_close - previous_close) / previous_close * 100


def analyze_ticker_patterns(
    ticker: str,
    candle_count: int,
    *,
    validate_ticker: ValidateTicker,
    get_ohlcv: GetOhlcv,
    detect_patterns: DetectPatterns,
) -> TickerPatternAnalysis:
    """Run the shared ticker validation, candle fetch, and pattern detection flow."""
    validate_ticker(ticker)
    candles, _atr = get_ohlcv(ticker, candle_count)
    patterns = detect_patterns(candles, mode=get_detection_mode(candle_count))
    return TickerPatternAnalysis(
        candles=candles,
        patterns=patterns,
        change_pct=calculate_change_pct(candles),
    )
