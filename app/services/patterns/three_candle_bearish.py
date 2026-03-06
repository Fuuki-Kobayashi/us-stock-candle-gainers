"""3-candle bearish pattern detection (11 patterns).

Detects: Evening Star, Three Black Crows, Three Inside Down,
Three Outside Down, Three Stars Top, Three Stars South (Bearish),
Inside Bar Bearish Breakout, Stick Sandwich (Bearish),
Unique Three River Top, Last Engulfing (Bearish),
Gap Down On Neck Continuation.
"""

from app.models.candle import CandleData, PatternResult
from app.services.pattern_detector import (
    _body_bottom,
    _body_top,
    _candle_range,
    _is_bearish,
    _is_bullish,
    _is_large_body,
    _is_small_body,
    _midpoint,
    _near_equal,
)


def detect_3_candle_bearish(
    c0: CandleData, c1: CandleData, c2: CandleData
) -> list[PatternResult]:
    """Detect 3-candle bearish patterns.

    Args:
        c0: Oldest candle.
        c1: Middle candle.
        c2: Newest candle.

    Returns:
        List of detected PatternResult (all type="confirmed", bearish).
    """
    results: list[PatternResult] = []

    # 1. Evening Star / Yoi no Myojo (B#3)
    # c0 large bullish, c1 small body, c2 large bearish closing below c0 midpoint
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
                direction="bearish",
                pattern_candle_count=3,
                name="宵の明星",
                pattern_id="evening_star",
                signal="🔽 弱気シグナル",
                description="上昇トレンドからの反転を示唆する3本パターンです。",
            )
        )

    # 2. Three Black Crows / Sanbagarasu (B#7)
    # All 3 bearish, each close < prev close, each open within prev body
    if (
        _is_bearish(c0)
        and _is_bearish(c1)
        and _is_bearish(c2)
        and c1.close < c0.close
        and c2.close < c1.close
        and _body_bottom(c0) <= c1.open <= _body_top(c0)
        and _body_bottom(c1) <= c2.open <= _body_top(c1)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="三羽烏（黒三兵）",
                pattern_id="three_black_crows",
                signal="🔽 弱気シグナル",
                description="3本連続の陰線で、強い下降トレンドを示唆します。",
            )
        )

    # 3. Three Inside Down (B#8)
    # c0 large bullish, c1 small bearish inside c0 body (harami),
    # c2 bearish closes below c0's body bottom (c0.open for bullish c0)
    c0_bt = _body_top(c0)
    c0_bb = _body_bottom(c0)
    c1_bt = _body_top(c1)
    c1_bb = _body_bottom(c1)
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _is_small_body(c1)
        and c1_bt <= c0_bt
        and c1_bb >= c0_bb
        and _is_bearish(c2)
        and c2.close < c0_bb
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="スリー・インサイド・ダウン",
                pattern_id="three_inside_down",
                signal="🔽 弱気シグナル",
                description="はらみ線の後に下抜けが確認された弱気パターンです。",
            )
        )

    # 4. Three Outside Down (B#9)
    # c0 small bullish, c1 large bearish engulfs c0, c2 bearish closes below c1.close
    c0_bt_s = _body_top(c0)
    c0_bb_s = _body_bottom(c0)
    if (
        _is_bullish(c0)
        and _is_small_body(c0)
        and _is_bearish(c1)
        and _is_large_body(c1)
        and _body_top(c1) >= c0_bt_s
        and _body_bottom(c1) <= c0_bb_s
        and _is_bearish(c2)
        and c2.close < c1.close
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="スリー・アウトサイド・ダウン",
                pattern_id="three_outside_down",
                signal="🔽 弱気シグナル",
                description="包み足の後に続落が確認された弱気パターンです。",
            )
        )

    # 5. Three Stars Top / Mittsu no Hoshi Tenjo (B#15)
    # All 3 small body at top area
    if _is_small_body(c0) and _is_small_body(c1) and _is_small_body(c2):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="三つの星天井",
                pattern_id="three_stars_top",
                signal="🔽 弱気シグナル",
                description="天井圏で3本連続の小実体が出現し、下落への転換を示唆します。",
            )
        )

    # 6. Three Stars in the South Bearish (B#16)
    # All 3 small bullish, range decreasing (buyers exhausting)
    r0 = _candle_range(c0)
    r1 = _candle_range(c1)
    r2 = _candle_range(c2)
    if (
        _is_bullish(c0)
        and _is_small_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and _is_bullish(c2)
        and _is_small_body(c2)
        and r0 > r1 > r2 > 0
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="南の三つ星（弱気）",
                pattern_id="three_stars_south_bearish",
                signal="🔽 弱気シグナル",
                description="3本連続の小実体陽線でレンジが縮小し、買い手の力尽きを示唆します。",
            )
        )

    # 7. Inside Bar Bearish Breakout (B#20)
    # c0 any, c1 inside c0 (harami), c2 bearish breaks below c0.low
    if (
        c1.high <= c0.high
        and c1.low >= c0.low
        and _is_bearish(c2)
        and c2.close < c0.low
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="インサイドバーの弱気ブレイク",
                pattern_id="inside_bar_bearish_break",
                signal="🔽 弱気シグナル",
                description="インサイドバーから下方にブレイクアウトした弱気パターンです。",
            )
        )

    # 8. Stick Sandwich Bearish (B#27)
    # c0 bullish, c1 bearish, c2 bullish, near_equal(c0.close, c2.close)
    if (
        _is_bullish(c0)
        and _is_bearish(c1)
        and _is_bullish(c2)
        and _near_equal(c0.close, c2.close)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="スティック・サンドイッチ（弱気）",
                pattern_id="stick_sandwich_bearish",
                signal="🔽 弱気シグナル",
                description="同じ終値で天井が確認された弱気パターンです。",
            )
        )

    # 9. Unique Three River Top / Bearish (B#28)
    # c0 large bullish, c1 small bullish inside c0, c2 small bearish
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and _body_top(c1) <= _body_top(c0)
        and _body_bottom(c1) >= _body_bottom(c0)
        and _is_bearish(c2)
        and _is_small_body(c2)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="ユニーク・スリー星・リバー（弱気）",
                pattern_id="unique_three_river_bearish",
                signal="🔽 弱気シグナル",
                description="大陽線の後に小陽線と小陰線が続く天井パターンです。",
            )
        )

    # 10. Last Engulfing Bearish (B#29)
    # c0 bullish, c1 gap up context, c2 large bearish engulfs c0
    c0_bt_e = _body_top(c0)
    c0_bb_e = _body_bottom(c0)
    c2_bt = _body_top(c2)
    c2_bb = _body_bottom(c2)
    if (
        _is_bullish(c0)
        and _is_bearish(c2)
        and _is_large_body(c2)
        and c2_bt >= c0_bt_e
        and c2_bb <= c0_bb_e
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="最後の抱き線（弱気）",
                pattern_id="last_engulfing_bearish",
                signal="🔽 弱気シグナル",
                description="窓を開けた後に大陰線が前の陽線を包む弱気パターンです。",
            )
        )

    # 11. Gap Down On Neck Continuation (B#30)
    # c0 bearish with gap down context, c1 bullish that recovers to c0.close level (on-neck),
    # c2 bearish continues decline
    tolerance = max(abs(c0.close), abs(c1.close)) * 0.02
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and c1.open < c0.close
        and abs(c1.close - c0.close) <= tolerance
        and _is_bearish(c2)
        and c2.close < c1.close
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bearish",
                pattern_candle_count=3,
                name="窓開け後の「あて首」継続",
                pattern_id="gap_neck_continuation",
                signal="🔽 弱気シグナル",
                description="窓を開けた後にあて首線で反発するも続落するパターンです。",
            )
        )

    return results
