"""Unit tests for get_short_interest_from_info in stock_data service (TDD Red phase).

Tests Unit-13 and Unit-14 for extracting short interest from a pre-fetched info dict.
No yfinance mocking needed since the function takes a plain dict.
"""

from __future__ import annotations

from app.models.candle import ShortInterest
from app.services.stock_data import get_short_interest_from_info


# Unit-13: test_get_short_interest_from_info_with_data
def test_get_short_interest_from_info_with_data() -> None:
    """get_short_interest_from_info should parse info dict into ShortInterest model."""
    info = {
        "shortPercentOfFloat": 0.15,
        "shortRatio": 3.5,
        "sharesShort": 1000000,
        "sharesShortPriorMonth": 900000,
        "dateShortInterest": 1709251200,  # epoch seconds
        "sharesShortPreviousMonthDate": 1706659200,
    }

    result = get_short_interest_from_info(info)

    assert result is not None
    assert isinstance(result, ShortInterest)

    # short_percent_of_float should be multiplied by 100
    assert result.short_percent_of_float == 15.0
    assert result.short_ratio == 3.5
    assert result.shares_short == 1000000
    assert result.shares_short_prior_month == 900000


# Unit-14: test_get_short_interest_from_info_all_none
def test_get_short_interest_from_info_all_none() -> None:
    """get_short_interest_from_info should return None when no short data exists."""
    # Empty dict - no short interest fields present
    result = get_short_interest_from_info({})
    assert result is None


def test_get_short_interest_from_info_all_fields_none() -> None:
    """get_short_interest_from_info should return None when all fields are explicitly None."""
    info = {
        "shortPercentOfFloat": None,
        "shortRatio": None,
        "sharesShort": None,
        "sharesShortPriorMonth": None,
    }

    result = get_short_interest_from_info(info)
    assert result is None
