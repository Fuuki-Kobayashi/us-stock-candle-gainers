"""Unit-04: 3-candle bullish pattern detection tests (15 patterns)."""

from app.services.patterns.three_candle_bullish import detect_3_candle_bullish
from tests.conftest import (
    make_bearish_large,
    make_bullish_large,
    make_candle,
    make_doji,
    make_small_body,
)

# --- 1. Morning Star / Ake no Myojo (#16) ---


def test_morning_star_detected():
    """Large bearish -> small body -> large bullish -> detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, high=112, low=98, close=100
    c1 = make_small_body(base=98.0, bullish=True)
    # c1: open=98, close=100, small body at bottom
    c2 = make_bullish_large(base=99.0)
    # c2: open=99, close=109, large bullish
    # c2.close=109 > midpoint(c0)=(110+100)/2=105
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "明けの明星" for r in results)
    match = next(r for r in results if r.name == "明けの明星")
    assert match.type == "confirmed"
    assert match.signal == "🔼 強気シグナル"


def test_morning_star_not_detected_c2_not_large():
    """3rd candle is small -> not detected."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_small_body(base=98.0, bullish=True)
    c2 = make_small_body(base=99.0, bullish=True)  # small, not large
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "明けの明星" for r in results)


# --- 2. Morning Doji Star / Ake no Jujisei (#17) ---


def test_morning_doji_star_detected():
    """Large bearish -> doji -> large bullish -> detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100
    c1 = make_doji(base=98.0)
    # c1: doji at bottom
    c2 = make_bullish_large(base=99.0)
    # c2: close=109 > midpoint(c0)=105
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "明けの十字星" for r in results)


def test_morning_doji_star_not_detected_c1_not_doji():
    """2nd candle is not a doji -> not detected."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_candle(open=98.0, high=105.0, low=95.0, close=103.0)
    # c1 body_ratio=5/10=0.5 -> not doji
    c2 = make_bullish_large(base=99.0)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "明けの十字星" for r in results)


# --- 3. Abandoned Baby Bottom / Sutego-zoko (#18) ---


def test_abandoned_baby_bottom_detected():
    """Large bearish -> gap-down doji -> gap-up large bullish -> detected."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=101.0)
    # c0 large bearish
    c1 = make_candle(open=98.0, high=99.0, low=97.0, close=98.1)
    # c1 doji (body_ratio=0.1/2=0.05), gap down from c0 (c1.high=99 < c0.low=100)
    c2 = make_candle(open=100.0, high=112.0, low=99.5, close=110.0)
    # c2 large bullish, gap up from c1 (c2.low=99.5 > c1.high=99)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "捨て子底" for r in results)


def test_abandoned_baby_bottom_not_detected_no_gap():
    """No gap between candles -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=101.0)
    c1 = make_candle(open=101.0, high=102.0, low=100.0, close=101.1)
    # c1.high=102 > c0.low=100 -> no gap down
    c2 = make_bullish_large(base=99.0)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "捨て子底" for r in results)


# --- 4. Three White Soldiers / Aka Sanpei (#19) ---


def test_three_white_soldiers_detected():
    """3 consecutive bullish, each close > prev close, each open within prev body."""
    c0 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    # c0 bullish, body=[100, 110]
    c1 = make_candle(open=105.0, high=122.0, low=103.0, close=120.0)
    # c1 bullish, open=105 in c0 body [100,110], close=120 > c0.close=110
    c2 = make_candle(open=115.0, high=132.0, low=113.0, close=130.0)
    # c2 bullish, open=115 in c1 body [105,120], close=130 > c1.close=120
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "赤三兵" for r in results)


def test_three_white_soldiers_not_detected_descending():
    """Close prices descending -> not detected."""
    c0 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    c1 = make_candle(open=105.0, high=110.0, low=103.0, close=108.0)
    # c1.close=108 < c0.close=110 -> descending
    c2 = make_candle(open=106.0, high=110.0, low=104.0, close=107.0)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "赤三兵" for r in results)


# --- 5. Three Inside Up (#20) ---


def test_three_inside_up_detected():
    """Large bearish -> small bullish inside (harami) -> bullish closes above c0.open."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100, body=[100, 110]
    c1 = make_candle(open=102.0, high=106.0, low=101.0, close=105.0)
    # c1 bullish, body=[102, 105] inside c0 body [100, 110]
    c2 = make_candle(open=106.0, high=115.0, low=105.0, close=113.0)
    # c2 bullish, close=113 > c0.open=110
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "スリー・インサイド・アップ" for r in results)


def test_three_inside_up_not_detected_no_breakout():
    """3rd candle doesn't close above c0.open -> not detected."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_candle(open=102.0, high=106.0, low=101.0, close=105.0)
    c2 = make_candle(open=104.0, high=108.0, low=103.0, close=107.0)
    # c2.close=107 < c0.open=110 -> no breakout
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "スリー・インサイド・アップ" for r in results)


# --- 6. Three Outside Up (#21) ---


def test_three_outside_up_detected():
    """Small bearish -> large bullish engulfs -> bullish closes above c1.close."""
    c0 = make_small_body(base=105.0, bullish=False)
    # c0: open=105, close=103, small bearish
    c1 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    # c1: large bullish, body=[100, 110] engulfs c0 body [103, 105]
    c2 = make_candle(open=111.0, high=118.0, low=110.0, close=115.0)
    # c2 bullish, close=115 > c1.close=110
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "スリー・アウトサイド・アップ" for r in results)


def test_three_outside_up_not_detected_no_continuation():
    """3rd candle doesn't continue upward -> not detected."""
    c0 = make_small_body(base=105.0, bullish=False)
    c1 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    c2 = make_candle(open=109.0, high=110.0, low=104.0, close=105.0)
    # c2.close=105 < c1.close=110 -> no continuation
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "スリー・アウトサイド・アップ" for r in results)


# --- 7. Morning Pin Bar Reversal (#22) ---


def test_morning_pin_bar_reversal_detected():
    """Large bearish -> bullish pin bar -> large bullish -> detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100
    # Custom pin bar: body=1, lower_shadow=8, upper_shadow=0 (satisfies ratio>=2 and upper<body*0.5)
    c1 = make_candle(open=99.0, high=100.0, low=91.0, close=99.8)
    # body=0.8, lower=8, upper=0.2, ratio=10>=2, 0.2<0.8*0.5=0.4 YES
    c2 = make_bullish_large(base=99.0)
    # c2: open=99, close=109, large bullish
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "モーニング・ピンバー・リバーサル" for r in results)


def test_morning_pin_bar_reversal_not_detected_no_pin():
    """2nd candle is not a pin bar -> not detected."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_candle(open=100.0, high=108.0, low=95.0, close=106.0)
    # c1: large body, not pin bar
    c2 = make_bullish_large(base=99.0)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "モーニング・ピンバー・リバーサル" for r in results)


# --- 8. Three Stars Bottom / Mittsu no Hoshi Zoko (#23) ---


def test_three_stars_bottom_detected():
    """3 consecutive small bodies (doji-like) at bottom -> detected."""
    c0 = make_small_body(base=100.0, bullish=False)
    # c0: small body
    c1 = make_small_body(base=99.0, bullish=True)
    # c1: small body
    c2 = make_small_body(base=99.5, bullish=True)
    # c2: small body
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "三つの星底" for r in results)


def test_three_stars_bottom_not_detected_large_body():
    """One candle has a large body -> not detected."""
    c0 = make_small_body(base=100.0, bullish=False)
    c1 = make_bullish_large(base=100.0)  # large body
    c2 = make_small_body(base=105.0, bullish=True)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "三つの星底" for r in results)


# --- 9. Stick Sandwich Bullish (#24) ---


def test_stick_sandwich_bullish_detected():
    """Bearish -> bullish -> bearish, c0.close ~= c2.close -> detected."""
    c0 = make_candle(open=105.0, high=106.0, low=98.0, close=100.0)
    # c0 bearish
    c1 = make_candle(open=99.0, high=108.0, low=98.0, close=106.0)
    # c1 bullish
    c2 = make_candle(open=105.0, high=106.0, low=98.0, close=100.0)
    # c2 bearish, close=100 ~= c0.close=100
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "スティック・サンドイッチ" for r in results)


def test_stick_sandwich_bullish_not_detected_diff_close():
    """c0.close and c2.close differ significantly -> not detected."""
    c0 = make_candle(open=105.0, high=106.0, low=98.0, close=100.0)
    c1 = make_candle(open=99.0, high=108.0, low=98.0, close=106.0)
    c2 = make_candle(open=105.0, high=106.0, low=90.0, close=92.0)
    # c2.close=92 != c0.close=100
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "スティック・サンドイッチ" for r in results)


# --- 10. Three Stars in the South / Minami no Mittsu Boshi (#25) ---


def test_three_stars_in_south_detected():
    """3 consecutive bearish candles, each range smaller than previous -> detected."""
    c0 = make_candle(open=110.0, high=112.0, low=96.0, close=98.0)
    # c0 bearish, range=16
    c1 = make_candle(open=100.0, high=101.0, low=90.0, close=92.0)
    # c1 bearish, range=11
    c2 = make_candle(open=93.0, high=94.0, low=87.0, close=89.0)
    # c2 bearish, range=7
    # ranges: 16 > 11 > 7 -> decreasing
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "南の三つ星" for r in results)


def test_three_stars_in_south_not_detected_expanding():
    """Ranges expanding -> not detected."""
    c0 = make_candle(open=110.0, high=111.0, low=105.0, close=106.0)
    # c0 bearish, range=6
    c1 = make_candle(open=108.0, high=110.0, low=98.0, close=100.0)
    # c1 bearish, range=12
    c2 = make_candle(open=102.0, high=105.0, low=85.0, close=88.0)
    # c2 bearish, range=20 -> expanding
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "南の三つ星" for r in results)


# --- 11. Unique Three River Bottom (#26) ---


def test_unique_three_river_bottom_detected():
    """Large bearish -> small bearish inside c0 (harami) -> small bullish with close > c1.low."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100, body=[100, 110]
    c1 = make_candle(open=107.0, high=108.0, low=101.0, close=103.0)
    # c1: bearish, body=[103, 107] inside c0 body [100, 110]
    c2 = make_candle(open=102.0, high=104.0, low=101.5, close=103.0)
    # c2: bullish, close=103 > c1.low=101
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "ユニーク・スリー・リバー" for r in results)


def test_unique_three_river_bottom_not_detected_no_harami():
    """c1 is not inside c0 body -> not detected."""
    c0 = make_bearish_large(base=100.0)
    # c0: body=[100, 110]
    c1 = make_candle(open=112.0, high=115.0, low=105.0, close=106.0)
    # c1 body top=112 > c0 body top=110 -> not harami
    c2 = make_candle(open=105.0, high=107.0, low=104.0, close=106.0)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "ユニーク・スリー・リバー" for r in results)


# --- 12. Downside Gap Three Methods / Sagarehare Sanpou (#27) ---


def test_downside_gap_three_methods_detected():
    """c0 bearish, c1 bearish with gap down, c2 bullish fills gap (c2.close >= c0.close)."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=102.0)
    # c0 bearish
    c1 = make_candle(open=98.0, high=99.0, low=88.0, close=90.0)
    # c1 bearish, gap down (c1.high=99 < c0.low=100)
    c2 = make_candle(open=91.0, high=106.0, low=90.0, close=104.0)
    # c2 bullish, close=104 >= c0.close=102 -> fills gap
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "下放れ三法" for r in results)


def test_downside_gap_three_methods_not_detected_no_fill():
    """c2 doesn't fill the gap -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=102.0)
    c1 = make_candle(open=98.0, high=99.0, low=88.0, close=90.0)
    # gap down
    c2 = make_candle(open=91.0, high=100.0, low=90.0, close=98.0)
    # c2.close=98 < c0.close=102 -> doesn't fill
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "下放れ三法" for r in results)


# --- 13. Upside Tasuki Gap / Agarehare Tasuki (#28) ---


def test_upside_tasuki_gap_detected():
    """c0 bullish, c1 bullish with gap up, c2 bearish doesn't fill gap (c2.close > c0.high)."""
    c0 = make_candle(open=100.0, high=110.0, low=98.0, close=108.0)
    # c0 bullish
    c1 = make_candle(open=112.0, high=120.0, low=111.0, close=118.0)
    # c1 bullish, gap up (c1.low=111 > c0.high=110)
    c2 = make_candle(open=117.0, high=118.0, low=112.0, close=113.0)
    # c2 bearish, close=113 > c0.high=110 -> gap not filled
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "上放れタスキ線" for r in results)


def test_upside_tasuki_gap_not_detected_gap_filled():
    """c2 closes below c0.high -> gap filled -> not detected."""
    c0 = make_candle(open=100.0, high=110.0, low=98.0, close=108.0)
    c1 = make_candle(open=112.0, high=120.0, low=111.0, close=118.0)
    c2 = make_candle(open=117.0, high=118.0, low=105.0, close=108.0)
    # c2.close=108 < c0.high=110 -> gap filled
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "上放れタスキ線" for r in results)


# --- 14. Upside Gap Side-by-Side White / Agarehare Narabikaka (#29) ---


def test_upside_gap_side_by_side_white_detected():
    """c0 any, c1 bullish with gap up from c0, c2 bullish -> detected."""
    c0 = make_candle(open=100.0, high=108.0, low=98.0, close=106.0)
    # c0 any
    c1 = make_candle(open=110.0, high=118.0, low=109.0, close=116.0)
    # c1 bullish, gap up (c1.low=109 > c0.high=108)
    c2 = make_candle(open=115.0, high=122.0, low=114.0, close=120.0)
    # c2 bullish
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "上放れ並び赤" for r in results)


def test_upside_gap_side_by_side_white_not_detected_no_gap():
    """No gap up between c0 and c1 -> not detected."""
    c0 = make_candle(open=100.0, high=108.0, low=98.0, close=106.0)
    c1 = make_candle(open=107.0, high=115.0, low=105.0, close=113.0)
    # c1.low=105 < c0.high=108 -> no gap
    c2 = make_candle(open=112.0, high=120.0, low=111.0, close=118.0)
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "上放れ並び赤" for r in results)


# --- 15. Inside Bar Bullish Breakout (#30) ---


def test_inside_bar_bullish_breakout_detected():
    """c0 any, c1 inside c0 (harami), c2 bullish breaks above c0.high."""
    c0 = make_candle(open=100.0, high=115.0, low=90.0, close=110.0)
    # c0: large range
    c1 = make_candle(open=105.0, high=112.0, low=93.0, close=102.0)
    # c1: inside c0 (high=112 < c0.high=115, low=93 > c0.low=90)
    c2 = make_candle(open=108.0, high=120.0, low=107.0, close=118.0)
    # c2 bullish, close=118 > c0.high=115 -> breaks above
    results = detect_3_candle_bullish(c0, c1, c2)
    assert any(r.name == "インサイドバーの上抜け" for r in results)


def test_inside_bar_bullish_breakout_not_detected_no_break():
    """3rd candle doesn't break above c0.high -> not detected."""
    c0 = make_candle(open=100.0, high=115.0, low=90.0, close=110.0)
    c1 = make_candle(open=105.0, high=112.0, low=93.0, close=102.0)
    c2 = make_candle(open=104.0, high=113.0, low=103.0, close=110.0)
    # c2.close=110 < c0.high=115 -> not breaking above
    results = detect_3_candle_bullish(c0, c1, c2)
    assert not any(r.name == "インサイドバーの上抜け" for r in results)
