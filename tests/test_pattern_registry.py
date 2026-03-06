"""Unit tests for the pattern registry (Unit-01)."""

import pytest

from app.services.pattern_registry import get_all_patterns, validate_pattern_ids


class TestGetAllPatterns:
    """Tests for get_all_patterns()."""

    def test_returns_list(self) -> None:
        """get_all_patterns() returns a list."""
        result = get_all_patterns()
        assert isinstance(result, list)

    def test_required_fields(self) -> None:
        """Each entry has id, name, direction, available_types, pattern_candle_count."""
        for entry in get_all_patterns():
            assert entry.id
            assert entry.name
            assert entry.direction
            assert entry.available_types
            assert entry.pattern_candle_count

    def test_unique_ids(self) -> None:
        """All IDs are unique."""
        patterns = get_all_patterns()
        ids = [p.id for p in patterns]
        assert len(ids) == len(set(ids))

    def test_total_count(self) -> None:
        """Total is 60."""
        patterns = get_all_patterns()
        assert len(patterns) == 60

    def test_three_candle_both_types(self) -> None:
        """3-candle patterns have available_types=["confirmed", "predicted"]."""
        patterns = get_all_patterns()
        three_candle = [p for p in patterns if p.pattern_candle_count == 3]
        assert len(three_candle) > 0
        for p in three_candle:
            assert p.available_types == ["confirmed", "predicted"], (
                f"Pattern {p.id} should have both types"
            )

    def test_one_two_candle_confirmed_only(self) -> None:
        """1 and 2-candle patterns have available_types=["confirmed"]."""
        patterns = get_all_patterns()
        one_two_candle = [p for p in patterns if p.pattern_candle_count in (1, 2)]
        assert len(one_two_candle) > 0
        for p in one_two_candle:
            assert p.available_types == ["confirmed"], (
                f"Pattern {p.id} should have confirmed only"
            )

    def test_direction_values(self) -> None:
        """All directions are either 'bullish' or 'bearish'."""
        patterns = get_all_patterns()
        for p in patterns:
            assert p.direction in ("bullish", "bearish"), (
                f"Pattern {p.id} has invalid direction: {p.direction}"
            )


class TestValidatePatternIds:
    """Tests for validate_pattern_ids()."""

    def test_valid_id_validation(self) -> None:
        """validate_pattern_ids(["morning_star"]) does not raise."""
        validate_pattern_ids(["morning_star"])

    def test_invalid_id_validation(self) -> None:
        """validate_pattern_ids(["nonexistent"]) raises ValueError."""
        with pytest.raises(ValueError, match="Invalid pattern IDs"):
            validate_pattern_ids(["nonexistent"])
