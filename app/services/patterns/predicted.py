"""Predicted pattern detection (26 patterns = 15 bullish + 11 bearish precursors).

Detects 2-candle precursors of 3-candle patterns, returning type="predicted"
with required_third describing the condition for the 3rd candle.
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
)


def _fmt(price: float) -> str:
    """Format price for display."""
    if price >= 100:
        return f"${price:.2f}"
    return f"${price:.2f}"


def detect_predicted(c0: CandleData, c1: CandleData) -> list[PatternResult]:
    """Detect predicted (precursor) patterns from 2 candles.

    Args:
        c0: Older candle.
        c1: Newer candle.

    Returns:
        List of detected PatternResult (all type="predicted").
    """
    results: list[PatternResult] = []

    c0_bt = _body_top(c0)
    c0_bb = _body_bottom(c0)
    c1_bt = _body_top(c1)
    c1_bb = _body_bottom(c1)
    c0_mid = (c0_bt + c0_bb) / 2

    # =========================================================================
    # Bullish precursors (15)
    # =========================================================================

    # 1. Morning Star Predicted
    if _is_bearish(c0) and _is_large_body(c0) and _is_small_body(c1):
        target = c0_mid
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="明けの明星予測",
                signal="🔼 強気シグナル（予測）",
                description="明けの明星の初期形成が見られます。",
                required_third=f"3本目に大陽線（終値 > {_fmt(target)}）が出現すれば完成",
            )
        )

    # 2. Morning Doji Star Predicted
    if _is_bearish(c0) and _is_large_body(c0) and _is_doji(c1):
        target = c0_mid
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="明けの十字星予測",
                signal="🔼 強気シグナル（予測）",
                description="明けの十字星の初期形成が見られます。",
                required_third=f"3本目に大陽線（終値 > {_fmt(target)}）が出現すれば完成",
            )
        )

    # 3. Abandoned Baby Bottom Predicted
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_doji(c1)
        and _has_gap_down(c0, c1)
    ):
        gap_line = c1.high
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="捨て子底予測",
                signal="🔼 強気シグナル（予測）",
                description="捨て子底の初期形成が見られます。",
                required_third=(
                    f"3本目に窓を開けた大陽線"
                    f"（始値 > {_fmt(gap_line)}）が出現すれば完成"
                ),
            )
        )

    # 4. Three White Soldiers Predicted
    if _is_bullish(c0) and _is_bullish(c1) and c1.close > c0.close:
        target = c1.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="赤三兵予測",
                signal="🔼 強気シグナル（予測）",
                description="赤三兵の初期形成が見られます。",
                required_third=(f"3本目も陽線で終値が {_fmt(target)} を上回れば完成"),
            )
        )

    # 5. Three Inside Up Predicted
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and c1_bt <= c0_bt
        and c1_bb >= c0_bb
    ):
        target = c0.open
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="スリー・インサイド・アップ予測",
                signal="🔼 強気シグナル（予測）",
                description="スリー・インサイド・アップの初期形成（はらみ線）が見られます。",
                required_third=(f"3本目の陽線の終値が {_fmt(target)} を上回れば完成"),
            )
        )

    # 6. Three Outside Up Predicted
    if (
        _is_bearish(c0)
        and _is_small_body(c0)
        and _is_bullish(c1)
        and _is_large_body(c1)
        and c1_bt >= c0_bt
        and c1_bb <= c0_bb
    ):
        target = c1.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="スリー・アウトサイド・アップ予測",
                signal="🔼 強気シグナル（予測）",
                description="スリー・アウトサイド・アップの初期形成（包み線）が見られます。",
                required_third=(f"3本目の陽線の終値が {_fmt(target)} を上回れば完成"),
            )
        )

    # 7. Morning Pin Bar Predicted
    if _is_bearish(c0) and _is_large_body(c0) and _is_pin_bar_bullish(c1):
        target = c0_mid
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="モーニング・ピンバー予測",
                signal="🔼 強気シグナル（予測）",
                description="モーニング・ピンバー・リバーサルの初期形成が見られます。",
                required_third=(
                    f"3本目に大陽線（終値 > {_fmt(target)}）が出現すれば完成"
                ),
            )
        )

    # 8. Three Stars Bottom Predicted
    if _is_small_body(c0) and _is_small_body(c1):
        c1_range = _candle_range(c1)
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="三つの星底予測",
                signal="🔼 強気シグナル（予測）",
                description="三つの星底の初期形成が見られます。",
                required_third=(f"3本目も小実体（値幅 < {_fmt(c1_range)}）なら完成"),
            )
        )

    # 9. Stick Sandwich Bullish Predicted
    if _is_bearish(c0) and _is_bullish(c1):
        target = c0.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="スティック・サンドイッチ予測",
                signal="🔼 強気シグナル（予測）",
                description="スティック・サンドイッチの初期形成が見られます。",
                required_third=(f"3本目の陰線の終値が {_fmt(target)} 付近なら完成"),
            )
        )

    # 10. Three Stars in South Predicted
    if _is_bearish(c0) and _is_bearish(c1) and _candle_range(c1) < _candle_range(c0):
        c1_range = _candle_range(c1)
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="南の三つ星予測",
                signal="🔼 強気シグナル（予測）",
                description="南の三つ星の初期形成が見られます。",
                required_third=(f"3本目も陰線で値幅が {_fmt(c1_range)} 未満なら完成"),
            )
        )

    # 11. Unique Three River Predicted
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _is_small_body(c1)
        and c1_bt <= c0_bt
        and c1_bb >= c0_bb
    ):
        target = c1.low
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="ユニーク・スリー・リバー予測",
                signal="🔼 強気シグナル（予測）",
                description="ユニーク・スリー・リバーの初期形成が見られます。",
                required_third=(f"3本目の小陽線の終値が {_fmt(target)} より上なら完成"),
            )
        )

    # 12. Downside Gap Three Methods Predicted
    if _is_bearish(c0) and _is_bearish(c1) and _has_gap_down(c0, c1):
        gap_top = c0.low
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="下放れ三法予測",
                signal="🔼 強気シグナル（予測）",
                description="下放れ三法の初期形成が見られます。",
                required_third=(f"3本目の陽線が窓（{_fmt(gap_top)}）を埋めれば完成"),
            )
        )

    # 13. Upside Tasuki Gap Predicted
    if _is_bullish(c0) and _is_bullish(c1) and _has_gap_up(c0, c1):
        gap_bottom = c0.high
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="上放れタスキ線予測",
                signal="🔼 強気シグナル（予測）",
                description="上放れタスキ線の初期形成が見られます。",
                required_third=(
                    f"3本目の陰線の終値が {_fmt(gap_bottom)} を下回らなければ完成"
                ),
            )
        )

    # 14. Upside Gap Side-by-Side White Predicted
    if _is_bullish(c1) and _has_gap_up(c0, c1):
        target = c1.open
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="上放れ並び赤予測",
                signal="🔼 強気シグナル（予測）",
                description="上放れ並び赤の初期形成が見られます。",
                required_third=(f"3本目も陽線（始値 ≈ {_fmt(target)}）なら完成"),
            )
        )

    # 15. Inside Bar Bullish Breakout Predicted
    if c1.high <= c0.high and c1.low >= c0.low:
        target = c0.high
        results.append(
            PatternResult(
                type="predicted",
                direction="bullish",
                pattern_candle_count=3,
                name="インサイドバー上抜け予測",
                signal="🔼 強気シグナル（予測）",
                description="インサイドバーの上抜けの初期形成が見られます。",
                required_third=(f"3本目の陽線の終値が {_fmt(target)} を上回れば完成"),
            )
        )

    # =========================================================================
    # Bearish precursors (11)
    # =========================================================================

    # 1. Evening Star Predicted
    if _is_bullish(c0) and _is_large_body(c0) and _is_small_body(c1):
        target = c0_mid
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="宵の明星予測",
                signal="🔽 弱気シグナル（予測）",
                description="宵の明星の初期形成が見られます。",
                required_third=(
                    f"3本目に大陰線（終値 < {_fmt(target)}）が出現すれば完成"
                ),
            )
        )

    # 2. Three Black Crows Predicted
    if _is_bearish(c0) and _is_bearish(c1) and c1.close < c0.close:
        target = c1.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="三羽烏予測",
                signal="🔽 弱気シグナル（予測）",
                description="三羽烏の初期形成が見られます。",
                required_third=(f"3本目も陰線で終値が {_fmt(target)} を下回れば完成"),
            )
        )

    # 3. Three Inside Down Predicted
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _is_small_body(c1)
        and c1_bt <= c0_bt
        and c1_bb >= c0_bb
    ):
        target = c0.open
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="スリー・インサイド・ダウン予測",
                signal="🔽 弱気シグナル（予測）",
                description="スリー・インサイド・ダウンの初期形成（はらみ線）が見られます。",
                required_third=(f"3本目の陰線の終値が {_fmt(target)} を下回れば完成"),
            )
        )

    # 4. Three Outside Down Predicted
    if (
        _is_bullish(c0)
        and _is_small_body(c0)
        and _is_bearish(c1)
        and _is_large_body(c1)
        and c1_bt >= c0_bt
        and c1_bb <= c0_bb
    ):
        target = c1.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="スリー・アウトサイド・ダウン予測",
                signal="🔽 弱気シグナル（予測）",
                description="スリー・アウトサイド・ダウンの初期形成（包み足）が見られます。",
                required_third=(f"3本目の陰線の終値が {_fmt(target)} を下回れば完成"),
            )
        )

    # 5. Three Stars Top Predicted
    if _is_small_body(c0) and _is_small_body(c1):
        c1_range = _candle_range(c1)
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="三つの星天井予測",
                signal="🔽 弱気シグナル（予測）",
                description="三つの星天井の初期形成が見られます。",
                required_third=(f"3本目も小実体（値幅 < {_fmt(c1_range)}）なら完成"),
            )
        )

    # 6. Three Stars South Bearish Predicted
    if (
        _is_bullish(c0)
        and _is_small_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and _candle_range(c1) < _candle_range(c0)
    ):
        c1_range = _candle_range(c1)
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="南の三つ星（弱気）予測",
                signal="🔽 弱気シグナル（予測）",
                description="南の三つ星（弱気）の初期形成が見られます。",
                required_third=(f"3本目も小実体で値幅が {_fmt(c1_range)} 未満なら完成"),
            )
        )

    # 7. Inside Bar Bearish Predicted
    if c1.high <= c0.high and c1.low >= c0.low:
        target = c0.low
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="インサイドバー弱気予測",
                signal="🔽 弱気シグナル（予測）",
                description="インサイドバーの弱気ブレイクの初期形成が見られます。",
                required_third=(f"3本目の陰線の終値が {_fmt(target)} を下回れば完成"),
            )
        )

    # 8. Stick Sandwich Bearish Predicted
    if _is_bullish(c0) and _is_bearish(c1):
        target = c0.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="スティック・サンドイッチ（弱気）予測",
                signal="🔽 弱気シグナル（予測）",
                description="スティック・サンドイッチ（弱気）の初期形成が見られます。",
                required_third=(f"3本目の陽線の終値が {_fmt(target)} 付近なら完成"),
            )
        )

    # 9. Unique Three River Top Predicted
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
    ):
        target = c1.low
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="ユニーク・スリー星・リバー（弱気）予測",
                signal="🔽 弱気シグナル（予測）",
                description="ユニーク・スリー星・リバー（弱気）の初期形成が見られます。",
                required_third=(
                    f"3本目に小陰線（終値 < {_fmt(target)}）が出現すれば完成"
                ),
            )
        )

    # 10. Last Engulfing Bearish Predicted
    if _is_bullish(c0) and _has_gap_up(c0, c1):
        target_open = c0.close
        target_close = c0.open
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="最後の抱き線（弱気）予測",
                signal="🔽 弱気シグナル（予測）",
                description="最後の抱き線（弱気）の初期形成が見られます。",
                required_third=(
                    f"3本目の大陰線（始値 > {_fmt(target_open)}、"
                    f"終値 < {_fmt(target_close)}）でc0を包めば完成"
                ),
            )
        )

    # 11. Gap Down On Neck Continuation Predicted
    tolerance = max(abs(c0.close), abs(c1.close)) * 0.02
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and c1.open < c0.close
        and abs(c1.close - c0.close) <= tolerance
    ):
        target = c1.close
        results.append(
            PatternResult(
                type="predicted",
                direction="bearish",
                pattern_candle_count=3,
                name="窓開け後あて首継続予測",
                signal="🔽 弱気シグナル（予測）",
                description="窓開け後のあて首継続パターンの初期形成が見られます。",
                required_third=(f"3本目の陰線の終値が {_fmt(target)} を下回れば完成"),
            )
        )

    return results
