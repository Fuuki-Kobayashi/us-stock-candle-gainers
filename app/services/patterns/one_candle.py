"""1-candle pattern detection (4 bearish patterns).

Detects: Bearish Pin Bar, Gravestone Doji, Hanging Man, Shooting Star.
"""

from app.models.candle import CandleData, PatternResult
from app.services.pattern_detector import (
    _body_size,
    _candle_range,
    _is_doji,
    _is_pin_bar_bearish,
    _is_small_body,
    _lower_shadow,
    _lower_shadow_ratio,
    _upper_shadow,
    _upper_shadow_ratio,
)


def detect_1_candle(candle: CandleData) -> list[PatternResult]:
    """Detect 1-candle bearish patterns.

    Args:
        candle: Single candlestick data.

    Returns:
        List of detected PatternResult (all type="confirmed", bearish).
    """
    results: list[PatternResult] = []

    # 1. Bearish Pin Bar (B#6)
    if _is_pin_bar_bearish(candle):
        results.append(
            PatternResult(
                type="confirmed",
                name="ベアリッシュ・ピンバー",
                signal="🔽 弱気シグナル",
                description="上ヒゲが長く、高値圏での売り圧力を示唆します。",
            )
        )

    # 2. Gravestone Doji (B#11)
    cr = _candle_range(candle)
    if cr > 0 and _is_doji(candle):
        us = _upper_shadow(candle)
        ls = _lower_shadow(candle)
        if us > cr * 0.6 and ls < cr * 0.1:
            results.append(
                PatternResult(
                    type="confirmed",
                    name="トウバ（墓石十字）",
                    signal="🔽 弱気シグナル",
                    description="買い手が完全に押し戻された十字線で、天井シグナルです。",
                )
            )

    # 3. Hanging Man (B#12)
    body = _body_size(candle)
    if _is_small_body(candle) and body > 0:
        if _lower_shadow_ratio(candle) >= 2.0:
            if _upper_shadow(candle) < body * 0.3:
                results.append(
                    PatternResult(
                        type="confirmed",
                        name="首吊り線",
                        signal="🔽 弱気シグナル",
                        description="高値圏で出現する小実体・長い下ヒゲのパターンで、下落の警告です。",
                    )
                )

    # 4. Shooting Star (B#13)
    if _is_small_body(candle) and body > 0:
        if _upper_shadow_ratio(candle) >= 2.0:
            if _lower_shadow(candle) < body * 0.3:
                results.append(
                    PatternResult(
                        type="confirmed",
                        name="流れ星",
                        signal="🔽 弱気シグナル",
                        description="高値で買われた後に激しく売り戻されたパターンです。",
                    )
                )

    return results
