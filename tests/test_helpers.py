"""Unit-06: Tests for candlestick helper functions."""

import pytest

from app.services.pattern_detector import (
    _body_bottom,
    _body_ratio,
    _body_size,
    _body_top,
    _candle_range,
    _has_gap_down,
    _has_gap_up,
    _is_bearish,
    _is_bullish,
    _is_doji,
    _is_marubozu,
    _is_pin_bar_bearish,
    _is_pin_bar_bullish,
    _lower_shadow,
    _lower_shadow_ratio,
    _near_equal,
    _upper_shadow,
    _upper_shadow_ratio,
)
from tests.conftest import make_candle


def test_body_ratio_normal():
    """Body ratio for a normal candle: abs(close-open) / (high-low)."""
    c = make_candle(open=100.0, high=110.0, low=90.0, close=105.0)
    # body = 5, range = 20 -> ratio = 0.25
    assert _body_ratio(c) == pytest.approx(0.25)


def test_body_ratio_zero_range():
    """Body ratio when high == low (zero range) returns 0.0."""
    c = make_candle(open=100.0, high=100.0, low=100.0, close=100.0)
    assert _body_ratio(c) == 0.0


def test_is_bullish():
    """Bullish when close >= open."""
    assert _is_bullish(make_candle(open=100.0, close=105.0)) is True
    assert _is_bullish(make_candle(open=100.0, close=100.0)) is True
    assert _is_bullish(make_candle(open=100.0, close=95.0)) is False


def test_is_bearish():
    """Bearish when close < open."""
    assert _is_bearish(make_candle(open=100.0, close=95.0)) is True
    assert _is_bearish(make_candle(open=100.0, close=100.0)) is False
    assert _is_bearish(make_candle(open=100.0, close=105.0)) is False


def test_is_doji():
    """Doji when body ratio <= DOJI_THRESHOLD (0.1)."""
    # body=0.5, range=10 -> ratio=0.05 -> doji
    doji = make_candle(open=100.0, high=105.0, low=95.0, close=100.5)
    assert _is_doji(doji) is True
    # body=5, range=20 -> ratio=0.25 -> not doji
    non_doji = make_candle(open=100.0, high=110.0, low=90.0, close=105.0)
    assert _is_doji(non_doji) is False


def test_is_marubozu():
    """Marubozu when body ratio >= MARUBOZU_THRESHOLD (0.9)."""
    # body=10, range=10.2 -> ratio=~0.98 -> marubozu
    maru = make_candle(open=100.0, high=110.1, low=99.9, close=110.0)
    assert _is_marubozu(maru) is True
    # body=5, range=20 -> ratio=0.25 -> not marubozu
    non_maru = make_candle(open=100.0, high=110.0, low=90.0, close=105.0)
    assert _is_marubozu(non_maru) is False


def test_upper_shadow():
    """Upper shadow = high - max(open, close)."""
    c = make_candle(open=100.0, high=115.0, low=90.0, close=105.0)
    # upper shadow = 115 - 105 = 10
    assert _upper_shadow(c) == pytest.approx(10.0)


def test_lower_shadow():
    """Lower shadow = min(open, close) - low."""
    c = make_candle(open=100.0, high=115.0, low=90.0, close=105.0)
    # lower shadow = 100 - 90 = 10
    assert _lower_shadow(c) == pytest.approx(10.0)


def test_upper_shadow_ratio():
    """Upper shadow ratio = upper_shadow / body_size."""
    c = make_candle(open=100.0, high=115.0, low=95.0, close=105.0)
    # upper shadow = 10, body = 5 -> ratio = 2.0
    assert _upper_shadow_ratio(c) == pytest.approx(2.0)


def test_lower_shadow_ratio():
    """Lower shadow ratio = lower_shadow / body_size."""
    c = make_candle(open=100.0, high=115.0, low=85.0, close=105.0)
    # lower shadow = 100 - 85 = 15, body = 5 -> ratio = 3.0
    assert _lower_shadow_ratio(c) == pytest.approx(3.0)


def test_is_pin_bar_bullish():
    """Bullish pin bar: long lower shadow, short upper shadow."""
    c2 = make_candle(open=100.0, high=103.0, low=88.0, close=103.0)
    # body = 3, lower shadow = 100 - 88 = 12, ratio = 4.0 >= 2.0
    # upper shadow = 103 - 103 = 0, 0 < 3*0.5 = 1.5 -> True
    assert _is_pin_bar_bullish(c2) is True
    # Non pin bar (symmetric shadows)
    c3 = make_candle(open=100.0, high=110.0, low=90.0, close=105.0)
    assert _is_pin_bar_bullish(c3) is False


def test_is_pin_bar_bearish():
    """Bearish pin bar: long upper shadow, short lower shadow."""
    c = make_candle(open=103.0, high=115.0, low=100.0, close=100.0)
    # body = 3, upper shadow = 115 - 103 = 12, ratio = 4.0 >= 2.0
    # lower shadow = 100 - 100 = 0, 0 < 3*0.5 = 1.5 -> True
    assert _is_pin_bar_bearish(c) is True
    # Non pin bar
    c2 = make_candle(open=100.0, high=110.0, low=90.0, close=105.0)
    assert _is_pin_bar_bearish(c2) is False


def test_has_gap_up():
    """Gap up: curr.low > prev.high."""
    prev = make_candle(open=100.0, high=110.0, low=95.0, close=105.0)
    curr = make_candle(open=112.0, high=115.0, low=111.0, close=114.0)
    assert _has_gap_up(prev, curr) is True
    # No gap
    curr_no_gap = make_candle(open=108.0, high=115.0, low=109.0, close=114.0)
    assert _has_gap_up(prev, curr_no_gap) is False


def test_has_gap_down():
    """Gap down: curr.high < prev.low."""
    prev = make_candle(open=100.0, high=110.0, low=95.0, close=105.0)
    curr = make_candle(open=93.0, high=94.0, low=90.0, close=91.0)
    assert _has_gap_down(prev, curr) is True
    # No gap
    curr_no_gap = make_candle(open=96.0, high=98.0, low=93.0, close=97.0)
    assert _has_gap_down(prev, curr_no_gap) is False


def test_body_top_body_bottom():
    """body_top = max(open, close), body_bottom = min(open, close)."""
    bullish = make_candle(open=100.0, close=110.0)
    assert _body_top(bullish) == pytest.approx(110.0)
    assert _body_bottom(bullish) == pytest.approx(100.0)

    bearish = make_candle(open=110.0, close=100.0)
    assert _body_top(bearish) == pytest.approx(110.0)
    assert _body_bottom(bearish) == pytest.approx(100.0)


def test_body_size():
    """body_size = abs(close - open)."""
    c = make_candle(open=100.0, close=107.0)
    assert _body_size(c) == pytest.approx(7.0)
    c2 = make_candle(open=107.0, close=100.0)
    assert _body_size(c2) == pytest.approx(7.0)


def test_candle_range():
    """candle_range = high - low."""
    c = make_candle(high=120.0, low=95.0)
    assert _candle_range(c) == pytest.approx(25.0)


def test_near_equal():
    """near_equal with default tolerance."""
    assert _near_equal(100.0, 100.0) is True
    assert _near_equal(100.0, 100.05) is True  # diff=0.05, tol=100*0.001=0.1
    assert _near_equal(100.0, 101.0) is False  # diff=1.0, tol=0.1


def test_near_equal_boundary():
    """near_equal with explicit tolerance."""
    assert _near_equal(100.0, 100.5, tolerance=0.5) is True
    assert _near_equal(100.0, 100.6, tolerance=0.5) is False
