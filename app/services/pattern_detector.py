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


# --- Confirmed patterns (3-candle) ---


def _detect_confirmed_patterns(candles: list[CandleData]) -> list[PatternResult]:
    """Detect confirmed 3-candle patterns from the last 3 candles."""
    if len(candles) < 3:
        return []

    c0, c1, c2 = candles[-3], candles[-2], candles[-1]
    results: list[PatternResult] = []

    # 1. Morning Star
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_small_body(c1)
        and _is_bullish(c2)
        and _is_large_body(c2)
        and c2.close > _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                name="モーニングスター",
                signal="🔼 強気シグナル",
                description="下降トレンドからの反転を示唆する3本パターンです。",
            )
        )

    # 2. Evening Star
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_small_body(c1)
        and _is_bearish(c2)
        and _is_large_body(c2)
        and c2.close < _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                name="イブニングスター",
                signal="🔽 弱気シグナル",
                description="上昇トレンドからの反転を示唆する3本パターンです。",
            )
        )

    # 3. Three White Soldiers
    if (
        _is_bullish(c0)
        and _is_bullish(c1)
        and _is_bullish(c2)
        and c1.close > c0.close
        and c2.close > c1.close
        and min(c0.open, c0.close) <= c1.open <= max(c0.open, c0.close)
        and min(c1.open, c1.close) <= c2.open <= max(c1.open, c1.close)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                name="スリーホワイトソルジャーズ",
                signal="🔼 強気シグナル",
                description="3本連続の陽線で、強い上昇トレンドを示唆します。",
            )
        )

    # 4. Three Black Crows
    if (
        _is_bearish(c0)
        and _is_bearish(c1)
        and _is_bearish(c2)
        and c1.close < c0.close
        and c2.close < c1.close
        and min(c0.open, c0.close) <= c1.open <= max(c0.open, c0.close)
        and min(c1.open, c1.close) <= c2.open <= max(c1.open, c1.close)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                name="スリーブラッククロウズ",
                signal="🔽 弱気シグナル",
                description="3本連続の陰線で、強い下降トレンドを示唆します。",
            )
        )

    # 5. Rising Three Methods
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _is_small_body(c1)
        and c1.high <= c0.high
        and c1.low >= c0.low
        and _is_bullish(c2)
        and _is_large_body(c2)
        and c2.close > c0.close
    ):
        results.append(
            PatternResult(
                type="confirmed",
                name="上昇三法",
                signal="🔼 強気シグナル",
                description="上昇トレンドの継続を示唆するパターンです。",
            )
        )

    # 6. Falling Three Methods
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and c1.high <= c0.high
        and c1.low >= c0.low
        and _is_bearish(c2)
        and _is_large_body(c2)
        and c2.close < c0.close
    ):
        results.append(
            PatternResult(
                type="confirmed",
                name="下降三法",
                signal="🔽 弱気シグナル",
                description="下降トレンドの継続を示唆するパターンです。",
            )
        )

    return results


# --- Predicted patterns (2-candle) ---


def _detect_predicted_patterns(candles: list[CandleData]) -> list[PatternResult]:
    """Detect predicted 2-candle patterns from the first 2 candles."""
    if len(candles) < 2:
        return []

    c0, c1 = candles[0], candles[1]
    results: list[PatternResult] = []

    # 1. Morning Star Predicted
    if _is_bearish(c0) and _is_large_body(c0) and _is_small_body(c1):
        results.append(
            PatternResult(
                type="predicted",
                name="モーニングスター予測",
                signal="🔼 強気シグナル（予測）",
                description="モーニングスターの初期形成が見られます。",
                required_third="3日目に大きな陽線が出現し、1日目の中間点を超えて引ける",
            )
        )

    # 2. Evening Star Predicted
    if _is_bullish(c0) and _is_large_body(c0) and _is_small_body(c1):
        results.append(
            PatternResult(
                type="predicted",
                name="イブニングスター予測",
                signal="🔽 弱気シグナル（予測）",
                description="イブニングスターの初期形成が見られます。",
                required_third="3日目に大きな陰線が出現し、1日目の中間点を下回って引ける",
            )
        )

    # 3. Bullish Engulfing Predicted
    if _is_bearish(c0) and _is_bullish(c1) and c1.open < c0.low:
        results.append(
            PatternResult(
                type="predicted",
                name="強気の包み足予測",
                signal="🔼 強気シグナル（予測）",
                description="強気の包み足パターンの形成が見られます。",
                required_third="3日目も陽線で続伸する",
            )
        )

    # 4. Bearish Engulfing Predicted
    if _is_bullish(c0) and _is_bearish(c1) and c1.open > c0.high:
        results.append(
            PatternResult(
                type="predicted",
                name="弱気の包み足予測",
                signal="🔽 弱気シグナル（予測）",
                description="弱気の包み足パターンの形成が見られます。",
                required_third="3日目も陰線で続落する",
            )
        )

    # 5. Bullish Piercing Predicted
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and c1.open < c0.low
        and c1.close > _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type="predicted",
                name="強気の切り込み予測",
                signal="🔼 強気シグナル（予測）",
                description="強気の切り込みパターンの形成が見られます。",
                required_third="3日目に陽線で1日目の始値を超える",
            )
        )

    # 6. Bearish Dark Cloud Predicted
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and c1.open > c0.high
        and c1.close < _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type="predicted",
                name="弱気のかぶせ線予測",
                signal="🔽 弱気シグナル（予測）",
                description="弱気のかぶせ線パターンの形成が見られます。",
                required_third="3日目に陰線で1日目の始値を下回る",
            )
        )

    return results


def detect_patterns(candles: list[CandleData], mode: str) -> list[PatternResult]:
    """Detect candlestick patterns.

    Args:
        candles: List of OHLCV candlestick data.
        mode: Detection mode.
            "realdata" -> both confirmed + predicted
            "simulation_predicted" -> predicted only
            "simulation_confirmed" -> confirmed only
    """
    results: list[PatternResult] = []

    if mode in ("realdata", "simulation_confirmed"):
        results.extend(_detect_confirmed_patterns(candles))

    if mode in ("realdata", "simulation_predicted"):
        results.extend(_detect_predicted_patterns(candles))

    return results
