"""Unit-02: 2-candle bullish pattern detection tests (15 patterns)."""

from app.services.patterns.two_candle_bullish import detect_2_candle_bullish
from tests.conftest import (
    make_bearish_large,
    make_bullish_large,
    make_candle,
    make_marubozu_bearish,
)

# --- 1. Bullish Engulfing (包み線/抱き線) ---


def test_bullish_engulfing_detected():
    """c0 bearish, c1 bullish engulfs c0 body -> detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    # c0 body: top=105, bottom=100
    c1 = make_candle(open=99.0, high=107.0, low=98.0, close=106.0)
    # c1 body: top=106, bottom=99 -> engulfs c0 body (99 < 100, 106 > 105)
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "包み線（抱き線）" for r in results)
    match = next(r for r in results if r.name == "包み線（抱き線）")
    assert match.type == "confirmed"
    assert match.signal == "🔼 強気シグナル"
    assert match.direction == "bullish"
    assert match.pattern_candle_count == 2


def test_bullish_engulfing_not_detected_partial():
    """c1 does not fully engulf c0 body -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    # c0 body: top=105, bottom=100
    c1 = make_candle(open=101.0, high=106.0, low=100.0, close=104.0)
    # c1 body: top=104, bottom=101 -> does NOT engulf (101 > 100, but 104 < 105)
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "包み線（抱き線）" for r in results)


# --- 2. Bullish Harami (はらみ線) ---


def test_bullish_harami_detected():
    """c0 large bearish, c1 small bullish inside c0 body -> detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, high=112, low=98, close=100 -> body top=110, bottom=100
    c1 = make_candle(open=102.0, high=104.0, low=101.0, close=103.0)
    # c1: body top=103, bottom=102 -> inside c0 body (102>100, 103<110)
    # c1 body_ratio = 1/3 ~ 0.33 ... need small body
    c1 = make_candle(open=103.0, high=105.0, low=101.0, close=104.0)
    # c1: body=1, range=4, body_ratio=0.25 (small)
    # body_bottom=103 > 100, body_top=104 < 110
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "はらみ線" for r in results)


def test_bullish_harami_not_detected_outside():
    """c1 body extends outside c0 body -> not detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100 -> body top=110, bottom=100
    c1 = make_candle(open=99.0, high=106.0, low=98.0, close=100.5)
    # c1 body bottom=99 < c0 body bottom=100 -> outside
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "はらみ線" for r in results)


# --- 3. Harami Cross (はらみ寄せ線) ---


def test_harami_cross_detected():
    """c0 large bearish, c1 doji inside c0 body -> detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: body top=110, bottom=100
    c1 = make_candle(open=105.0, high=107.0, low=103.0, close=105.2)
    # c1: body_ratio=0.2/4=0.05 (doji), body within 100-110
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "はらみ寄せ線" for r in results)


def test_harami_cross_not_detected_not_doji():
    """c1 is not a doji -> not detected as harami cross."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_candle(open=102.0, high=108.0, low=101.0, close=106.0)
    # c1: body=4, range=7, body_ratio=0.57 (not doji)
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "はらみ寄せ線" for r in results)


# --- 4. Piercing Line (切り込み線) ---


def test_piercing_line_detected():
    """c0 bearish, c1 bullish opens below c0.low, closes above c0 midpoint."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=101.0)
    # c0 bearish, midpoint=(110+101)/2=105.5
    c1 = make_candle(open=99.0, high=108.0, low=98.0, close=107.0)
    # c1 bullish, open=99 < c0.low=100, close=107 > midpoint=105.5
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "切り込み線" for r in results)


def test_piercing_line_not_detected_below_midpoint():
    """c1 closes below c0 midpoint -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=101.0)
    # midpoint = 105.5
    c1 = make_candle(open=99.0, high=104.0, low=98.0, close=103.0)
    # close=103 < midpoint=105.5
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "切り込み線" for r in results)


# --- 5. Tweezers Bottom (毛抜き底) ---


def test_tweezers_bottom_detected():
    """c0 bearish, c1 bullish, same low -> detected."""
    c0 = make_candle(open=105.0, high=107.0, low=100.0, close=101.0)
    c1 = make_candle(open=101.0, high=106.0, low=100.0, close=105.0)
    # both have low=100.0, c0 bearish, c1 bullish
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "毛抜き底" for r in results)


def test_tweezers_bottom_not_detected_diff_low():
    """Different lows -> not detected."""
    c0 = make_candle(open=105.0, high=107.0, low=100.0, close=101.0)
    c1 = make_candle(open=101.0, high=106.0, low=97.0, close=105.0)
    # lows differ: 100.0 vs 97.0 (not near_equal)
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "毛抜き底" for r in results)


# --- 6. Bullish Meeting Lines (出会い線/逆襲線) ---


def test_meeting_lines_bullish_detected():
    """c0 large bearish, c1 large bullish, same close -> detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c0 large bearish (body_ratio=10/14~0.71)
    c1 = make_candle(open=90.0, high=102.0, low=89.0, close=100.0)
    # c1 large bullish (body_ratio=10/13~0.77), close=100=c0.close
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "出会い線（逆襲線）" for r in results)


def test_meeting_lines_bullish_not_detected_diff_close():
    """Closes are far apart -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    c1 = make_candle(open=90.0, high=108.0, low=89.0, close=106.0)
    # closes differ: 100 vs 106 (not near_equal)
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "出会い線（逆襲線）" for r in results)


# --- 7. Matching Low (並び底/ズバリ線) ---


def test_matching_low_detected():
    """Two consecutive bearish candles with same close -> detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    c1 = make_candle(open=103.0, high=104.0, low=99.0, close=100.0)
    # both bearish, same close=100
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "並び底（ズバリ線）" for r in results)


def test_matching_low_not_detected_diff_close():
    """Different closes -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    c1 = make_candle(open=103.0, high=104.0, low=96.0, close=97.0)
    # closes differ: 100 vs 97
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "並び底（ズバリ線）" for r in results)


# --- 8. Homing Pigeon (鳩の帰巣) ---


def test_homing_pigeon_detected():
    """Two bearish candles, c1 body inside c0 body -> detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c0 body: top=110, bottom=100
    c1 = make_candle(open=108.0, high=109.0, low=101.0, close=102.0)
    # c1 body: top=108, bottom=102 -> inside c0 (102>100, 108<110)
    # both bearish
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "鳩の帰巣" for r in results)


def test_homing_pigeon_not_detected_outside():
    """c1 body extends outside c0 body -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    c1 = make_candle(open=112.0, high=113.0, low=99.0, close=101.0)
    # c1 body top=112 > c0 body top=110 -> outside
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "鳩の帰巣" for r in results)


# --- 9. Last Engulfing Bottom (最後の抱き線) ---


def test_last_engulfing_bottom_detected():
    """c0 small bullish, c1 large bearish engulfs c0 -> detected."""
    c0 = make_candle(open=100.0, high=103.0, low=99.0, close=101.0)
    # c0 bullish (close>open), small body=1
    c1 = make_candle(open=102.0, high=103.0, low=97.0, close=98.0)
    # c1 bearish, body: top=102, bottom=98
    # engulfs c0 body: 98 < 100 and 102 > 101
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "最後の抱き線" for r in results)


def test_last_engulfing_bottom_not_detected_not_engulfing():
    """c1 does not engulf c0 -> not detected."""
    c0 = make_candle(open=100.0, high=103.0, low=99.0, close=101.0)
    c1 = make_candle(open=101.5, high=102.0, low=100.5, close=100.8)
    # c1 body: top=101.5, bottom=100.8 -> does NOT engulf c0 (100.8 > 100)
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "最後の抱き線" for r in results)


# --- 10. Tasuki Bottom (タスキ底) ---


def test_tasuki_bottom_detected():
    """c0 bearish, c1 bullish opens below c0.close (gap down reversal)."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    # c0 bearish
    c1 = make_candle(open=98.0, high=104.0, low=97.0, close=103.0)
    # c1 bullish, open=98 < c0.close=100 (gap down then reversal up)
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "タスキ底" for r in results)


def test_tasuki_bottom_not_detected_no_gap():
    """c1 opens at or above c0.close -> no gap -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    c1 = make_candle(open=101.0, high=106.0, low=100.0, close=105.0)
    # c1 open=101 > c0.close=100 -> no gap down
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "タスキ底" for r in results)


# --- 11. Double Pin Bar (ダブル・ピンバー) ---


def test_double_pin_bar_detected():
    """Both c0 and c1 are bullish pin bars -> detected."""
    c0 = make_candle(open=101.0, high=102.0, low=92.0, close=101.5)
    # body=0.5, lower_shadow=9 (ratio=18 >= 2.0), upper=0.5 < 0.5*0.5=0.25?
    # upper=0.5, body*0.5=0.25 -> 0.5 > 0.25... not pin bar
    # Fix: make upper shadow smaller
    c0 = make_candle(open=101.0, high=101.2, low=92.0, close=101.1)
    # body=0.1, lower_shadow=9 (ratio=90 >= 2.0), upper=0.1 < 0.1*0.5=0.05? NO
    # Need body > 0 and upper < body*0.5
    c0 = make_candle(open=100.0, high=101.0, low=90.0, close=100.8)
    # body=0.8, lower_shadow=10 (ratio=12.5 >= 2.0), upper=0.2 < 0.8*0.5=0.4 YES
    c1 = make_candle(open=99.0, high=100.0, low=89.0, close=99.8)
    # body=0.8, lower_shadow=10 (ratio=12.5 >= 2.0), upper=0.2 < 0.8*0.5=0.4 YES
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "ダブル・ピンバー" for r in results)


def test_double_pin_bar_not_detected_one_pin():
    """Only one candle is a pin bar -> not detected."""
    c0 = make_candle(open=100.0, high=101.0, low=90.0, close=100.8)
    # c0 is bullish pin bar
    c1 = make_candle(open=100.0, high=110.0, low=95.0, close=108.0)
    # c1 has large body, not a pin bar
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "ダブル・ピンバー" for r in results)


# --- 12. Kicking Bullish (行き違い線/キッキング) ---


def test_kicking_bullish_detected():
    """c0 marubozu bearish, c1 marubozu bullish, gap up -> detected."""
    c0 = make_marubozu_bearish(base=100.0)
    # c0: open=110, high=110.1, low=99.9, close=100 (marubozu bearish)
    c1 = make_candle(open=111.0, high=121.1, low=110.9, close=121.0)
    # c1: marubozu bullish (body_ratio=10/10.2~0.98), gap up (c1.low=110.9 > c0.high=110.1)
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "行き違い線（キッキング）" for r in results)


def test_kicking_bullish_not_detected_with_shadow():
    """c1 has significant shadows (not marubozu) -> not detected."""
    c0 = make_marubozu_bearish(base=100.0)
    c1 = make_candle(open=111.0, high=130.0, low=105.0, close=121.0)
    # c1: body=10, range=25, body_ratio=0.4 (not marubozu)
    # gap up exists but c1 is not marubozu
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "行き違い線（キッキング）" for r in results)


# --- 13. Separating Lines Bullish (振り分け線) ---


def test_separating_lines_bullish_detected():
    """c0 bearish, c1 bullish, same open -> detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    c1 = make_candle(open=105.0, high=112.0, low=104.0, close=110.0)
    # same open=105, c0 bearish, c1 bullish
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "振り分け線" for r in results)


def test_separating_lines_bullish_not_detected_diff_open():
    """Different opens -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=99.0, close=100.0)
    c1 = make_candle(open=100.0, high=112.0, low=99.0, close=110.0)
    # opens differ: 105 vs 100
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "振り分け線" for r in results)


# --- 14. Yang-Yang Harami (陽の陽はらみ) ---


def test_yang_yang_harami_detected():
    """c0 large bullish, c1 small bullish inside c0 body -> detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, high=112, low=98, close=110 -> body top=110, bottom=100
    c1 = make_candle(open=103.0, high=106.0, low=102.0, close=104.0)
    # c1 bullish, small body=1, body_ratio=1/4=0.25
    # body: top=104, bottom=103 -> inside c0 (103>100, 104<110)
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "陽の陽はらみ" for r in results)


def test_yang_yang_harami_not_detected_outside():
    """c1 body extends outside c0 body -> not detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: body top=110, bottom=100
    c1 = make_candle(open=99.0, high=106.0, low=98.0, close=100.5)
    # c1 body bottom=99 < c0 body bottom=100 -> outside
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "陽の陽はらみ" for r in results)


# --- 15. Breakaway Gap Bullish (ブレイクアウェイ・ギャップ) ---


def test_breakaway_gap_bullish_detected():
    """c1 large bullish with gap up from c0 -> detected."""
    c0 = make_candle(open=100.0, high=105.0, low=98.0, close=103.0)
    c1 = make_candle(open=106.0, high=118.0, low=105.5, close=116.0)
    # c1 large bullish (body_ratio=10/12.5=0.8), gap up (c1.low=105.5 > c0.high=105.0)
    results = detect_2_candle_bullish(c0, c1)
    assert any(r.name == "ブレイクアウェイ・ギャップ" for r in results)


def test_breakaway_gap_bullish_not_detected_no_gap():
    """No gap between c0 and c1 -> not detected."""
    c0 = make_candle(open=100.0, high=105.0, low=98.0, close=103.0)
    c1 = make_candle(open=104.0, high=116.0, low=103.0, close=114.0)
    # c1.low=103 < c0.high=105 -> no gap
    results = detect_2_candle_bullish(c0, c1)
    assert not any(r.name == "ブレイクアウェイ・ギャップ" for r in results)
