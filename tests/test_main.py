"""Tests for main.py app configuration and root endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestAppConfig:
    """Tests for FastAPI app configuration."""

    def test_app_title(self):
        assert app.title == "US Stock Candle Analysis"

    def test_analyze_route_registered(self):
        routes = [r.path for r in app.routes]
        assert "/analyze" in routes

    def test_risk_route_registered(self):
        routes = [r.path for r in app.routes]
        assert "/risk" in routes


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_returns_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestExceptionHandlers:
    """Tests for exception handler registration."""

    def test_exception_handlers_registered(self):
        from app.exceptions import (
            DataFetchError,
            TickerNotEquityError,
            TickerNotFoundError,
        )

        handler_types = list(app.exception_handlers.keys())
        assert TickerNotFoundError in handler_types
        assert TickerNotEquityError in handler_types
        assert DataFetchError in handler_types
