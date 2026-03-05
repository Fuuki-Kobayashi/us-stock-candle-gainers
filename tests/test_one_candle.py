"""Unit-01: 1-candle pattern detection tests (4 bearish patterns)."""

from app.services.patterns.one_candle import detect_1_candle
from tests.conftest import make_candle

# --- Bearish Pin Bar (B#6) ---


def test_bearish_pin_bar_detected():
    """Long upper shadow, short lower shadow -> Bearish Pin Bar detected."""
    # open=100.0, close=100.5 -> body=0.5
    # high=110.0 -> upper_shadow=9.5 (ratio=19.0 >= 2.0)
    # low=99.9 -> lower_shadow=0.1 (< body*0.5=0.25)
    candle = make_candle(open=100.0, high=110.0, low=99.9, close=100.5)
    results = detect_1_candle(candle)
    assert any(r.name == "ベアリッシュ・ピンバー" for r in results)
    match = next(r for r in results if r.name == "ベアリッシュ・ピンバー")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"
    assert match.direction == "bearish"
    assert match.pattern_candle_count == 1


def test_bearish_pin_bar_not_detected_short_upper():
    """Upper shadow is too short -> not detected."""
    # Body is large relative to upper shadow
    candle = make_candle(open=100.0, high=105.0, low=90.0, close=103.0)
    # body=3, upper_shadow=2, ratio=0.67 < 2.0
    results = detect_1_candle(candle)
    assert not any(r.name == "ベアリッシュ・ピンバー" for r in results)


# --- Gravestone Doji (B#11) ---


def test_gravestone_doji_detected():
    """Doji with long upper shadow, no lower shadow -> Gravestone Doji detected."""
    candle = make_candle(open=100.0, high=110.0, low=99.9, close=100.0)
    # body=0, range=10.1, body_ratio=0 (doji)
    # upper_shadow=10.0 > range*0.6=6.06
    # lower_shadow=0.1 < range*0.1=1.01
    results = detect_1_candle(candle)
    assert any(r.name == "トウバ（墓石十字）" for r in results)
    match = next(r for r in results if r.name == "トウバ（墓石十字）")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"
    assert match.direction == "bearish"
    assert match.pattern_candle_count == 1


def test_gravestone_doji_not_detected_with_body():
    """Candle has a large body -> not a doji, not detected."""
    candle = make_candle(open=100.0, high=115.0, low=95.0, close=110.0)
    # body=10, range=20, body_ratio=0.5 (not doji)
    results = detect_1_candle(candle)
    assert not any(r.name == "トウバ（墓石十字）" for r in results)


# --- Hanging Man (B#12) ---


def test_hanging_man_detected():
    """Small body, long lower shadow, short upper shadow -> Hanging Man."""
    candle = make_candle(open=108.0, high=109.0, low=100.0, close=109.0)
    # body=1.0, lower_shadow=8.0 (ratio=8.0 >= 2.0)
    # upper_shadow=0.0 < body*0.3=0.3
    # body_ratio=1/9~0.11 (<= 0.3 = small body)
    results = detect_1_candle(candle)
    assert any(r.name == "首吊り線" for r in results)
    match = next(r for r in results if r.name == "首吊り線")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"
    assert match.direction == "bearish"
    assert match.pattern_candle_count == 1


def test_hanging_man_not_detected_large_body():
    """Large body candle -> not detected as Hanging Man."""
    candle = make_candle(open=100.0, high=115.0, low=90.0, close=112.0)
    # body=12, range=25, body_ratio=0.48 (> 0.3, not small)
    results = detect_1_candle(candle)
    assert not any(r.name == "首吊り線" for r in results)


# --- Shooting Star (B#13) ---


def test_shooting_star_detected():
    """Small body, long upper shadow, short lower shadow -> Shooting Star."""
    candle = make_candle(open=100.0, high=110.0, low=99.9, close=100.5)
    # body=0.5, upper_shadow=9.5 (ratio=19.0 >= 2.0)
    # lower_shadow=0.1 < body*0.3=0.15
    # body_ratio=0.5/10.1~0.05 (<= 0.3 = small body)
    results = detect_1_candle(candle)
    assert any(r.name == "流れ星" for r in results)
    match = next(r for r in results if r.name == "流れ星")
    assert match.type == "confirmed"
    assert match.signal == "🔽 弱気シグナル"
    assert match.direction == "bearish"
    assert match.pattern_candle_count == 1


def test_shooting_star_not_detected_large_lower():
    """Large lower shadow -> not detected as Shooting Star."""
    candle = make_candle(open=105.0, high=115.0, low=90.0, close=106.0)
    # body=1, upper_shadow=9, lower_shadow=15
    # lower_shadow(15) > body(1)*0.3=0.3 -> fails condition
    results = detect_1_candle(candle)
    assert not any(r.name == "流れ星" for r in results)
