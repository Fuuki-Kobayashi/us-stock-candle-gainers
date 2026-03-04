"""Tests for pattern_detector service (Unit-10 through Unit-29)."""

from app.models.candle import CandleData, PatternResult
from app.services.pattern_detector import detect_patterns

# --- Helper: candle constructors ---


def _candle(
    date: str, o: float, h: float, lo: float, c: float, v: int = 1_000_000
) -> CandleData:
    return CandleData(date=date, open=o, high=h, low=lo, close=c, volume=v)


# ============================================================
# Unit-10: realdata mode returns both confirmed and predicted
# ============================================================
class TestUnit10:
    def test_detect_patterns_realdata_returns_confirmed_and_predicted(self) -> None:
        # Morning star candles (3 candles -> triggers confirmed AND predicted)
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),  # doji
            _candle("Day3", 141.5, 150.0, 141.0, 149.0),  # bullish large
        ]
        results = detect_patterns(candles, mode="realdata")
        types_found = {r.type for r in results}
        assert "confirmed" in types_found
        assert "predicted" in types_found


# ============================================================
# Unit-11: simulation_predicted returns predicted only
# ============================================================
class TestUnit11:
    def test_detect_patterns_simulation_predicted_returns_predicted_only(self) -> None:
        # 2 candles: bearish large + doji -> morning star predicted
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),  # doji
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        assert len(results) > 0
        for r in results:
            assert r.type == "predicted"


# ============================================================
# Unit-12: Confirmed Morning Star
# ============================================================
class TestUnit12:
    def test_detect_confirmed_morning_star(self) -> None:
        candles = [
            _candle(
                "Day1", 150.0, 151.0, 140.0, 141.0
            ),  # bearish large (body_ratio ~0.82)
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),  # doji (body_ratio=0.1)
            _candle(
                "Day3", 141.5, 150.0, 141.0, 149.0
            ),  # bullish large, close 149 > midpoint 145.5
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "モーニングスター" in names


# ============================================================
# Unit-13: Confirmed Evening Star
# ============================================================
class TestUnit13:
    def test_detect_confirmed_evening_star(self) -> None:
        candles = [
            _candle(
                "Day1", 140.0, 151.0, 139.0, 150.0
            ),  # bullish large (body_ratio ~0.83)
            _candle("Day2", 150.0, 151.0, 149.0, 150.3),  # doji (body_ratio=0.15)
            _candle(
                "Day3", 150.0, 151.0, 139.0, 140.0
            ),  # bearish large, close 140 < midpoint 145
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "イブニングスター" in names


# ============================================================
# Unit-14: Confirmed Three White Soldiers
# ============================================================
class TestUnit14:
    def test_detect_confirmed_three_white_soldiers(self) -> None:
        candles = [
            _candle("Day1", 100.0, 110.0, 99.0, 108.0),  # bullish
            _candle(
                "Day2", 105.0, 118.0, 104.0, 116.0
            ),  # bullish, open within prev body, close > prev close
            _candle(
                "Day3", 112.0, 126.0, 111.0, 124.0
            ),  # bullish, open within prev body, close > prev close
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        names = [r.name for r in results if r.type == "confirmed"]
        assert "スリーホワイトソルジャーズ" in names


# ============================================================
# Unit-15: Confirmed Three Black Crows
# ============================================================
class TestUnit15:
    def test_detect_confirmed_three_black_crows(self) -> None:
        candles = [
            _candle("Day1", 120.0, 121.0, 110.0, 112.0),  # bearish
            _candle(
                "Day2", 115.0, 116.0, 102.0, 104.0
            ),  # bearish, open within prev body, close < prev close
            _candle(
                "Day3", 108.0, 109.0, 94.0, 96.0
            ),  # bearish, open within prev body, close < prev close
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        names = [r.name for r in results if r.type == "confirmed"]
        assert "スリーブラッククロウズ" in names


# ============================================================
# Unit-16: Confirmed Rising Three Methods
# ============================================================
class TestUnit16:
    def test_detect_confirmed_rising_three_methods(self) -> None:
        candles = [
            _candle(
                "Day1", 100.0, 115.0, 99.0, 113.0
            ),  # large bullish (body_ratio ~0.81)
            _candle(
                "Day2", 110.0, 114.0, 100.0, 108.0
            ),  # small bearish within c0 range, body=2, range=14, ratio~0.14
            _candle(
                "Day3", 102.0, 120.0, 101.0, 118.0
            ),  # large bullish closing above c0 close (113)
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        names = [r.name for r in results if r.type == "confirmed"]
        assert "上昇三法" in names


# ============================================================
# Unit-17: Confirmed Falling Three Methods
# ============================================================
class TestUnit17:
    def test_detect_confirmed_falling_three_methods(self) -> None:
        candles = [
            _candle(
                "Day1", 115.0, 116.0, 100.0, 101.0
            ),  # large bearish (body_ratio ~0.875)
            _candle(
                "Day2", 104.0, 115.0, 101.0, 106.0
            ),  # small bullish within c0 range, body=2, range=14, ratio~0.14
            _candle(
                "Day3", 113.0, 114.0, 94.0, 95.0
            ),  # large bearish closing below c0 close (101)
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        names = [r.name for r in results if r.type == "confirmed"]
        assert "下降三法" in names


# ============================================================
# Unit-18: Predicted Morning Star
# ============================================================
class TestUnit18:
    def test_detect_predicted_morning_star(self) -> None:
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),  # doji
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "モーニングスター予測" in names
        ms = next(r for r in predicted if r.name == "モーニングスター予測")
        assert ms.required_third is not None


# ============================================================
# Unit-19: Predicted Evening Star
# ============================================================
class TestUnit19:
    def test_detect_predicted_evening_star(self) -> None:
        candles = [
            _candle("Day1", 140.0, 151.0, 139.0, 150.0),  # bullish large
            _candle("Day2", 150.0, 151.0, 149.0, 150.3),  # doji
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "イブニングスター予測" in names
        es = next(r for r in predicted if r.name == "イブニングスター予測")
        assert es.required_third is not None


# ============================================================
# Unit-20: Predicted Bullish Engulfing
# ============================================================
class TestUnit20:
    def test_detect_predicted_bullish_engulfing(self) -> None:
        candles = [
            _candle("Day1", 110.0, 112.0, 105.0, 106.0),  # bearish
            _candle(
                "Day2", 104.0, 115.0, 103.0, 114.0
            ),  # bullish, open (104) < c0 low (105)
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "強気の包み足予測" in names


# ============================================================
# Unit-21: Predicted Bearish Engulfing
# ============================================================
class TestUnit21:
    def test_detect_predicted_bearish_engulfing(self) -> None:
        candles = [
            _candle("Day1", 100.0, 110.0, 99.0, 108.0),  # bullish
            _candle(
                "Day2", 111.0, 112.0, 95.0, 96.0
            ),  # bearish, open (111) > c0 high (110)
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "弱気の包み足予測" in names


# ============================================================
# Unit-22: Predicted Bullish Piercing
# ============================================================
class TestUnit22:
    def test_detect_predicted_bullish_piercing(self) -> None:
        # c0: bearish large body, c1: opens below c0 low, closes above c0 midpoint
        candles = [
            _candle(
                "Day1", 150.0, 151.0, 140.0, 141.0
            ),  # bearish large, midpoint=145.5
            _candle(
                "Day2", 139.0, 148.0, 138.0, 146.0
            ),  # opens below 140, closes 146 > 145.5
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "強気の切り込み予測" in names


# ============================================================
# Unit-23: Predicted Bearish Dark Cloud
# ============================================================
class TestUnit23:
    def test_detect_predicted_bearish_dark_cloud(self) -> None:
        # c0: bullish large body, c1: opens above c0 high, closes below c0 midpoint
        candles = [
            _candle("Day1", 140.0, 151.0, 139.0, 150.0),  # bullish large, midpoint=145
            _candle(
                "Day2", 152.0, 153.0, 143.0, 144.0
            ),  # opens above 151, closes 144 < 145
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "弱気のかぶせ線予測" in names


# ============================================================
# Unit-24: No pattern found (flat candles)
# ============================================================
class TestUnit24:
    def test_detect_patterns_no_pattern_found(self) -> None:
        candles = [
            _candle("Day1", 100.0, 100.0, 100.0, 100.0),
            _candle("Day2", 100.0, 100.0, 100.0, 100.0),
            _candle("Day3", 100.0, 100.0, 100.0, 100.0),
        ]
        results = detect_patterns(candles, mode="realdata")
        assert results == []


# ============================================================
# Unit-25: Body ratio boundary 60% (exactly 0.60 = large body)
# ============================================================
class TestUnit25:
    def test_detect_patterns_body_ratio_boundary_60_percent(self) -> None:
        # Body ratio = abs(close - open) / (high - low)
        # Want exactly 0.60: body=6, range=10 -> 6/10=0.60
        # Morning star: c0 bearish large, c1 doji, c2 bullish large above c0 midpoint
        candles = [
            _candle(
                "Day1", 110.0, 110.0, 100.0, 104.0
            ),  # bearish, body=6, range=10, ratio=0.60
            _candle("Day2", 104.0, 105.0, 103.0, 104.2),  # doji, ratio=0.1
            _candle(
                "Day3", 104.5, 115.0, 104.0, 110.0
            ),  # bullish, body=5.5, range=11, ratio=0.5 -> not large
        ]
        # c2 body ratio is 0.5 which is NOT large, so morning star won't trigger.
        # Let's use a c2 with ratio exactly 0.60.
        candles = [
            _candle("Day1", 110.0, 110.0, 100.0, 104.0),  # bearish, ratio=0.60 (large)
            _candle("Day2", 104.0, 105.0, 103.0, 104.2),  # doji
            _candle(
                "Day3", 104.0, 114.0, 104.0, 110.0
            ),  # bullish, body=6, range=10, ratio=0.60 (large), close 110 > midpoint 107
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "モーニングスター" in names


# ============================================================
# Unit-26: Body ratio boundary 30% (exactly 0.30 = small body)
# ============================================================
class TestUnit26:
    def test_detect_patterns_body_ratio_boundary_30_percent(self) -> None:
        # Doji-like: body_ratio exactly 0.30
        # body=3, range=10 -> 3/10=0.30
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle(
                "Day2", 141.0, 145.0, 135.0, 144.0
            ),  # body=3, range=10, ratio=0.30 (small/doji-like)
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "モーニングスター予測" in names


# ============================================================
# Unit-27: high == low (zero range) -> no crash
# ============================================================
class TestUnit27:
    def test_detect_patterns_high_equals_low_zero_range(self) -> None:
        candles = [
            _candle("Day1", 100.0, 100.0, 100.0, 100.0),
            _candle("Day2", 100.0, 100.0, 100.0, 100.0),
        ]
        # Should not raise, returns empty or valid results
        results = detect_patterns(candles, mode="realdata")
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, PatternResult)


# ============================================================
# Unit-28: simulation_confirmed returns confirmed only
# ============================================================
class TestUnit28:
    def test_detect_patterns_confirmed_only_for_simulation_confirmed(self) -> None:
        # Morning star candles (triggers both confirmed and predicted in realdata)
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),
            _candle("Day3", 141.5, 150.0, 141.0, 149.0),
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        for r in results:
            assert r.type == "confirmed"


# ============================================================
# Unit-29: PatternResult fields are complete
# ============================================================
class TestUnit29:
    def test_pattern_result_fields_complete(self) -> None:
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),
            _candle("Day3", 141.5, 150.0, 141.0, 149.0),
        ]
        results = detect_patterns(candles, mode="realdata")
        assert len(results) > 0
        for r in results:
            assert isinstance(r.type, str) and len(r.type) > 0
            assert isinstance(r.name, str) and len(r.name) > 0
            assert isinstance(r.signal, str) and len(r.signal) > 0
            assert isinstance(r.description, str) and len(r.description) > 0
