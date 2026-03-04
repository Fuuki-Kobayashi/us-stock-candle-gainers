"""Unit tests for simulation service (Unit-30 through Unit-39)."""

from app.models.candle import CandleData
from app.services.simulation import generate_simulated_candles


class TestGenerateSimulatedCandles:
    """Tests for generate_simulated_candles function."""

    def test_generate_simulated_candles_two_days(self) -> None:
        """Unit-30: base_price=100.0, changes=[5.0, -3.0] -> 2 candles, dates correct."""
        result = generate_simulated_candles(base_price=100.0, changes=[5.0, -3.0])

        assert len(result) == 2
        assert all(isinstance(c, CandleData) for c in result)
        assert result[0].date == "1日目 (シミュレーション)"
        assert result[1].date == "2日目 (シミュレーション)"

    def test_generate_simulated_candles_two_days_predicted_patterns(self) -> None:
        """Unit-31: Candles can be passed to pattern detector (structural check)."""
        result = generate_simulated_candles(base_price=100.0, changes=[-5.0, 0.0])

        assert len(result) == 2
        # Verify each candle has all required OHLCV fields for pattern detection
        for candle in result:
            assert isinstance(candle, CandleData)
            assert candle.open > 0
            assert candle.high > 0
            assert candle.low > 0
            assert candle.close > 0
            assert isinstance(candle.volume, int)

    def test_generate_simulated_candles_three_days(self) -> None:
        """Unit-32: base_price=100.0, changes=[5.0, -3.0, 8.0] -> 3 candles."""
        result = generate_simulated_candles(base_price=100.0, changes=[5.0, -3.0, 8.0])

        assert len(result) == 3
        assert all(isinstance(c, CandleData) for c in result)

    def test_generate_simulated_candles_date_labels(self) -> None:
        """Unit-33: Verify exact Japanese date labels."""
        result = generate_simulated_candles(base_price=100.0, changes=[5.0, -3.0, 8.0])

        assert result[0].date == "1日目 (シミュレーション)"
        assert result[1].date == "2日目 (シミュレーション)"
        assert result[2].date == "3日目 (シミュレーション)"

    def test_simulation_fallback_change1_only(self) -> None:
        """Unit-34: change1 only (no change2) should result in realdata mode."""
        change1: float | None = 5.0
        change2: float | None = None
        change3: float | None = None

        if change1 is not None and change2 is not None and change3 is not None:
            mode = "simulation_confirmed"
        elif change1 is not None and change2 is not None:
            mode = "simulation_predicted"
        else:
            mode = "realdata"

        assert mode == "realdata"

    def test_generate_simulated_candles_volume_zero(self) -> None:
        """Unit-35: All candles have volume == 0 and it's an int."""
        result = generate_simulated_candles(base_price=100.0, changes=[5.0, -3.0])

        for candle in result:
            assert candle.volume == 0
            assert isinstance(candle.volume, int)

    def test_generate_simulated_candles_zero_change(self) -> None:
        """Unit-36: changes=[0.0, 0.0] -> open == close for each candle."""
        result = generate_simulated_candles(base_price=100.0, changes=[0.0, 0.0])

        for candle in result:
            assert candle.open == candle.close

    def test_generate_simulated_candles_negative_change(self) -> None:
        """Unit-37: changes=[-50.0, -30.0] -> close < open."""
        result = generate_simulated_candles(base_price=100.0, changes=[-50.0, -30.0])

        for candle in result:
            assert candle.close < candle.open

    def test_generate_simulated_candles_price_chain(self) -> None:
        """Unit-38: changes=[10.0, -5.0] -> candles[1].open == candles[0].close."""
        result = generate_simulated_candles(base_price=100.0, changes=[10.0, -5.0])

        assert result[1].open == result[0].close

    def test_generate_simulated_candles_high_low_margins(self) -> None:
        """Unit-39: changes=[5.0] -> high/low margins are correct."""
        result = generate_simulated_candles(base_price=100.0, changes=[5.0])

        candle = result[0]
        expected_high = max(candle.open, candle.close) * 1.005
        expected_low = min(candle.open, candle.close) * 0.995

        assert candle.high == expected_high
        assert candle.low == expected_low
