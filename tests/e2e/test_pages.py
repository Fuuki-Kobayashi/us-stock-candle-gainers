"""E2E tests: verify that all pages load and core UI elements are present."""

import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


def test_index_page_loads(page: Page, base_url: str) -> None:
    """The main analysis page loads with the expected title and input."""
    page.goto(base_url)

    expect(page).to_have_title("US Stock Candle Analysis")
    expect(page.locator("#ticker")).to_be_visible()
    expect(page.locator("#analyze-btn")).to_be_visible()


def test_screener_page_loads(page: Page, base_url: str) -> None:
    """The screener page loads with the ticker textarea and scan button."""
    page.goto(f"{base_url}/screener")

    expect(page).to_have_title("Screener - US Stock Candle Analysis")
    expect(page.locator("#tickers-input")).to_be_visible()
    expect(page.locator("#scan-btn")).to_be_visible()


def test_pattern_search_page_loads(page: Page, base_url: str) -> None:
    """The pattern search page loads with pattern checklist and search button."""
    page.goto(f"{base_url}/pattern-search")

    expect(page).to_have_title("Pattern Search - US Stock Candle Analysis")
    expect(page.locator("#pattern-checklist")).to_be_visible()
    expect(page.locator("#search-btn")).to_be_visible()


def test_index_empty_state_visible(page: Page, base_url: str) -> None:
    """Before analysis, the empty state message is shown."""
    page.goto(base_url)

    expect(page.locator("#empty-state")).to_be_visible()
    expect(page.locator("#results-section")).to_be_hidden()


def test_index_candle_mode_toggle(page: Page, base_url: str) -> None:
    """2-candle / 3-candle mode buttons toggle correctly."""
    page.goto(base_url)

    btn_2 = page.locator("#btn-2candle")
    btn_3 = page.locator("#btn-3candle")

    # Default: 3-candle active
    expect(btn_3).to_have_class(re.compile("mode-btn-active"))

    # Click 2-candle
    btn_2.click()
    expect(btn_2).to_have_class(re.compile("mode-btn-active"))


def test_index_error_on_empty_ticker(page: Page, base_url: str) -> None:
    """Clicking analyze without a ticker shows an error."""
    page.goto(base_url)

    page.locator("#analyze-btn").click()

    expect(page.locator("#error-container")).to_be_visible()


def test_api_health_check(page: Page, base_url: str) -> None:
    """The API docs endpoint responds successfully."""
    response = page.request.get(f"{base_url}/docs")
    assert response.ok
