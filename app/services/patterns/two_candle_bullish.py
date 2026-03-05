"""2-candle bullish pattern detection (15 patterns).

Detects bullish patterns formed by two consecutive candlesticks.
c0 = previous candle, c1 = current candle.
"""

from app.models.candle import CandleData, PatternResult
from app.services.pattern_detector import (
    _body_bottom,
    _body_top,
    _has_gap_up,
    _is_bearish,
    _is_bullish,
    _is_doji,
    _is_large_body,
    _is_marubozu,
    _is_pin_bar_bullish,
    _is_small_body,
    _midpoint,
    _near_equal,
)


def detect_2_candle_bullish(c0: CandleData, c1: CandleData) -> list[PatternResult]:
    """Detect 2-candle bullish patterns.

    Args:
        c0: Previous candle.
        c1: Current candle.

    Returns:
        List of detected PatternResult (all type="confirmed", bullish).
    """
    results: list[PatternResult] = []

    # 1. Bullish Engulfing (包み線/抱き線)
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and _body_bottom(c1) < _body_bottom(c0)
        and _body_top(c1) > _body_top(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="包み線（抱き線）",
                signal="🔼 強気シグナル",
                description="大きな陽線が前の陰線を完全に包み込み、強い反転シグナルです。",
            )
        )

    # 2. Bullish Harami (はらみ線)
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="はらみ線",
                signal="🔼 強気シグナル",
                description="大陰線の中に小陽線が収まり、弱気エネルギーの衰退を示します。",
            )
        )

    # 3. Harami Cross (はらみ寄せ線)
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_doji(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="はらみ寄せ線",
                signal="🔼 強気シグナル",
                description="大陰線の中に十字線が出現し、迷いが頂点に達した反転シグナルです。",
            )
        )

    # 4. Piercing Line (切り込み線)
    if (
        _is_bearish(c0)
        and _is_bullish(c1)
        and c1.open < c0.low
        and c1.close > _midpoint(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="切り込み線",
                signal="🔼 強気シグナル",
                description="安値を下回って始まった陽線が前日の中間点を超え、強い買い圧力を示します。",
            )
        )

    # 5. Tweezers Bottom (毛抜き底)
    if _is_bearish(c0) and _is_bullish(c1) and _near_equal(c0.low, c1.low):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="毛抜き底",
                signal="🔼 強気シグナル",
                description="同じ安値を共有する2本のローソク足で、強いサポートレベルを示します。",
            )
        )

    # 6. Bullish Meeting Lines (出会い線/逆襲線)
    if (
        _is_bearish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_large_body(c1)
        and _near_equal(c0.close, c1.close)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="出会い線（逆襲線）",
                signal="🔼 強気シグナル",
                description="大陰線と大陽線が同じ終値付近で引け、穏やかな反転シグナルです。",
            )
        )

    # 7. Matching Low (並び底/ズバリ線)
    if _is_bearish(c0) and _is_bearish(c1) and _near_equal(c0.close, c1.close):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="並び底（ズバリ線）",
                signal="🔼 強気シグナル",
                description="2本連続の陰線が同じ終値で引け、サポートの堅さを示します。",
            )
        )

    # 8. Homing Pigeon (鳩の帰巣)
    if (
        _is_bearish(c0)
        and _is_bearish(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="鳩の帰巣",
                signal="🔼 強気シグナル",
                description="2本連続の陰線で2本目が小さく、売り圧力の減少を示します。",
            )
        )

    # 9. Last Engulfing Bottom (最後の抱き線)
    if (
        _is_bullish(c0)
        and _is_bearish(c1)
        and _body_bottom(c1) < _body_bottom(c0)
        and _body_top(c1) > _body_top(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="最後の抱き線",
                signal="🔼 強気シグナル",
                description="下降トレンド中の最後の売りクライマックスシグナルです。",
            )
        )

    # 10. Tasuki Bottom (タスキ底)
    if _is_bearish(c0) and _is_bullish(c1) and c1.open < c0.close:
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="タスキ底",
                signal="🔼 強気シグナル",
                description="陰線の後に窓を開けて陽線が出現し、穏やかな底入れシグナルです。",
            )
        )

    # 11. Double Pin Bar (ダブル・ピンバー)
    if _is_pin_bar_bullish(c0) and _is_pin_bar_bullish(c1):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="ダブル・ピンバー",
                signal="🔼 強気シグナル",
                description="2本連続の下ヒゲの長いピンバーで、強い買い圧力を示します。",
            )
        )

    # 12. Kicking Bullish (行き違い線/キッキング)
    if (
        _is_marubozu(c0)
        and _is_bearish(c0)
        and _is_marubozu(c1)
        and _is_bullish(c1)
        and _has_gap_up(c0, c1)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="行き違い線（キッキング）",
                signal="🔼 強気シグナル",
                description="ヒゲなし大陰線の後に窓を開けてヒゲなし大陽線が出現し、パニック的な買い強さを示します。",
            )
        )

    # 13. Separating Lines Bullish (振り分け線)
    if _is_bearish(c0) and _is_bullish(c1) and _near_equal(c0.open, c1.open):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="振り分け線",
                signal="🔼 強気シグナル",
                description="同じ始値で陰線と陽線が分かれ、上昇トレンドの再開を示唆します。",
            )
        )

    # 14. Yang-Yang Harami (陽の陽はらみ)
    if (
        _is_bullish(c0)
        and _is_large_body(c0)
        and _is_bullish(c1)
        and _is_small_body(c1)
        and _body_bottom(c1) > _body_bottom(c0)
        and _body_top(c1) < _body_top(c0)
    ):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="陽の陽はらみ",
                signal="🔼 強気シグナル",
                description="大陽線の中に小陽線が収まり、健全な一服を示します。",
            )
        )

    # 15. Breakaway Gap Bullish (ブレイクアウェイ・ギャップ)
    if _is_bullish(c1) and _is_large_body(c1) and _has_gap_up(c0, c1):
        results.append(
            PatternResult(
                type="confirmed",
                direction="bullish",
                pattern_candle_count=2,
                name="ブレイクアウェイ・ギャップ",
                signal="🔼 強気シグナル",
                description="上方に窓を開けて大陽線が出現し、レジスタンスの突破を示します。",
            )
        )

    return results
