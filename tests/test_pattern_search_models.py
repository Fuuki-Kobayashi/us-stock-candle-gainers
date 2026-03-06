"""Unit-02: PatternSearchRequest model validation tests."""

import pytest
from pydantic import ValidationError

from app.models.pattern_search import PatternSearchRequest


class TestPatternSearchRequest:
    """Tests for PatternSearchRequest validation."""

    def test_valid_request(self) -> None:
        """Valid request with tickers and pattern_ids."""
        req = PatternSearchRequest(
            tickers=["AAPL", "MSFT"],
            pattern_ids=["hammer", "engulfing_bullish"],
        )
        assert req.tickers == ["AAPL", "MSFT"]
        assert req.pattern_ids == ["hammer", "engulfing_bullish"]
        assert req.candle_count == 3

    def test_tickers_max_50(self) -> None:
        """Request with exactly 50 tickers should pass."""
        tickers = [f"TICK{i}" for i in range(50)]
        req = PatternSearchRequest(
            tickers=tickers,
            pattern_ids=["hammer"],
        )
        assert len(req.tickers) == 50

    def test_tickers_exceeds_50(self) -> None:
        """Request with 51 tickers should raise ValidationError."""
        tickers = [f"TICK{i}" for i in range(51)]
        with pytest.raises(ValidationError, match="tickers must not exceed 50"):
            PatternSearchRequest(
                tickers=tickers,
                pattern_ids=["hammer"],
            )

    def test_tickers_empty(self) -> None:
        """Empty tickers list should raise ValidationError."""
        with pytest.raises(ValidationError, match="tickers must not be empty"):
            PatternSearchRequest(
                tickers=[],
                pattern_ids=["hammer"],
            )

    def test_pattern_ids_empty(self) -> None:
        """Empty pattern_ids list should raise ValidationError."""
        with pytest.raises(ValidationError, match="pattern_ids must not be empty"):
            PatternSearchRequest(
                tickers=["AAPL"],
                pattern_ids=[],
            )

    def test_candle_count_default_3(self) -> None:
        """Default candle_count should be 3."""
        req = PatternSearchRequest(
            tickers=["AAPL"],
            pattern_ids=["hammer"],
        )
        assert req.candle_count == 3

    def test_candle_count_invalid(self) -> None:
        """candle_count of 1 or 4 should raise ValidationError."""
        with pytest.raises(ValidationError):
            PatternSearchRequest(
                tickers=["AAPL"],
                pattern_ids=["hammer"],
                candle_count=1,
            )
        with pytest.raises(ValidationError):
            PatternSearchRequest(
                tickers=["AAPL"],
                pattern_ids=["hammer"],
                candle_count=4,
            )
