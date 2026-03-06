"""Unit-03: 2-candle bearish pattern detection tests (15 patterns)."""

from app.services.patterns.two_candle_bearish import detect_2_candle_bearish
from tests.conftest import (
    make_bullish_large,
    make_candle,
    make_marubozu_bullish,
)

# --- 1. Bearish Engulfing / Yin no You Tsutsumi (B#1) ---


def test_bearish_engulfing_detected():
    """c0 bullish, c1 large bearish engulfs c0 body -> detected."""
    c0 = make_candle(open=100.0, high=106.0, low=99.0, close=105.0)
    # c0 bullish, body: bottom=100, top=105
    c1 = make_candle(open=106.0, high=107.0, low=98.0, close=99.0)
    # c1 bearish, body: top=106, bottom=99 -> engulfs c0 body (99 < 100, 106 > 105)
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "陰の陽包み" for r in results)
    match = next(r for r in results if r.name == "陰の陽包み")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"
    assert match.direction == "bearish"
    assert match.pattern_candle_count == 2
    assert match.pattern_id == "bearish_engulfing"


def test_bearish_engulfing_not_detected_partial():
    """c1 does not fully engulf c0 body -> not detected."""
    c0 = make_candle(open=100.0, high=106.0, low=99.0, close=105.0)
    # c0 body: bottom=100, top=105
    c1 = make_candle(open=104.0, high=106.0, low=100.0, close=101.0)
    # c1 body: top=104, bottom=101 -> does NOT engulf (101 > 100, 104 < 105)
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "陰の陽包み" for r in results)


# --- 2. Bearish Harami / Yin no You Harami (B#2) ---


def test_bearish_harami_detected():
    """c0 large bullish, c1 small bearish inside c0 body -> detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, high=112, low=98, close=110 -> body top=110, bottom=100
    c1 = make_candle(open=107.0, high=108.0, low=102.0, close=104.0)
    # c1: bearish, body_ratio=3/6=0.5... too large. Use smaller body.
    c1 = make_candle(open=106.0, high=108.0, low=103.0, close=105.0)
    # c1: bearish (close<open), body=1, range=5, ratio=0.2 (small)
    # body: top=106, bottom=105 -> inside c0 body [100, 110]
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "陰の陽はらみ" for r in results)
    match = next(r for r in results if r.name == "陰の陽はらみ")
    assert match.pattern_id == "bearish_harami"


def test_bearish_harami_not_detected_outside():
    """c1 body extends outside c0 body -> not detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: body top=110, bottom=100
    c1 = make_candle(open=111.0, high=113.0, low=104.0, close=106.0)
    # c1 body top=111 > c0 body top=110 -> outside
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "陰の陽はらみ" for r in results)


# --- 3. Dark Cloud Cover / Kabuse-sen (B#4) ---


def test_dark_cloud_cover_detected():
    """c0 bullish, c1 bearish opens above c0.high, closes below c0 midpoint."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=109.0)
    # c0 bullish, midpoint=(100+109)/2=104.5
    c1 = make_candle(open=111.0, high=112.0, low=102.0, close=103.0)
    # c1 bearish, open=111 > c0.high=110, close=103 < midpoint=104.5
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "かぶせ線" for r in results)
    match = next(r for r in results if r.name == "かぶせ線")
    assert match.pattern_id == "dark_cloud_cover"


def test_dark_cloud_cover_not_detected_above_midpoint():
    """c1 closes above c0 midpoint -> not detected."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=109.0)
    # midpoint = 104.5
    c1 = make_candle(open=111.0, high=112.0, low=105.0, close=106.0)
    # close=106 > midpoint=104.5
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "かぶせ線" for r in results)


# --- 4. Tweezers Top / Kenuki Tenjo (B#5) ---


def test_tweezers_top_detected():
    """c0 bullish, c1 bearish, same high -> detected."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=108.0)
    c1 = make_candle(open=107.0, high=110.0, low=101.0, close=102.0)
    # both have high=110, c0 bullish, c1 bearish
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "毛抜き天井" for r in results)
    match = next(r for r in results if r.name == "毛抜き天井")
    assert match.pattern_id == "tweezers_top"


def test_tweezers_top_not_detected_diff_high():
    """Different highs -> not detected."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=108.0)
    c1 = make_candle(open=107.0, high=115.0, low=101.0, close=102.0)
    # highs differ: 110 vs 115 (not near_equal)
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "毛抜き天井" for r in results)


# --- 5. Bearish Meeting Lines / Deai-sen Bearish (B#10) ---


def test_meeting_lines_bearish_detected():
    """c0 large bullish, c1 large bearish, same close -> detected."""
    c0 = make_candle(open=90.0, high=102.0, low=89.0, close=100.0)
    # c0 large bullish (body_ratio=10/13~0.77)
    c1 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c1 large bearish (body_ratio=10/14~0.71), close=100=c0.close
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "出会い線（弱気）" for r in results)
    match = next(r for r in results if r.name == "出会い線（弱気）")
    assert match.pattern_id == "bearish_meeting_line"


def test_meeting_lines_bearish_not_detected_diff_close():
    """Closes are far apart -> not detected."""
    c0 = make_candle(open=90.0, high=102.0, low=89.0, close=100.0)
    c1 = make_candle(open=110.0, high=112.0, low=89.0, close=92.0)
    # closes differ: 100 vs 92
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "出会い線（弱気）" for r in results)


# --- 6. Last Engulfing Top / Saigo no Daki-sen Bearish (B#14) ---


def test_last_engulfing_top_detected():
    """c0 small bearish, c1 large bullish engulfs c0 -> detected."""
    c0 = make_candle(open=101.0, high=103.0, low=99.0, close=100.0)
    # c0 bearish (small), body: top=101, bottom=100
    c1 = make_candle(open=99.0, high=108.0, low=98.0, close=107.0)
    # c1 bullish, body: top=107, bottom=99 -> engulfs c0 body (99 < 100, 107 > 101)
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "最後の抱き線（弱気）" for r in results)
    match = next(r for r in results if r.name == "最後の抱き線（弱気）")
    assert match.pattern_id == "bearish_last_engulfing"


def test_last_engulfing_top_not_detected_not_engulfing():
    """c1 does not engulf c0 -> not detected."""
    c0 = make_candle(open=101.0, high=103.0, low=99.0, close=100.0)
    c1 = make_candle(open=100.5, high=102.0, low=100.0, close=101.5)
    # c1 body: top=101.5, bottom=100.5 -> doesn't engulf c0 body [100, 101]
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "最後の抱き線（弱気）" for r in results)


# --- 7. Thrusting Line / Sashikomi-sen (B#21) ---


def test_thrusting_line_detected():
    """c0 bearish, c1 bullish, c1.open < c0.low, c1.close < midpoint(c0)."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=101.0)
    # c0 bearish, midpoint=(110+101)/2=105.5
    c1 = make_candle(open=99.0, high=104.0, low=98.0, close=103.0)
    # c1 bullish, open=99 < c0.low=100, close=103 < midpoint=105.5
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "差し込み線" for r in results)
    match = next(r for r in results if r.name == "差し込み線")
    assert match.pattern_id == "thrusting_line"


def test_thrusting_line_not_detected_above_half():
    """c1 closes above c0 midpoint -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=101.0)
    # midpoint=105.5
    c1 = make_candle(open=99.0, high=108.0, low=98.0, close=107.0)
    # close=107 > midpoint=105.5
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "差し込み線" for r in results)


# --- 8. On Neck Line / Ate-kubi-sen (B#22) ---


def test_on_neck_line_detected():
    """c0 large bearish, c1 bullish, c1.open < c0.low, c1.close ~= c0.close."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c0 large bearish
    c1 = make_candle(open=97.0, high=101.0, low=96.0, close=100.0)
    # c1 bullish, open=97 < c0.low=98, close=100 ~= c0.close=100
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "あて首線" for r in results)
    match = next(r for r in results if r.name == "あて首線")
    assert match.pattern_id == "on_neck_line"


def test_on_neck_line_not_detected_too_far():
    """c1.close is far from c0.close -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    c1 = make_candle(open=97.0, high=107.0, low=96.0, close=106.0)
    # c1.close=106 far from c0.close=100
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "あて首線" for r in results)


# --- 9. In Neck Line / Iri-kubi-sen (B#23) ---


def test_in_neck_line_detected():
    """c0 large bearish, c1 bullish, c1.open < c0.low, c1.close slightly above c0.close but below midpoint."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c0 large bearish, midpoint=(110+100)/2=105
    c1 = make_candle(open=97.0, high=103.0, low=96.0, close=101.5)
    # c1 bullish, open=97 < c0.low=98, close=101.5 > c0.close=100, close < midpoint=105
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "入り首線" for r in results)
    match = next(r for r in results if r.name == "入り首線")
    assert match.pattern_id == "in_neck_line"


def test_in_neck_line_not_detected_too_deep():
    """c1 closes above c0 midpoint -> too deep -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # midpoint=105
    c1 = make_candle(open=97.0, high=108.0, low=96.0, close=107.0)
    # close=107 > midpoint=105 -> too deep
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "入り首線" for r in results)


# --- 10. Kicking Bearish / Iki-chigai-sen Bearish (B#24) ---


def test_kicking_bearish_detected():
    """c0 marubozu bullish, c1 marubozu bearish, gap down -> detected."""
    c0 = make_marubozu_bullish(base=100.0)
    # c0: open=100, high=110.1, low=99.9, close=110 (marubozu bullish)
    c1 = make_candle(open=99.0, high=99.1, low=88.9, close=89.0)
    # c1: marubozu bearish (body_ratio=10/10.2~0.98), gap down (c1.high=99.1 < c0.low=99.9)
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "行き違い線（弱気）" for r in results)
    match = next(r for r in results if r.name == "行き違い線（弱気）")
    assert match.pattern_id == "bearish_kicking"


def test_kicking_bearish_not_detected_with_shadow():
    """c1 has significant shadows -> not detected."""
    c0 = make_marubozu_bullish(base=100.0)
    c1 = make_candle(open=99.0, high=105.0, low=80.0, close=89.0)
    # c1: body=10, range=25, body_ratio=0.4 (not marubozu)
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "行き違い線（弱気）" for r in results)


# --- 11. Separating Lines Bearish / Furiwake-sen (B#25) ---


def test_separating_lines_bearish_detected():
    """c0 bullish, c1 bearish, same open -> detected."""
    c0 = make_candle(open=105.0, high=112.0, low=104.0, close=110.0)
    c1 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    # same open=105, c0 bullish, c1 bearish
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "振り分線" for r in results)
    match = next(r for r in results if r.name == "振り分線")
    assert match.pattern_id == "bearish_separating_line"


def test_separating_lines_bearish_not_detected_diff_open():
    """Different opens -> not detected."""
    c0 = make_candle(open=105.0, high=112.0, low=104.0, close=110.0)
    c1 = make_candle(open=100.0, high=106.0, low=93.0, close=95.0)
    # opens differ: 105 vs 100
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "振り分線" for r in results)


# --- 12. Downside Gap Breakout / Kako no Madoake Toppa (B#26) ---


def test_downside_gap_breakout_detected():
    """c1 large bearish with gap down from c0 -> detected."""
    c0 = make_candle(open=100.0, high=105.0, low=98.0, close=103.0)
    c1 = make_candle(open=96.0, high=97.0, low=84.0, close=86.0)
    # c1 large bearish (body_ratio=10/13~0.77), gap down (c1.high=97 < c0.low=98)
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "下降の窓開け突破" for r in results)
    match = next(r for r in results if r.name == "下降の窓開け突破")
    assert match.pattern_id == "bearish_breakaway_gap"


def test_downside_gap_breakout_not_detected_no_gap():
    """No gap between c0 and c1 -> not detected."""
    c0 = make_candle(open=100.0, high=105.0, low=98.0, close=103.0)
    c1 = make_candle(open=99.0, high=100.0, low=86.0, close=88.0)
    # c1.high=100 > c0.low=98 -> no gap
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "下降の窓開け突破" for r in results)


# --- 13. Downside Gap Side-by-Side Black / Sagarehanarebikuro (B#19) ---


def test_downside_gap_side_by_side_black_detected():
    """c0 bearish, c1 bearish, _near_equal(c0.close, c1.open) continuation after gap."""
    c0 = make_candle(open=105.0, high=106.0, low=93.0, close=95.0)
    # c0 bearish
    c1 = make_candle(open=95.0, high=96.0, low=85.0, close=87.0)
    # c1 bearish, c1.open=95 ~= c0.close=95 -> continuation
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "下放れ並び黒" for r in results)
    match = next(r for r in results if r.name == "下放れ並び黒")
    assert match.pattern_id == "falling_twin_black"


def test_downside_gap_side_by_side_black_not_detected_no_continuation():
    """c0 and c1 opens are far apart -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=93.0, close=95.0)
    c1 = make_candle(open=102.0, high=103.0, low=90.0, close=92.0)
    # c1.open=102 != c0.close=95 (not near_equal)
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "下放れ並び黒" for r in results)


# --- 14. Downside Tasuki Gap / Sagarehanaretasuki (B#18) ---


def test_downside_tasuki_gap_detected():
    """c0 bearish, c1 bullish, c1.close < c0.open -> gap not recovered."""
    c0 = make_candle(open=105.0, high=106.0, low=93.0, close=95.0)
    # c0 bearish
    c1 = make_candle(open=94.0, high=102.0, low=93.0, close=100.0)
    # c1 bullish, close=100 < c0.open=105 (doesn't recover to c0's open)
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "下放れタスキ線" for r in results)
    match = next(r for r in results if r.name == "下放れタスキ線")
    assert match.pattern_id == "bearish_tasuki_gap"


def test_downside_tasuki_gap_not_detected_gap_filled():
    """c1 closes above c0.open -> gap filled -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=93.0, close=95.0)
    c1 = make_candle(open=94.0, high=108.0, low=93.0, close=107.0)
    # c1.close=107 >= c0.open=105 -> gap filled
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "下放れタスキ線" for r in results)


# --- 15. Bearish Harami Variant / Yin no You Harami Bearish Variant (B#17) ---


def test_bearish_harami_variant_detected():
    """c0 large bullish, c1 bearish inside c0 body AND c1.close < c0.close."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, close=110, body=[100, 110]
    c1 = make_candle(open=108.0, high=109.0, low=104.0, close=105.0)
    # c1 bearish, body=[105, 108] inside c0 body [100, 110]
    # c1.close=105 < c0.close=110 -> shows weakness
    results = detect_2_candle_bearish(c0, c1)
    assert any(r.name == "陰の陽はらみ（弱気バリアント）" for r in results)
    match = next(r for r in results if r.name == "陰の陽はらみ（弱気バリアント）")
    assert match.pattern_id == "bearish_harami_variant"


def test_bearish_harami_variant_not_detected_no_breakdown():
    """c1 is not bearish or not inside c0 -> not detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, close=110
    c1 = make_candle(open=105.0, high=112.0, low=104.0, close=111.0)
    # c1 bullish, close=111 > c0.close=110 -> not showing weakness
    results = detect_2_candle_bearish(c0, c1)
    assert not any(r.name == "陰の陽はらみ（弱気バリアント）" for r in results)
