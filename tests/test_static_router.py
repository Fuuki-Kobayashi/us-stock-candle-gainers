"""Integration tests for the static router (GET /).

Tests that the root endpoint serves HTML content.
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
INDEX_HTML_PATH = os.path.join(STATIC_DIR, "index.html")


@pytest.fixture(autouse=True)
def ensure_static_index_html():
    """Ensure static/index.html exists for the test.

    Creates a minimal placeholder if not present, and cleans up
    only if we created it.
    """
    created = False
    if not os.path.exists(INDEX_HTML_PATH):
        os.makedirs(STATIC_DIR, exist_ok=True)
        with open(INDEX_HTML_PATH, "w") as f:
            f.write("<!DOCTYPE html><html><body>test</body></html>")
        created = True
    yield
    if created and os.path.exists(INDEX_HTML_PATH):
        os.remove(INDEX_HTML_PATH)


# --- Integ-07: test_get_root_returns_html ---


async def test_get_root_returns_html() -> None:
    """GET / returns 200 with text/html content-type."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type
