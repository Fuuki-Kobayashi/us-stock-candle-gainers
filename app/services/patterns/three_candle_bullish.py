"""3-candle bullish pattern detection (15 patterns).

Detects bullish 3-candle patterns where c0 = oldest, c1 = middle, c2 = newest.
All detected patterns have type="confirmed" and signal="🔼 強気シグナル".
"""

from app.models.candle import CandleData, PatternResult
from app.services.pattern_detector import (
    _body_bottom,
    _body_top,
    _candle_range,
    _has_gap_down,
    _has_gap_up,
    _is_bearish,
    _is_bullish,
    _is_doji,
    _is_large_body,
    _is_pin_bar_bullish,
    _is_small_body,
    _midpoint,
    _near_equal,
)

_SIGNAL = "🔼 強気シグナル"
_TYPE = "confirmed"


def detect_3_candle_bullish(
    c0: CandleData, c1: CandleData, c2: CandleData
) -> list[PatternResult]:
    """Detect 3-candle bullish patterns.

    Args:
        c0: Oldest candle.
        c1: Middle candle.
        c2: Newest candle.

    Returns:
        List of detected PatternResult.
    """
    results: list[PatternResult] = []

    # 1. Morning Star / 明けの明星 (#16)
    # c0 large bearish, c1 small body, c2 large bullish, c2.close > midpoint(c0)
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
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="明けの明星",
                signal=_SIGNAL,
                description="下降トレンドからの反転を示唆する3本パターンです。",
            )
        )

    # 2. Morning Doji Star / 明けの十字星 (#17)
    # c0 large bearish, c1 doji, c2 large bullish, c2.close > midpoint(c0)
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_doji(c1)
        and _is_bullish(c2)
        and _is_large_body(c2)
        and c2.close > _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="明けの十字星",
                signal=_SIGNAL,
                description="大陰線の後に十字線、そして大陽線が出現する強い反転シグナルです。",
            )
        )

    # 3. Abandoned Baby Bottom / 捨て子底 (#18)
    # c0 large bearish, c1 doji with gap down, c2 large bullish with gap up
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_doji(c1)
        and _has_gap_down(c0, c1)
        and _is_bullish(c2)
        and _is_large_body(c2)
        and _has_gap_up(c1, c2)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="捨て子底",
                signal=_SIGNAL,
                description="窓を開けた十字線が前後のローソク足から孤立する、最も強い底値シグナルです。",
            )
        )

    # 4. Three White Soldiers / 赤三兵 (#19)
    # All 3 bullish, each close > prev close, each open within prev body
    if (
        _is_bullish(c0)
        and _is_bullish(c1)
        and _is_bullish(c2)
        and c1.close > c0.close
        and c2.close > c1.close
        and _body_bottom(c0) <= c1.open <= _body_top(c0)
        and _body_bottom(c1) <= c2.open <= _body_top(c1)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="赤三兵",
                signal=_SIGNAL,
                description="3本連続の陽線で、強い上昇トレンドを示唆します。",
            )
        )

    # 5. Three Inside Up / スリー・インサイド・アップ (#20)
    # c0 large bearish, c1 small bullish inside c0 body (harami), c2 bullish closes above c0.open
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
        and _is_bullish(c2)
        and c2.close > c0.open
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="スリー・インサイド・アップ（D3S）",
                signal=_SIGNAL,
                description="はらみ線の後に上抜ける陽線で、安全な反転確認です。",
            )
        )

    # 6. Three Outside Up / スリー・アウトサイド・アップ (#21)
    # c0 small bearish, c1 large bullish engulfs c0, c2 bullish closes above c1.close
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and _is_large_body(c1)
        and _body_bottom(c1) < _body_bottom(c0)
        and _body_top(c1) > _body_top(c0)
        and _is_bullish(c2)
        and c2.close > c1.close
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="スリー・アウトサイド・アップ",
                signal=_SIGNAL,
                description="包み線の後に続伸する陽線で、強い反転確認です。",
            )
        )

    # 7. Morning Pin Bar Reversal / モーニング・ピンバー・リバーサル (#22)
    # c0 large bearish, c1 bullish pin bar, c2 large bullish
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_pin_bar_bullish(c1)
        and _is_bullish(c2)
        and _is_large_body(c2)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="モーニング・ピンバー・リバーサル",
                signal=_SIGNAL,
                description="大陰線の後にピンバーが出現し、V字回復を示唆します。",
            )
        )

    # 8. Three Stars Bottom / 三つの星底 (#23)
    # All 3 small body (doji-like) at bottom
    if _is_small_body(c0) and _is_small_body(c1) and _is_small_body(c2):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="三つの星底",
                signal=_SIGNAL,
                description="3本連続の小実体で、エネルギーが溜まり上昇への爆発を示唆します。",
            )
        )

    # 9. Stick Sandwich Bullish / スティック・サンドイッチ (#24)
    # c0 bearish, c1 bullish, c2 bearish, near_equal(c0.close, c2.close)
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and _is_bearish(c2)
        and _near_equal(c0.close, c2.close)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="スティック・サンドイッチ",
                signal=_SIGNAL,
                description="短期的なW底を形成する反転パターンです。",
            )
        )

    # 10. Three Stars in the South / 南の三つ星 (#25)
    # All 3 bearish, each range smaller than previous
    if (
        _is_bearish(c0)
        and _is_bearish(c1)
        and _is_bearish(c2)
        and _candle_range(c1) < _candle_range(c0)
        and _candle_range(c2) < _candle_range(c1)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="南の三つ星",
                signal=_SIGNAL,
                description="3本連続の陰線でレンジが縮小し、売り手の力尽きを示唆します。",
            )
        )

    # 11. Unique Three River Bottom / ユニーク・スリー・リバー (#26)
    # c0 large bearish, c1 small bearish inside c0 body (harami), c2 small bullish close > c1.low
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
        and _is_bullish(c2)
        and c2.close > c1.low
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="ユニーク・スリー・リバー",
                signal=_SIGNAL,
                description="大陰線の後にはらみ小陰線、そして小陽線で徐々に底打ちを示唆します。",
            )
        )

    # 12. Downside Gap Three Methods / 下放れ三法 (#27)
    # c0 bearish, c1 bearish with gap down, c2 bullish fills gap (c2.close >= c0.close)
    if (
        _is_bearish(c0)
        and _is_bearish(c1)
        and _has_gap_down(c0, c1)
        and _is_bullish(c2)
        and c2.close >= c0.close
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="下放れ三法",
                signal=_SIGNAL,
                description="下方窓を開けた2本の陰線の後、陽線が窓を埋めて反発を示唆します。",
            )
        )

    # 13. Upside Tasuki Gap / 上放れタスキ線 (#28)
    # c0 bullish, c1 bullish with gap up, c2 bearish doesn't fill gap (c2.close > c0.high)
    if (
        _is_bullish(c0)
        and _is_bullish(c1)
        and _has_gap_up(c0, c1)
        and _is_bearish(c2)
        and c2.close > c0.high
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="上放れタスキ線",
                signal=_SIGNAL,
                description="上方窓の後の押し目で窓を埋めず、優れた押し目買いの機会です。",
            )
        )

    # 14. Upside Gap Side-by-Side White / 上放れ並び赤 (#29)
    # c0 any, c1 bullish with gap up from c0, c2 bullish
    if _is_bullish(c1) and _has_gap_up(c0, c1) and _is_bullish(c2):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="上放れ並び赤",
                signal=_SIGNAL,
                description="上方窓の後に2本の陽線が並び、極めて強い上昇エネルギーを示唆します。",
            )
        )

    # 15. Inside Bar Bullish Breakout / インサイドバーの上抜け (#30)
    # c0 any, c1 inside c0 (harami), c2 bullish breaks above c0.high
    if c1.high < c0.high and c1.low > c0.low and _is_bullish(c2) and c2.close > c0.high:
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bullish",
                pattern_candle_count=3,
                name="インサイドバーの上抜け",
                signal=_SIGNAL,
                description="インサイドバーからの上方ブレイクアウトで、トレンド継続を示唆します。",
            )
        )

    return results
