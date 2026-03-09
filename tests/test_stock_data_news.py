"""Unit tests for get_news function in stock_data service (TDD Red phase).

Tests Unit-09 through Unit-11 for the news fetching feature.
All yfinance calls are mocked.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from app.services.stock_data import get_news

# Fixed "now" for all tests: 2026-03-09T12:00:00 UTC
FIXED_NOW = datetime(2026, 3, 9, 12, 0, 0, tzinfo=UTC)


def _make_news_item(
    item_id: str,
    title: str,
    summary: str,
    pub_date: str,
    provider: str = "Yahoo Finance",
    url: str = "https://example.com/news",
) -> dict:
    """Helper to create a single news item in yfinance format."""
    return {
        "id": item_id,
        "content": {
            "title": title,
            "summary": summary,
            "pubDate": pub_date,
            "provider": {"displayName": provider},
            "canonicalUrl": {"url": url},
        },
    }


# Unit-09: test_get_news_extracts_fields_correctly
@patch("app.services.stock_data.datetime")
@patch("app.services.stock_data.yf")
def test_get_news_extracts_fields_correctly(
    mock_yf: MagicMock,
    mock_datetime: MagicMock,
) -> None:
    """get_news should extract title, summary, pub_date, source, url from each item."""
    mock_datetime.now.return_value = FIXED_NOW
    mock_datetime.fromisoformat = datetime.fromisoformat
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.news = [
        _make_news_item(
            "1",
            "Test News Title 1",
            "Test summary 1",
            "2026-03-08T14:00:00Z",
            "Yahoo Finance",
            "https://example.com/news1",
        ),
        _make_news_item(
            "2",
            "Test News Title 2",
            "Test summary 2",
            "2026-03-07T10:00:00Z",
            "Reuters",
            "https://example.com/news2",
        ),
        _make_news_item(
            "3",
            "Test News Title 3",
            "Test summary 3",
            "2026-03-06T08:00:00Z",
            "Bloomberg",
            "https://example.com/news3",
        ),
    ]

    result = get_news("AAPL", max_items=5, days=7)

    assert isinstance(result, list)
    assert len(result) == 3

    # Verify first item fields
    first = result[0]
    assert first["title"] == "Test News Title 1"
    assert first["summary"] == "Test summary 1"
    assert first["pub_date"] == "2026-03-08T14:00:00Z"
    assert first["source"] == "Yahoo Finance"
    assert first["url"] == "https://example.com/news1"

    # Verify all items have required keys
    required_keys = {"title", "summary", "pub_date", "source", "url"}
    for item in result:
        assert set(item.keys()) >= required_keys


# Unit-10: test_get_news_filters_by_date_and_limit
@patch("app.services.stock_data.datetime")
@patch("app.services.stock_data.yf")
def test_get_news_filters_by_date_and_limit(
    mock_yf: MagicMock,
    mock_datetime: MagicMock,
) -> None:
    """get_news should filter out items older than `days` and cap at `max_items`."""
    mock_datetime.now.return_value = FIXED_NOW
    mock_datetime.fromisoformat = datetime.fromisoformat
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker

    # 3 items from today (within 7 days)
    today_items = [
        _make_news_item(
            f"today-{i}",
            f"Today News {i}",
            f"Today summary {i}",
            "2026-03-09T08:00:00Z",
        )
        for i in range(3)
    ]
    # 3 items from 5 days ago (within 7 days)
    five_days_ago_items = [
        _make_news_item(
            f"5d-{i}",
            f"5 Days Ago News {i}",
            f"5 days ago summary {i}",
            "2026-03-04T08:00:00Z",
        )
        for i in range(3)
    ]
    # 2 items from 10 days ago (outside 7-day window)
    ten_days_ago_items = [
        _make_news_item(
            f"10d-{i}",
            f"10 Days Ago News {i}",
            f"10 days ago summary {i}",
            "2026-02-27T08:00:00Z",
        )
        for i in range(2)
    ]

    mock_ticker.news = today_items + five_days_ago_items + ten_days_ago_items

    result = get_news("AAPL", max_items=5, days=7)

    # 6 items are within the 7-day window, but capped at max_items=5
    assert len(result) == 5

    # Verify no items from 10 days ago are included
    for item in result:
        assert "10 Days Ago" not in item["title"]


# Unit-11: test_get_news_returns_empty_when_no_news
@patch("app.services.stock_data.datetime")
@patch("app.services.stock_data.yf")
def test_get_news_returns_empty_when_no_news(
    mock_yf: MagicMock,
    mock_datetime: MagicMock,
) -> None:
    """get_news should return empty list when no news available."""
    mock_datetime.now.return_value = FIXED_NOW
    mock_datetime.fromisoformat = datetime.fromisoformat
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.news = []

    result = get_news("AAPL", max_items=5, days=7)

    assert isinstance(result, list)
    assert len(result) == 0


@patch("app.services.stock_data.datetime")
@patch("app.services.stock_data.yf")
def test_get_news_returns_empty_when_news_is_none(
    mock_yf: MagicMock,
    mock_datetime: MagicMock,
) -> None:
    """get_news should handle None from yfinance gracefully."""
    mock_datetime.now.return_value = FIXED_NOW
    mock_datetime.fromisoformat = datetime.fromisoformat
    mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.news = None

    result = get_news("AAPL", max_items=5, days=7)

    assert isinstance(result, list)
    assert len(result) == 0
