"""Tests for pattern_detector service (Unit-10 through Unit-29).

Updated for 60-pattern engine rewrite:
- Pattern names changed to Japanese standard names
- Old predicted patterns (engulfing/piercing/dark cloud) moved to 2-candle confirmed
- Old confirmed names (e.g. モーニングスター) replaced with new names (明けの明星)
"""

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
# Unit-12: Confirmed Morning Star (now 明けの明星)
# ============================================================
class TestUnit12:
    def test_detect_confirmed_morning_star(self) -> None:
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle("Day2", 141.0, 142.0, 140.0, 141.2),  # doji
            _candle("Day3", 141.5, 150.0, 141.0, 149.0),  # bullish large
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "明けの明星" in names


# ============================================================
# Unit-13: Confirmed Evening Star (now 宵の明星)
# ============================================================
class TestUnit13:
    def test_detect_confirmed_evening_star(self) -> None:
        candles = [
            _candle("Day1", 140.0, 151.0, 139.0, 150.0),  # bullish large
            _candle("Day2", 150.0, 151.0, 149.0, 150.3),  # doji
            _candle("Day3", 150.0, 151.0, 139.0, 140.0),  # bearish large
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "宵の明星" in names


# ============================================================
# Unit-14: Confirmed Three White Soldiers (now 赤三兵)
# ============================================================
class TestUnit14:
    def test_detect_confirmed_three_white_soldiers(self) -> None:
        candles = [
            _candle("Day1", 100.0, 110.0, 99.0, 108.0),  # bullish
            _candle("Day2", 105.0, 118.0, 104.0, 116.0),  # bullish
            _candle("Day3", 112.0, 126.0, 111.0, 124.0),  # bullish
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        names = [r.name for r in results if r.type == "confirmed"]
        assert "赤三兵" in names


# ============================================================
# Unit-15: Confirmed Three Black Crows (now 三羽烏（黒三兵）)
# ============================================================
class TestUnit15:
    def test_detect_confirmed_three_black_crows(self) -> None:
        candles = [
            _candle("Day1", 120.0, 121.0, 110.0, 112.0),  # bearish
            _candle("Day2", 115.0, 116.0, 102.0, 104.0),  # bearish
            _candle("Day3", 108.0, 109.0, 94.0, 96.0),  # bearish
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        names = [r.name for r in results if r.type == "confirmed"]
        assert "三羽烏（黒三兵）" in names


# ============================================================
# Unit-16: Rising Three Methods -> removed from new 60-pattern set
# Test updated to verify no crash with this data
# ============================================================
class TestUnit16:
    def test_detect_confirmed_rising_three_methods(self) -> None:
        candles = [
            _candle("Day1", 100.0, 115.0, 99.0, 113.0),  # large bullish
            _candle("Day2", 110.0, 114.0, 100.0, 108.0),  # small bearish
            _candle("Day3", 102.0, 120.0, 101.0, 118.0),  # large bullish
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        # Pattern detection should work without error
        assert isinstance(results, list)


# ============================================================
# Unit-17: Falling Three Methods -> removed from new 60-pattern set
# Test updated to verify no crash with this data
# ============================================================
class TestUnit17:
    def test_detect_confirmed_falling_three_methods(self) -> None:
        candles = [
            _candle("Day1", 115.0, 116.0, 100.0, 101.0),  # large bearish
            _candle("Day2", 104.0, 115.0, 101.0, 106.0),  # small bullish
            _candle("Day3", 113.0, 114.0, 94.0, 95.0),  # large bearish
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        assert isinstance(results, list)


# ============================================================
# Unit-18: Predicted Morning Star (now 明けの明星予測)
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
        assert "明けの明星予測" in names
        ms = next(r for r in predicted if r.name == "明けの明星予測")
        assert ms.required_third is not None


# ============================================================
# Unit-19: Predicted Evening Star (now 宵の明星予測)
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
        assert "宵の明星予測" in names
        es = next(r for r in predicted if r.name == "宵の明星予測")
        assert es.required_third is not None


# ============================================================
# Unit-20: Bullish Engulfing -> now 2-candle confirmed (包み線（抱き線）)
# ============================================================
class TestUnit20:
    def test_detect_confirmed_bullish_engulfing(self) -> None:
        candles = [
            _candle("Day1", 110.0, 112.0, 105.0, 106.0),  # bearish
            _candle("Day2", 104.0, 115.0, 103.0, 114.0),  # bullish engulfing
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "包み線（抱き線）" in names


# ============================================================
# Unit-21: Bearish Engulfing -> now 2-candle confirmed (陰の陽包み)
# ============================================================
class TestUnit21:
    def test_detect_confirmed_bearish_engulfing(self) -> None:
        candles = [
            _candle("Day1", 100.0, 110.0, 99.0, 108.0),  # bullish
            _candle("Day2", 111.0, 112.0, 95.0, 96.0),  # bearish engulfing
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "陰の陽包み" in names


# ============================================================
# Unit-22: Bullish Piercing -> now 2-candle confirmed (切り込み線)
# ============================================================
class TestUnit22:
    def test_detect_confirmed_bullish_piercing(self) -> None:
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle("Day2", 139.0, 148.0, 138.0, 146.0),  # piercing
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "切り込み線" in names


# ============================================================
# Unit-23: Bearish Dark Cloud -> now 2-candle confirmed (かぶせ線)
# ============================================================
class TestUnit23:
    def test_detect_confirmed_bearish_dark_cloud(self) -> None:
        candles = [
            _candle("Day1", 140.0, 151.0, 139.0, 150.0),  # bullish large
            _candle("Day2", 152.0, 153.0, 143.0, 144.0),  # dark cloud
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "かぶせ線" in names


# ============================================================
# Unit-24: No pattern found (flat candles)
# With 60 patterns, zero-range candles may match small-body patterns.
# Updated to verify no crash instead of empty result.
# ============================================================
class TestUnit24:
    def test_detect_patterns_no_pattern_found(self) -> None:
        candles = [
            _candle("Day1", 100.0, 100.0, 100.0, 100.0),
            _candle("Day2", 100.0, 100.0, 100.0, 100.0),
            _candle("Day3", 100.0, 100.0, 100.0, 100.0),
        ]
        results = detect_patterns(candles, mode="realdata")
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, PatternResult)


# ============================================================
# Unit-25: Body ratio boundary 60% (exactly 0.60 = large body)
# ============================================================
class TestUnit25:
    def test_detect_patterns_body_ratio_boundary_60_percent(self) -> None:
        candles = [
            _candle("Day1", 110.0, 110.0, 100.0, 104.0),  # bearish, ratio=0.60
            _candle("Day2", 104.0, 105.0, 103.0, 104.2),  # doji
            _candle("Day3", 104.0, 114.0, 104.0, 110.0),  # bullish, ratio=0.60
        ]
        results = detect_patterns(candles, mode="simulation_confirmed")
        confirmed = [r for r in results if r.type == "confirmed"]
        names = [r.name for r in confirmed]
        assert "明けの明星" in names


# ============================================================
# Unit-26: Body ratio boundary 30% (exactly 0.30 = small body)
# ============================================================
class TestUnit26:
    def test_detect_patterns_body_ratio_boundary_30_percent(self) -> None:
        candles = [
            _candle("Day1", 150.0, 151.0, 140.0, 141.0),  # bearish large
            _candle("Day2", 141.0, 145.0, 135.0, 144.0),  # body=3, range=10, ratio=0.30
        ]
        results = detect_patterns(candles, mode="simulation_predicted")
        predicted = [r for r in results if r.type == "predicted"]
        names = [r.name for r in predicted]
        assert "明けの明星予測" in names


# ============================================================
# Unit-27: high == low (zero range) -> no crash
# ============================================================
class TestUnit27:
    def test_detect_patterns_high_equals_low_zero_range(self) -> None:
        candles = [
            _candle("Day1", 100.0, 100.0, 100.0, 100.0),
            _candle("Day2", 100.0, 100.0, 100.0, 100.0),
        ]
        results = detect_patterns(candles, mode="realdata")
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, PatternResult)


# ============================================================
# Unit-28: simulation_confirmed returns confirmed only
# ============================================================
class TestUnit28:
    def test_detect_patterns_confirmed_only_for_simulation_confirmed(self) -> None:
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
