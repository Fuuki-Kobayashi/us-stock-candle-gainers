"""Candlestick pattern detection service.

Detects confirmed (3-candle) and predicted (2-candle) patterns
from OHLCV candlestick data without any external dependencies.
"""

from app.models.candle import CandleData, PatternResult

# --- Thresholds ---
LARGE_BODY_THRESHOLD = 0.6
SMALL_BODY_THRESHOLD = 0.3
DOJI_THRESHOLD = 0.1
MARUBOZU_THRESHOLD = 0.9
PIN_BAR_SHADOW_RATIO = 2.0
TOLERANCE_RATIO = 0.001


def _body_ratio(candle: CandleData) -> float:
    """Calculate body ratio: abs(close - open) / (high - low)."""
    candle_range = candle.high - candle.low
    if candle_range == 0:
        return 0.0
    return abs(candle.close - candle.open) / candle_range


def _is_bullish(candle: CandleData) -> bool:
    return candle.close >= candle.open


def _is_bearish(candle: CandleData) -> bool:
    return candle.close < candle.open


def _is_large_body(candle: CandleData) -> bool:
    return _body_ratio(candle) >= LARGE_BODY_THRESHOLD


def _is_small_body(candle: CandleData) -> bool:
    return _body_ratio(candle) <= SMALL_BODY_THRESHOLD


def _midpoint(candle: CandleData) -> float:
    return (candle.open + candle.close) / 2


def _body_top(candle: CandleData) -> float:
    return max(candle.open, candle.close)


def _body_bottom(candle: CandleData) -> float:
    return min(candle.open, candle.close)


def _body_size(candle: CandleData) -> float:
    return abs(candle.close - candle.open)


def _candle_range(candle: CandleData) -> float:
    return candle.high - candle.low


def _is_doji(candle: CandleData) -> bool:
    return _body_ratio(candle) <= DOJI_THRESHOLD


def _is_marubozu(candle: CandleData) -> bool:
    return _body_ratio(candle) >= MARUBOZU_THRESHOLD


def _upper_shadow(candle: CandleData) -> float:
    return candle.high - max(candle.open, candle.close)


def _lower_shadow(candle: CandleData) -> float:
    return min(candle.open, candle.close) - candle.low


def _upper_shadow_ratio(candle: CandleData) -> float:
    body = _body_size(candle)
    if body == 0:
        cr = _candle_range(candle)
        return _upper_shadow(candle) / cr if cr > 0 else 0.0
    return _upper_shadow(candle) / body


def _lower_shadow_ratio(candle: CandleData) -> float:
    body = _body_size(candle)
    if body == 0:
        cr = _candle_range(candle)
        return _lower_shadow(candle) / cr if cr > 0 else 0.0
    return _lower_shadow(candle) / body


def _is_pin_bar_bullish(candle: CandleData) -> bool:
    return (
        _lower_shadow_ratio(candle) >= PIN_BAR_SHADOW_RATIO
        and _upper_shadow(candle) < _body_size(candle) * 0.5
    )


def _is_pin_bar_bearish(candle: CandleData) -> bool:
    return (
        _upper_shadow_ratio(candle) >= PIN_BAR_SHADOW_RATIO
        and _lower_shadow(candle) < _body_size(candle) * 0.5
    )


def _has_gap_up(prev: CandleData, curr: CandleData) -> bool:
    return curr.low > prev.high


def _has_gap_down(prev: CandleData, curr: CandleData) -> bool:
    return curr.high < prev.low


def _near_equal(a: float, b: float, tolerance: float | None = None) -> bool:
    if tolerance is None:
        tolerance = max(abs(a), abs(b)) * TOLERANCE_RATIO
    return abs(a - b) <= tolerance


# --- Pattern detection via submodules ---


def detect_patterns(candles: list[CandleData], mode: str) -> list[PatternResult]:
    """Detect candlestick patterns.

    Args:
        candles: List of OHLCV candlestick data.
        mode: Detection mode.
            "realdata" -> 1-candle + 2-candle + 3-candle confirmed + predicted
            "realdata_2candle" -> 1-candle + 2-candle confirmed + predicted
            "simulation_predicted" -> predicted only
            "simulation_confirmed" -> 1-candle + 2-candle + 3-candle confirmed
    """
    # Lazy import to avoid circular dependency
    # (submodules import helpers from this module)
    from app.services.patterns import (
        detect_1_candle,
        detect_2_candle_bearish,
        detect_2_candle_bullish,
        detect_3_candle_bearish,
        detect_3_candle_bullish,
        detect_predicted,
    )

    results: list[PatternResult] = []

    if mode == "realdata":
        # 1-candle (last candle)
        if len(candles) >= 1:
            results.extend(detect_1_candle(candles[-1]))
        # 2-candle (last 2)
        if len(candles) >= 2:
            results.extend(detect_2_candle_bullish(candles[-2], candles[-1]))
            results.extend(detect_2_candle_bearish(candles[-2], candles[-1]))
        # 3-candle (all 3)
        if len(candles) >= 3:
            results.extend(
                detect_3_candle_bullish(candles[-3], candles[-2], candles[-1])
            )
            results.extend(
                detect_3_candle_bearish(candles[-3], candles[-2], candles[-1])
            )
        # predicted (last 2)
        if len(candles) >= 2:
            results.extend(detect_predicted(candles[-2], candles[-1]))

    elif mode == "realdata_2candle":
        # 1-candle (last)
        if len(candles) >= 1:
            results.extend(detect_1_candle(candles[-1]))
        # 2-candle confirmed (both)
        if len(candles) >= 2:
            results.extend(detect_2_candle_bullish(candles[-2], candles[-1]))
            results.extend(detect_2_candle_bearish(candles[-2], candles[-1]))
        # predicted (both)
        if len(candles) >= 2:
            results.extend(detect_predicted(candles[-2], candles[-1]))

    elif mode == "simulation_predicted":
        # predicted only
        if len(candles) >= 2:
            results.extend(detect_predicted(candles[-2], candles[-1]))

    elif mode == "simulation_confirmed":
        # 1-candle (last)
        if len(candles) >= 1:
            results.extend(detect_1_candle(candles[-1]))
        # 2-candle (last 2)
        if len(candles) >= 2:
            results.extend(detect_2_candle_bullish(candles[-2], candles[-1]))
            results.extend(detect_2_candle_bearish(candles[-2], candles[-1]))
        # 3-candle (all 3)
        if len(candles) >= 3:
            results.extend(
                detect_3_candle_bullish(candles[-3], candles[-2], candles[-1])
            )
            results.extend(
                detect_3_candle_bearish(candles[-3], candles[-2], candles[-1])
            )

    return results
