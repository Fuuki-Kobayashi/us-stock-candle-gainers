"""2-candle bearish pattern detection (15 patterns).

Detects bearish 2-candle patterns where c0 = previous candle, c1 = current candle.
All detected patterns have type="confirmed" and signal="🔽 弱気シグナル".
"""

from app.models.candle import CandleData, PatternResult
from app.services.pattern_detector import (
    _body_bottom,
    _body_top,
    _has_gap_down,
    _is_bearish,
    _is_bullish,
    _is_large_body,
    _is_marubozu,
    _is_small_body,
    _midpoint,
    _near_equal,
)

_SIGNAL = "🔽 弱気シグナル"
_TYPE = "confirmed"


def detect_2_candle_bearish(c0: CandleData, c1: CandleData) -> list[PatternResult]:
    """Detect 2-candle bearish patterns.

    Args:
        c0: Previous (older) candle.
        c1: Current (newer) candle.

    Returns:
        List of detected PatternResult.
    """
    results: list[PatternResult] = []

    # 1. Bearish Engulfing / 陰の陽包み (B#1)
    # c0 bullish, c1 large bearish engulfs c0 body
    if (
        _is_bullish(c0)
        and _is_bearish(c1)
        and _body_top(c1) > _body_top(c0)
        and _body_bottom(c1) < _body_bottom(c0)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="陰の陽包み",
                pattern_id="bearish_engulfing",
                signal=_SIGNAL,
                description="大陰線が前日の陽線を完全に包み込む、最も強い弱気シグナルです。",
            )
        )

    # 2. Bearish Harami / 陰の陽はらみ (B#2)
    # c0 large bullish, c1 small bearish inside c0 body
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _is_small_body(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="陰の陽はらみ",
                pattern_id="bearish_harami",
                signal=_SIGNAL,
                description="大陽線の中に小さな陰線が収まり、上昇の減速を示唆します。",
            )
        )

    # 3. Dark Cloud Cover / かぶせ線 (B#4)
    # c0 bullish, c1 bearish, c1.open > c0.high, c1.close < midpoint(c0)
    if (
        _is_bullish(c0)
        and _is_bearish(c1)
        and c1.open > c0.high
        and c1.close < _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="かぶせ線",
                pattern_id="dark_cloud_cover",
                signal=_SIGNAL,
                description="高値で始まり、前日の中間点以下まで押し戻される弱気パターンです。",
            )
        )

    # 4. Tweezers Top / 毛抜き天井 (B#5)
    # c0 bullish, c1 bearish, near_equal(c0.high, c1.high)
    if _is_bullish(c0) and _is_bearish(c1) and _near_equal(c0.high, c1.high):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="毛抜き天井",
                pattern_id="tweezers_top",
                signal=_SIGNAL,
                description="同じ高値で抵抗された2本のローソク足で、天井を示唆します。",
            )
        )

    # 5. Bearish Meeting Lines / 出会い線（弱気）(B#10)
    # c0 large bullish, c1 large bearish, near_equal(c0.close, c1.close)
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _is_large_body(c1)
        and _near_equal(c0.close, c1.close)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="出会い線（弱気）",
                pattern_id="bearish_meeting_line",
                signal=_SIGNAL,
                description="大陽線と大陰線が同じ終値付近で引け、買い勢力の押し戻しを示唆します。",
            )
        )

    # 6. Last Engulfing Top / 最後の抱き線（弱気）(B#14)
    # c0 bearish (small), c1 large bullish engulfs c0
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and _body_bottom(c1) < _body_bottom(c0)
        and _body_top(c1) > _body_top(c0)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="最後の抱き線（弱気）",
                pattern_id="bearish_last_engulfing",
                signal=_SIGNAL,
                description="上昇トレンド中の最後の買い仕掛けで、反転下落を示唆します。",
            )
        )

    # 7. Thrusting Line / 差し込み線 (B#21)
    # c0 bearish, c1 bullish, c1.open < c0.low, c1.close < midpoint(c0)
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and c1.open < c0.low
        and c1.close < _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="差し込み線",
                pattern_id="thrusting_line",
                signal=_SIGNAL,
                description="弱い買い戻しで半値にも届かず、下落の継続を示唆します。",
            )
        )

    # 8. On Neck Line / あて首線 (B#22)
    # c0 large bearish, c1 bullish, c1.open < c0.low, near_equal(c1.close, c0.close)
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and c1.open < c0.low
        and _near_equal(c1.close, c0.close)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="あて首線",
                pattern_id="on_neck_line",
                signal=_SIGNAL,
                description="大陰線の後の陽線が前日の終値付近まで戻すだけで、弱い反発です。",
            )
        )

    # 9. In Neck Line / 入り首線 (B#23)
    # c0 large bearish, c1 bullish, c1.open < c0.low, c1.close > c0.close, c1.close < midpoint(c0)
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and c1.open < c0.low
        and c1.close > c0.close
        and c1.close < _midpoint(c0)
        and not _near_equal(c1.close, c0.close)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="入り首線",
                pattern_id="in_neck_line",
                signal=_SIGNAL,
                description="大陰線の後の陽線がボディにわずかに入るだけで、弱い反発です。",
            )
        )

    # 10. Kicking Bearish / 行き違い線（弱気）(B#24)
    # c0 marubozu bullish, c1 marubozu bearish, gap down
    if (
        _is_bullish(c0)
        and _is_marubozu(c0)
        and _is_bearish(c1)
        and _is_marubozu(c1)
        and _has_gap_down(c0, c1)
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="行き違い線（弱気）",
                pattern_id="bearish_kicking",
                signal=_SIGNAL,
                description="ヒゲなし大陽線の後に窓を開けてヒゲなし大陰線が出現、パニック的下落です。",
            )
        )

    # 11. Separating Lines Bearish / 振り分線 (B#25)
    # c0 bullish, c1 bearish, near_equal(c0.open, c1.open)
    if _is_bullish(c0) and _is_bearish(c1) and _near_equal(c0.open, c1.open):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="振り分線",
                pattern_id="bearish_separating_line",
                signal=_SIGNAL,
                description="同じ始値から陽線と陰線に分かれ、売り圧力の強さを示唆します。",
            )
        )

    # 12. Downside Gap Breakout / 下降の窓開け突破 (B#26)
    # c1 large bearish, gap down from c0
    if _is_large_body(c1) and _is_bearish(c1) and _has_gap_down(c0, c1):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="下降の窓開け突破",
                pattern_id="bearish_breakaway_gap",
                signal=_SIGNAL,
                description="下方に窓を開けて大陰線が出現、下落加速を示唆します。",
            )
        )

    # 13. Downside Gap Side-by-Side Black / 下放れ並び黒 (B#19)
    # c0 bearish, c1 bearish, near_equal(c0.close, c1.open) continuation
    if _is_bearish(c0) and _is_bearish(c1) and _near_equal(c0.close, c1.open):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="下放れ並び黒",
                pattern_id="falling_twin_black",
                signal=_SIGNAL,
                description="2本の陰線が並び、下落の継続を示唆します。",
            )
        )

    # 14. Downside Tasuki Gap / 下放れタスキ線 (B#18)
    # c0 bearish, c1 bullish, c1.close < c0.open (doesn't recover)
    if _is_bearish(c0) and _is_bullish(c1) and c1.close < c0.open:
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="下放れタスキ線",
                pattern_id="bearish_tasuki_gap",
                signal=_SIGNAL,
                description="陰線の後の陽線が窓を埋めきれず、下落の継続を示唆します。",
            )
        )

    # 15. Bearish Harami Variant / 陰の陽はらみ（弱気バリアント）(B#17)
    # c0 large bullish, c1 bearish inside c0 body AND c1.close < c0.close
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bearish(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
        and c1.close < c0.close
    ):
        results.append(
            PatternResult(
                type=_TYPE,
                direction="bearish",
                pattern_candle_count=2,
                name="陰の陽はらみ（弱気バリアント）",
                pattern_id="bearish_harami_variant",
                signal=_SIGNAL,
                description="大陽線の中に陰線が収まり、終値が前日終値を下回る弱気パターンです。",
            )
        )

    return results
