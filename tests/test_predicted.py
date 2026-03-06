"""Unit-08: Predicted pattern detection tests (26 patterns = 15 bullish + 11 bearish)."""

from app.services.patterns.predicted import detect_predicted
from tests.conftest import (
    make_bearish_large,
    make_bullish_large,
    make_candle,
    make_doji,
    make_small_body,
)

# =============================================================================
# Bullish precursors (15 patterns)
# =============================================================================

# --- 1. Morning Star Predicted ---


def test_morning_star_predicted():
    """Large bearish -> small body -> Morning Star predicted."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_small_body(base=95.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert any(r.name == "明けの明星予測" for r in results)
    match = next(r for r in results if r.name == "明けの明星予測")
    assert match.type == "predicted"
    assert match.signal == "🔼 強気シグナル（予測）"
    assert match.required_third is not None and "大陽線" in match.required_third
    assert match.direction == "bullish"
    assert match.pattern_candle_count == 3
    assert match.pattern_id == "morning_star"


def test_morning_star_predicted_not_detected():
    """c0 is not large bearish -> not detected."""
    c0 = make_small_body(base=100.0, bullish=False)  # small, not large bearish
    c1 = make_small_body(base=98.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert not any(r.name == "明けの明星予測" for r in results)


# --- 2. Morning Doji Star Predicted ---


def test_morning_doji_star_predicted():
    """Large bearish -> doji -> Morning Doji Star predicted."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_doji(base=95.0)
    results = detect_predicted(c0, c1)
    assert any(r.name == "明けの十字星予測" for r in results)
    match = next(r for r in results if r.name == "明けの十字星予測")
    assert match.type == "predicted"
    assert match.signal == "🔼 強気シグナル（予測）"
    assert match.required_third is not None and "大陽線" in match.required_third


# --- 3. Abandoned Baby Bottom Predicted ---


def test_abandoned_baby_bottom_predicted():
    """Large bearish -> doji with gap down -> Abandoned Baby predicted."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, high=112, low=98, close=100
    # Gap down: c1.high < c0.low=98
    c1 = make_candle(open=95.0, high=96.0, low=90.0, close=95.2)
    # c1 is doji: body=0.2, range=6, ratio=0.03
    results = detect_predicted(c0, c1)
    assert any(r.name == "捨て子底予測" for r in results)
    match = next(r for r in results if r.name == "捨て子底予測")
    assert match.type == "predicted"
    assert (
        match.required_third is not None and "窓を開けた大陽線" in match.required_third
    )


# --- 4. Three White Soldiers Predicted ---


def test_three_white_soldiers_predicted():
    """2 consecutive bullish with c1.close > c0.close -> Red Three predicted."""
    c0 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    c1 = make_candle(open=105.0, high=118.0, low=104.0, close=115.0)
    # Both bullish, c1.close=115 > c0.close=110
    results = detect_predicted(c0, c1)
    assert any(r.name == "赤三兵予測" for r in results)
    match = next(r for r in results if r.name == "赤三兵予測")
    assert match.required_third is not None and "陽線" in match.required_third


# --- 5. Three Inside Up Predicted ---


def test_three_inside_up_predicted():
    """Large bearish -> small bullish inside (harami) -> predicted."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100, body=[100,110]
    c1 = make_candle(open=102.0, high=110.0, low=100.0, close=105.0)
    # c1: bullish, body=[102,105] body_ratio=3/10=0.3 (small), inside c0 body [100,110]
    results = detect_predicted(c0, c1)
    assert any(
        "スリー・インサイド・アップ" in r.name and "予測" in r.name for r in results
    )
    match = next(
        r
        for r in results
        if "スリー・インサイド・アップ" in r.name and "予測" in r.name
    )
    assert match.required_third is not None and "陽線" in match.required_third


# --- 6. Three Outside Up Predicted ---


def test_three_outside_up_predicted():
    """Small bearish -> large bullish engulfs -> predicted."""
    c0 = make_small_body(base=105.0, bullish=False)
    # c0: open=105, close=103, body=[103,105]
    c1 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    # c1: large bullish, body=[100,110] engulfs c0 body [103,105]
    results = detect_predicted(c0, c1)
    assert any(r.name == "スリー・アウトサイド・アップ予測" for r in results)
    match = next(r for r in results if r.name == "スリー・アウトサイド・アップ予測")
    assert match.required_third is not None and "陽線" in match.required_third


# --- 7. Morning Pin Bar Predicted ---


def test_morning_pin_bar_predicted():
    """Large bearish -> bullish pin bar -> predicted."""
    c0 = make_bearish_large(base=100.0)
    # Custom pin bar: body=1, lower_shadow=8, upper_shadow=0
    c1 = make_candle(open=96.0, high=97.0, low=88.0, close=97.0)
    # body=1, lower_shadow=96-88=8 (ratio=8>=2), upper_shadow=0 (<0.5)
    results = detect_predicted(c0, c1)
    assert any(r.name == "モーニング・ピンバー予測" for r in results)
    match = next(r for r in results if r.name == "モーニング・ピンバー予測")
    assert match.required_third is not None and "大陽線" in match.required_third


# --- 8. Three Stars Bottom Predicted ---


def test_three_stars_bottom_predicted():
    """2 consecutive small bodies -> predicted."""
    c0 = make_small_body(base=95.0, bullish=False)
    c1 = make_small_body(base=94.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert any(r.name == "三つの星底予測" for r in results)
    match = next(r for r in results if r.name == "三つの星底予測")
    assert match.required_third is not None and "小実体" in match.required_third


# --- 9. Stick Sandwich Bullish Predicted ---


def test_stick_sandwich_bullish_predicted():
    """Bearish -> bullish -> predicted."""
    c0 = make_candle(open=105.0, high=107.0, low=95.0, close=97.0)
    # c0: bearish
    c1 = make_candle(open=96.0, high=105.0, low=95.0, close=103.0)
    # c1: bullish
    results = detect_predicted(c0, c1)
    assert any(r.name == "スティック・サンドイッチ予測" for r in results)
    match = next(r for r in results if r.name == "スティック・サンドイッチ予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 10. Three Stars in South Predicted ---


def test_three_stars_in_south_predicted():
    """2 bearish with smaller range -> predicted."""
    c0 = make_candle(open=105.0, high=108.0, low=94.0, close=97.0)
    # c0: bearish, range=14
    c1 = make_candle(open=98.0, high=100.0, low=91.0, close=93.0)
    # c1: bearish, range=9 (smaller)
    results = detect_predicted(c0, c1)
    assert any(r.name == "南の三つ星予測" for r in results)
    match = next(r for r in results if r.name == "南の三つ星予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 11. Unique Three River Predicted ---


def test_unique_three_river_predicted():
    """Large bearish -> small bearish inside c0 -> predicted."""
    c0 = make_bearish_large(base=100.0)
    # c0: open=110, close=100, body=[100,110]
    c1 = make_candle(open=107.0, high=110.0, low=100.0, close=104.0)
    # c1: bearish, body=[104,107] body_ratio=3/10=0.3 (small), inside c0 body
    results = detect_predicted(c0, c1)
    assert any(r.name == "ユニーク・スリー・リバー予測" for r in results)
    match = next(r for r in results if r.name == "ユニーク・スリー・リバー予測")
    assert match.required_third is not None and "小陽線" in match.required_third


# --- 12. Downside Gap Three Methods Predicted ---


def test_downside_gap_three_methods_predicted():
    """Bearish -> bearish with gap down -> predicted."""
    c0 = make_candle(open=110.0, high=112.0, low=100.0, close=102.0)
    # c0: bearish
    c1 = make_candle(open=97.0, high=98.0, low=90.0, close=92.0)
    # c1: bearish, gap down (c1.high=98 < c0.low=100)
    results = detect_predicted(c0, c1)
    assert any(r.name == "下放れ三法予測" for r in results)
    match = next(r for r in results if r.name == "下放れ三法予測")
    assert match.required_third is not None and "陽線" in match.required_third


# --- 13. Upside Tasuki Gap Predicted ---


def test_upside_tasuki_gap_predicted():
    """Bullish -> bullish with gap up -> predicted."""
    c0 = make_candle(open=100.0, high=112.0, low=98.0, close=110.0)
    # c0: bullish
    c1 = make_candle(open=115.0, high=122.0, low=113.0, close=120.0)
    # c1: bullish, gap up (c1.low=113 > c0.high=112)
    results = detect_predicted(c0, c1)
    assert any(r.name == "上放れタスキ線予測" for r in results)
    match = next(r for r in results if r.name == "上放れタスキ線予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 14. Upside Gap Side-by-Side White Predicted ---


def test_upside_gap_side_by_side_white_predicted():
    """Any -> bullish with gap up -> predicted."""
    c0 = make_candle(open=100.0, high=110.0, low=98.0, close=108.0)
    c1 = make_candle(open=113.0, high=120.0, low=112.0, close=118.0)
    # c1: bullish, gap up (c1.low=112 > c0.high=110)
    results = detect_predicted(c0, c1)
    assert any(r.name == "上放れ並び赤予測" for r in results)
    match = next(r for r in results if r.name == "上放れ並び赤予測")
    assert match.required_third is not None and "陽線" in match.required_third


# --- 15. Inside Bar Bullish Breakout Predicted ---


def test_inside_bar_bullish_breakout_predicted():
    """Any large -> c1 inside c0 body -> predicted."""
    c0 = make_candle(open=100.0, high=115.0, low=90.0, close=110.0)
    # c0: large body, range=25
    c1 = make_candle(open=105.0, high=108.0, low=95.0, close=103.0)
    # c1: inside c0 (high=108 < 115, low=95 > 90)
    results = detect_predicted(c0, c1)
    assert any(r.name == "インサイドバー上抜け予測" for r in results)
    match = next(r for r in results if r.name == "インサイドバー上抜け予測")
    assert match.required_third is not None and "陽線" in match.required_third


# =============================================================================
# Bearish precursors (11 patterns)
# =============================================================================

# --- 1. Evening Star Predicted ---


def test_evening_star_predicted():
    """Large bullish -> small body -> Evening Star predicted."""
    c0 = make_bullish_large(base=100.0)
    c1 = make_small_body(base=112.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert any(r.name == "宵の明星予測" for r in results)
    match = next(r for r in results if r.name == "宵の明星予測")
    assert match.type == "predicted"
    assert match.signal == "🔽 弱気シグナル（予測）"
    assert match.required_third is not None and "大陰線" in match.required_third
    assert match.direction == "bearish"
    assert match.pattern_candle_count == 3
    assert match.pattern_id == "evening_star"


def test_evening_star_predicted_not_detected():
    """c0 is not large bullish -> not detected."""
    c0 = make_small_body(base=100.0, bullish=True)  # small, not large bullish
    c1 = make_small_body(base=103.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert not any(r.name == "宵の明星予測" for r in results)


# --- 2. Three Black Crows Predicted ---


def test_three_black_crows_predicted():
    """2 bearish with c1.close < c0.close -> predicted."""
    c0 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    c1 = make_candle(open=105.0, high=107.0, low=93.0, close=95.0)
    # Both bearish, c1.close=95 < c0.close=100
    results = detect_predicted(c0, c1)
    assert any(r.name == "三羽烏予測" for r in results)
    match = next(r for r in results if r.name == "三羽烏予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 3. Three Inside Down Predicted ---


def test_three_inside_down_predicted():
    """Large bullish -> small bearish inside c0 -> predicted."""
    c0 = make_bullish_large(base=100.0)
    # c0: open=100, close=110, body=[100,110]
    c1 = make_candle(open=108.0, high=110.0, low=100.0, close=105.0)
    # c1: bearish, body=[105,108] body_ratio=3/10=0.3 (small), inside c0
    results = detect_predicted(c0, c1)
    assert any(r.name == "スリー・インサイド・ダウン予測" for r in results)
    match = next(r for r in results if r.name == "スリー・インサイド・ダウン予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 4. Three Outside Down Predicted ---


def test_three_outside_down_predicted():
    """Small bullish -> large bearish engulfs -> predicted."""
    c0 = make_small_body(base=105.0, bullish=True)
    # c0: open=105, close=107, body=[105,107]
    c1 = make_candle(open=110.0, high=112.0, low=98.0, close=100.0)
    # c1: large bearish, body=[100,110] engulfs c0
    results = detect_predicted(c0, c1)
    assert any(r.name == "スリー・アウトサイド・ダウン予測" for r in results)
    match = next(r for r in results if r.name == "スリー・アウトサイド・ダウン予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 5. Three Stars Top Predicted ---


def test_three_stars_top_predicted():
    """2 consecutive small bodies (at top) -> predicted."""
    c0 = make_small_body(base=150.0, bullish=True)
    c1 = make_small_body(base=151.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert any(r.name == "三つの星天井予測" for r in results)
    match = next(r for r in results if r.name == "三つの星天井予測")
    assert match.required_third is not None and "小実体" in match.required_third


# --- 6. Three Stars South Bearish Predicted ---


def test_three_stars_south_bearish_predicted():
    """2 small bullish with smaller range -> predicted."""
    c0 = make_candle(open=100.0, high=106.0, low=94.0, close=102.0)
    # range=12, small body (body=2, ratio=2/12=0.17)
    c1 = make_candle(open=101.0, high=105.0, low=96.0, close=102.5)
    # range=9, small body (body=1.5, ratio=1.5/9=0.17), smaller range
    results = detect_predicted(c0, c1)
    assert any(r.name == "南の三つ星（弱気）予測" for r in results)
    match = next(r for r in results if r.name == "南の三つ星（弱気）予測")
    assert match.required_third is not None and "小実体" in match.required_third


# --- 7. Inside Bar Bearish Predicted ---


def test_inside_bar_bearish_predicted():
    """Any large -> c1 inside c0 -> predicted."""
    c0 = make_candle(open=100.0, high=115.0, low=90.0, close=110.0)
    c1 = make_candle(open=105.0, high=108.0, low=95.0, close=103.0)
    # c1 inside c0
    results = detect_predicted(c0, c1)
    assert any(r.name == "インサイドバー弱気予測" for r in results)
    match = next(r for r in results if r.name == "インサイドバー弱気予測")
    assert match.required_third is not None and "陰線" in match.required_third


# --- 8. Stick Sandwich Bearish Predicted ---


def test_stick_sandwich_bearish_predicted():
    """Bullish -> bearish -> predicted."""
    c0 = make_candle(open=98.0, high=112.0, low=97.0, close=110.0)
    # c0: bullish
    c1 = make_candle(open=112.0, high=113.0, low=103.0, close=105.0)
    # c1: bearish
    results = detect_predicted(c0, c1)
    assert any(r.name == "スティック・サンドイッチ（弱気）予測" for r in results)
    match = next(r for r in results if r.name == "スティック・サンドイッチ（弱気）予測")
    assert match.required_third is not None and "陽線" in match.required_third


# --- 9. Unique Three River Top Predicted ---


def test_unique_three_river_top_predicted():
    """Large bullish -> small bullish -> predicted."""
    c0 = make_bullish_large(base=100.0)
    c1 = make_small_body(base=108.0, bullish=True)
    results = detect_predicted(c0, c1)
    assert any(r.name == "ユニーク・スリー星・リバー（弱気）予測" for r in results)
    match = next(
        r for r in results if r.name == "ユニーク・スリー星・リバー（弱気）予測"
    )
    assert match.required_third is not None and "小陰線" in match.required_third


# --- 10. Last Engulfing Bearish Predicted ---


def test_last_engulfing_bearish_predicted():
    """Bullish -> gap up -> predicted."""
    c0 = make_candle(open=100.0, high=110.0, low=99.0, close=108.0)
    # c0: bullish
    c1 = make_candle(open=112.0, high=114.0, low=111.0, close=113.0)
    # c1: gap up (c1.low=111 > c0.high=110)
    results = detect_predicted(c0, c1)
    assert any(r.name == "最後の抱き線（弱気）予測" for r in results)
    match = next(r for r in results if r.name == "最後の抱き線（弱気）予測")
    assert match.required_third is not None and "大陰線" in match.required_third


# --- 11. Gap Down On Neck Continuation Predicted ---


def test_gap_on_neck_continuation_predicted():
    """Bearish (gap context) -> bullish reaching c0.close -> predicted."""
    c0 = make_candle(open=110.0, high=112.0, low=96.0, close=98.0)
    # c0: bearish
    c1 = make_candle(open=93.0, high=98.5, low=92.0, close=98.0)
    # c1: bullish, reaching c0.close=98
    results = detect_predicted(c0, c1)
    assert any(r.name == "窓開け後あて首継続予測" for r in results)
    match = next(r for r in results if r.name == "窓開け後あて首継続予測")
    assert match.required_third is not None and "陰線" in match.required_third


# =============================================================================
# Common tests
# =============================================================================


def test_all_predicted_have_required_third_field():
    """All predicted results must have required_third set."""
    # Use data that triggers multiple patterns
    c0 = make_bearish_large(base=100.0)
    c1 = make_small_body(base=95.0, bullish=True)
    results = detect_predicted(c0, c1)
    for r in results:
        assert r.type == "predicted"
        assert r.required_third is not None
        assert len(r.required_third) > 0


def test_evening_star_predicted_not_detected_small_c0():
    """c0 is small body -> evening star precursor not detected."""
    c0 = make_small_body(base=100.0, bullish=True)
    c1 = make_small_body(base=103.0, bullish=False)
    results = detect_predicted(c0, c1)
    assert not any(r.name == "宵の明星予測" for r in results)


def test_morning_star_predicted_not_detected_c1_large():
    """c1 is large body (not small) -> morning star precursor not detected."""
    c0 = make_bearish_large(base=100.0)
    c1 = make_bullish_large(base=95.0)  # large body, not small
    results = detect_predicted(c0, c1)
    assert not any(r.name == "明けの明星予測" for r in results)
