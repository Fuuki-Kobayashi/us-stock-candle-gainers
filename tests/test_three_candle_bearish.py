"""Unit-05: 3-candle bearish pattern detection tests (11 patterns)."""

from app.services.patterns.three_candle_bearish import detect_3_candle_bearish
from tests.conftest import make_bullish_large, make_candle, make_small_body

# --- Evening Star / Yoi no Myojo (B#3) ---


def test_evening_star_detected():
    """Large bullish -> small body -> large bearish -> Evening Star detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, high=112, low=98, close=110
    c1 = make_small_body(base=112.0, bullish=True)
    # c1: open=112, high=117, low=107, close=114 (small body at top)
    c2 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c2: large bearish, close < midpoint(c0)=(100+110)/2=105
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "宵の明星" for r in results)
    match = next(r for r in results if r.name == "宵の明星")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_evening_star_not_detected_c2_not_large():
    """3rd candle is small -> not detected."""
    c0 = make_bullish_large(base=100.0)
    c1 = make_small_body(base=112.0, bullish=True)
    c2 = make_small_body(base=108.0, bullish=False)  # small body, not large bearish
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "宵の明星" for r in results)


# --- Three Black Crows / Sanbagarasu (B#7) ---


def test_three_black_crows_detected():
    """3 consecutive bearish candles, each closing lower, each opening within prev body."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c0 bearish, body: 100-110
    c1 = make_candle(open=105.0, high=107.0, low=93.0, close=95.0)
    # c1 bearish, open=105 within c0 body [100,110], close=95 < c0.close=100
    c2 = make_candle(open=100.0, high=102.0, low=88.0, close=90.0)
    # c2 bearish, open=100 within c1 body [95,105], close=90 < c1.close=95
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "三羽烏（黒三兵）" for r in results)
    match = next(r for r in results if r.name == "三羽烏（黒三兵）")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_three_black_crows_not_detected_ascending():
    """Close prices ascending -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    c1 = make_candle(open=105.0, high=107.0, low=98.0, close=102.0)
    # c1.close=102 > c0.close=100 -> ascending
    c2 = make_candle(open=106.0, high=108.0, low=100.0, close=104.0)
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "三羽烏（黒三兵）" for r in results)


# --- Three Inside Down (B#8) ---


def test_three_inside_down_detected():
    """Large bullish -> small bearish inside (harami) -> bearish closes below c0.close."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, close=110, body=[100,110]
    c1 = make_candle(open=108.0, high=110.0, low=100.0, close=105.0)
    # c1: bearish, body=[105,108] body_ratio=3/10=0.3 (small), inside c0 body [100,110]
    c2 = make_candle(open=102.0, high=103.0, low=95.0, close=97.0)
    # c2: bearish, close=97 < c0's body bottom=100
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "スリー・インサイド・ダウン" for r in results)
    match = next(r for r in results if r.name == "スリー・インサイド・ダウン")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_three_inside_down_not_detected_no_breakdown():
    """3rd candle doesn't close below c0 open -> not detected."""
    c0 = make_bullish_large(base=100.0)
    c1 = make_candle(open=108.0, high=109.0, low=101.0, close=103.0)
    c2 = make_candle(open=105.0, high=108.0, low=102.0, close=106.0)
    # c2.close=106 > c0.open=100 -> not breaking down
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "スリー・インサイド・ダウン" for r in results)


# --- Three Outside Down (B#9) ---


def test_three_outside_down_detected():
    """Small bullish -> large bearish engulfs -> bearish closes below c1.close."""
    c0 = make_small_body(base=105.0, bullish=True)
    # c0: open=105, close=107, small bullish
    c1 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c1: large bearish, body=[100,110] engulfs c0 body [105,107]
    c2 = make_candle(open=99.0, high=100.0, low=93.0, close=95.0)
    # c2: bearish, close=95 < c1.close=100
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "スリー・アウトサイド・ダウン" for r in results)
    match = next(r for r in results if r.name == "スリー・アウトサイド・ダウン")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_three_outside_down_not_detected_no_continuation():
    """3rd candle doesn't continue decline -> not detected."""
    c0 = make_small_body(base=105.0, bullish=True)
    c1 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    c2 = make_candle(open=101.0, high=106.0, low=100.0, close=105.0)
    # c2.close=105 > c1.close=100 -> not continuing
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "スリー・アウトサイド・ダウン" for r in results)


# --- Three Stars Top / Mittsu no Hoshi Tenjo (B#15) ---


def test_three_stars_top_detected():
    """3 consecutive small bodies at top area -> Three Stars Top detected."""
    c0 = make_small_body(base=150.0, bullish=True)
    # c0: open=150, close=152, small body
    c1 = make_small_body(base=151.0, bullish=True)
    # c1: open=151, close=153, small body
    c2 = make_small_body(base=150.5, bullish=False)
    # c2: open=150.5, close=148.5, small body
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "三つの星天井" for r in results)
    match = next(r for r in results if r.name == "三つの星天井")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_three_stars_top_not_detected_large_body():
    """One candle has a large body -> not detected."""
    c0 = make_small_body(base=150.0, bullish=True)
    c1 = make_bullish_large(base=150.0)  # large body
    c2 = make_small_body(base=155.0, bullish=False)
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "三つの星天井" for r in results)


# --- Three Stars in the South Bearish (B#16) ---


def test_three_stars_south_bearish_detected():
    """3 consecutive small bullish candles, range decreasing -> detected."""
    c0 = make_candle(open=100.0, high=106.0, low=94.0, close=102.0)
    # range=12, small body (body=2, ratio=2/12=0.17)
    c1 = make_candle(open=101.0, high=105.0, low=96.0, close=102.5)
    # range=9, small body (body=1.5, ratio=1.5/9=0.17)
    c2 = make_candle(open=101.5, high=104.0, low=98.0, close=102.8)
    # range=6, small body (body=1.3, ratio=1.3/6=0.22)
    # ranges: 12 > 9 > 6 -> decreasing
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "南の三つ星（弱気）" for r in results)
    match = next(r for r in results if r.name == "南の三つ星（弱気）")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_three_stars_south_bearish_not_detected_not_bullish():
    """Candles are bearish -> not detected (pattern requires bullish)."""
    c0 = make_candle(open=102.0, high=106.0, low=94.0, close=100.0)
    # bearish
    c1 = make_candle(open=101.0, high=104.0, low=96.0, close=99.0)
    c2 = make_candle(open=100.0, high=103.0, low=97.0, close=98.0)
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "南の三つ星（弱気）" for r in results)


# --- Inside Bar Bearish Breakout (B#20) ---


def test_inside_bar_bearish_breakout_detected():
    """Any candle -> inside bar (harami) -> bearish breaks below c0.low."""
    c0 = make_candle(open=100.0, high=115.0, low=90.0, close=110.0)
    # c0: large range, body=[100,110]
    c1 = make_candle(open=105.0, high=108.0, low=95.0, close=102.0)
    # c1: inside c0 (high=108 < c0.high=115, low=95 > c0.low=90)
    c2 = make_candle(open=94.0, high=95.0, low=85.0, close=87.0)
    # c2: bearish, close=87 < c0.low=90 -> breaks below
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "インサイドバーの弱気ブレイク" for r in results)
    match = next(r for r in results if r.name == "インサイドバーの弱気ブレイク")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_inside_bar_bearish_breakout_not_detected_no_break():
    """3rd candle doesn't break below c0.low -> not detected."""
    c0 = make_candle(open=100.0, high=115.0, low=90.0, close=110.0)
    c1 = make_candle(open=105.0, high=108.0, low=95.0, close=102.0)
    c2 = make_candle(open=100.0, high=103.0, low=95.0, close=97.0)
    # c2.close=97 > c0.low=90 -> not breaking below
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "インサイドバーの弱気ブレイク" for r in results)


# --- Stick Sandwich Bearish (B#27) ---


def test_stick_sandwich_bearish_detected():
    """Bullish -> bearish -> bullish, c0.close ~= c2.close (ceiling confirmed)."""
    c0 = make_candle(open=98.0, high=112.0, low=97.0, close=110.0)
    # c0: bullish
    c1 = make_candle(open=112.0, high=113.0, low=103.0, close=105.0)
    # c1: bearish
    c2 = make_candle(open=103.0, high=112.0, low=102.0, close=110.0)
    # c2: bullish, close=110 ~= c0.close=110
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "スティック・サンドイッチ（弱気）" for r in results)
    match = next(r for r in results if r.name == "スティック・サンドイッチ（弱気）")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_stick_sandwich_bearish_not_detected_diff_close():
    """c0.close and c2.close differ significantly -> not detected."""
    c0 = make_candle(open=98.0, high=112.0, low=97.0, close=110.0)
    c1 = make_candle(open=112.0, high=113.0, low=103.0, close=105.0)
    c2 = make_candle(open=103.0, high=120.0, low=102.0, close=118.0)
    # c2.close=118 != c0.close=110
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "スティック・サンドイッチ（弱気）" for r in results)


# --- Unique Three River Top / Bearish (B#28) ---


def test_unique_three_river_top_detected():
    """Large bullish -> small bullish inside c0 -> small bearish -> detected."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, close=110, large bullish
    c1 = make_candle(open=105.0, high=110.0, low=100.0, close=107.0)
    # c1: bullish, body=[105,107] body_ratio=2/10=0.2 (small), inside c0 body [100,110]
    c2 = make_candle(open=106.0, high=110.0, low=100.0, close=104.0)
    # c2: bearish, body=[104,106] body_ratio=2/10=0.2 (small)
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "ユニーク・スリー星・リバー（弱気）" for r in results)
    match = next(r for r in results if r.name == "ユニーク・スリー星・リバー（弱気）")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_unique_three_river_top_not_detected_no_small():
    """2nd candle is large -> not detected."""
    c0 = make_bullish_large(base=100.0)
    c1 = make_bullish_large(base=102.0)  # large body, not small
    c2 = make_candle(open=106.0, high=107.0, low=103.0, close=104.0)
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "ユニーク・スリー星・リバー（弱気）" for r in results)


# --- Last Engulfing Bearish (B#29) ---


def test_last_engulfing_bearish_detected():
    """Bullish -> large bearish engulfs c0 with gap context -> detected."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=108.0)
    # c0: bullish
    c1 = make_candle(open=112.0, high=114.0, low=108.0, close=110.0)
    # c1: gap up from c0 (c1.low=108 ~= c0.close=108)
    c2 = make_candle(open=112.0, high=113.0, low=96.0, close=98.0)
    # c2: large bearish, body=[98,112] engulfs c0 body [100,108]
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "最後の抱き線（弱気）" for r in results)
    match = next(r for r in results if r.name == "最後の抱き線（弱気）")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_last_engulfing_bearish_not_detected_no_engulf():
    """3rd candle doesn't engulf c0 -> not detected."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=108.0)
    c1 = make_candle(open=112.0, high=114.0, low=108.0, close=110.0)
    c2 = make_candle(open=109.0, high=110.0, low=103.0, close=104.0)
    # c2 body=[104,109], doesn't engulf c0 body [100,108]
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "最後の抱き線（弱気）" for r in results)


# --- Gap Down On Neck Continuation (B#30) ---


def test_gap_on_neck_continuation_detected():
    """Bearish with gap down -> bullish recovers to c0.close (on-neck) -> bearish continues."""
    c0 = make_candle(open=110.0, high=112.0, low=96.0, close=98.0)
    # c0: bearish
    c1 = make_candle(open=93.0, high=98.5, low=92.0, close=98.0)
    # c1: bullish, gap down (c1.high=98.5 ~close to c0.low=96, on-neck reaching c0.close=98)
    c2 = make_candle(open=97.0, high=98.0, low=88.0, close=90.0)
    # c2: bearish, continues decline
    results = detect_3_candle_bearish(c0, c1, c2)
    assert any(r.name == "窓開け後の「あて首」継続" for r in results)
    match = next(r for r in results if r.name == "窓開け後の「あて首」継続")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"


def test_gap_on_neck_continuation_not_detected_no_gap():
    """No gap down context -> not detected."""
    c0 = make_candle(open=110.0, high=112.0, low=96.0, close=98.0)
    c1 = make_candle(open=100.0, high=108.0, low=99.0, close=107.0)
    # c1: no gap down (c1.high=108 > c0.low=96), bullish recovery too strong
    c2 = make_candle(open=106.0, high=107.0, low=100.0, close=102.0)
    results = detect_3_candle_bearish(c0, c1, c2)
    assert not any(r.name == "窓開け後の「あて首」継続" for r in results)
