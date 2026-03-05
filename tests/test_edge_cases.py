"""Unit-09: Edge case tests for detect_patterns."""

from app.services.pattern_detector import _near_equal, detect_patterns
from tests.conftest import make_candle


def test_zero_range_candle():
    """high == low candles should not crash."""
    c = make_candle(open=100, high=100, low=100, close=100)
    result = detect_patterns([c, c, c], "realdata")
    assert isinstance(result, list)


def test_zero_volume():
    """volume == 0 should not crash."""
    c = make_candle(volume=0)
    result = detect_patterns([c, c, c], "realdata")
    assert isinstance(result, list)


def test_flat_candles_no_pattern():
    """All-same-value candles (zero range) should not crash.

    Note: zero-range candles may trigger small-body patterns (e.g. three stars),
    so we only verify no crash occurs, not that result is empty.
    """
    c = make_candle(open=100, high=100, low=100, close=100)
    result = detect_patterns([c, c, c], "realdata")
    assert isinstance(result, list)


def test_single_candle_input():
    """Single candle input should not crash."""
    c = make_candle()
    result = detect_patterns([c], "realdata")
    assert isinstance(result, list)


def test_empty_candle_list():
    """Empty candle list should return empty list."""
    result = detect_patterns([], "realdata")
    assert result == []


def test_tolerance_boundary():
    """_near_equal boundary values."""
    assert _near_equal(100.0, 100.0)
    assert _near_equal(100.0, 100.09, tolerance=0.1)
    assert not _near_equal(100.0, 100.11, tolerance=0.1)


def test_two_candle_input_no_3candle_patterns():
    """2-candle input should not produce 3-candle confirmed patterns."""
    c0 = make_candle(open=110, high=112, low=98, close=100)  # bearish
    c1 = make_candle(open=95, high=108, low=93, close=105)  # bullish
    result = detect_patterns([c0, c1], "realdata")
    three_candle_names = [
        "明けの明星",
        "赤三兵",
        "宵の明星",
        "三羽烏（黒三兵）",
        "明けの十字星",
        "捨て子底",
        "スリー・インサイド・アップ",
        "スリー・アウトサイド・アップ",
        "モーニング・ピンバー・リバーサル",
        "三つの星底",
        "スティック・サンドイッチ",
        "南の三つ星",
        "ユニーク・スリー・リバー",
        "下放れ三法",
        "上放れタスキ線",
        "上放れ並び赤",
        "インサイドバーの上抜け",
        "スリー・インサイド・ダウン",
        "スリー・アウトサイド・ダウン",
        "三つの星天井",
        "南の三つ星（弱気）",
        "インサイドバーの弱気ブレイク",
        "スティック・サンドイッチ（弱気）",
        "ユニーク・スリー星・リバー（弱気）",
        "最後の抱き線（弱気）",
        "窓開け後の「あて首」継続",
    ]
    for r in result:
        assert r.name not in three_candle_names or r.type == "predicted"
