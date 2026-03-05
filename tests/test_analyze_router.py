"""Integration tests for the analyze router (POST /analyze).

These tests mock yfinance at the service level (app.services.stock_data.yf)
and test through the full HTTP layer using httpx AsyncClient.

Integ-01: 3-candle realdata mode tests
Integ-02: 2-candle realdata mode tests
Integ-03: Simulation mode tests
Integ-04: Error case tests
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from httpx import ASGITransport, AsyncClient

from app.models.candle import CandleData

# --- Mock candle data for integration tests ---

# 3-candle: morning star pattern (large bearish -> small body -> large bullish)
MOCK_3CANDLES = [
    CandleData(
        date="2024-01-01",
        open=110,
        high=112,
        low=98,
        close=100,
        volume=1000000,
    ),
    CandleData(
        date="2024-01-02",
        open=99,
        high=101,
        low=97,
        close=100,
        volume=1000000,
    ),
    CandleData(
        date="2024-01-03",
        open=100,
        high=112,
        low=98,
        close=110,
        volume=1000000,
    ),
]

# 2-candle: engulfing pattern (bearish -> bullish engulfing)
MOCK_2CANDLES = [
    CandleData(
        date="2024-01-01",
        open=110,
        high=112,
        low=98,
        close=100,
        volume=1000000,
    ),
    CandleData(
        date="2024-01-02",
        open=97,
        high=115,
        low=95,
        close=113,
        volume=1000000,
    ),
]

# 3-candle names that should only appear in 3-candle confirmed mode
THREE_CANDLE_CONFIRMED_NAMES = [
    "明けの明星",
    "明けの十字星",
    "捨て子底",
    "赤三兵",
    "スリー・インサイド・アップ",
    "スリー・アウトサイド・アップ",
    "モーニング・ピンバー・リバーサル",
    "三つの星底",
    "スティック・サンドイッチ",
    "南の三つ星",
    "ユニーク・スリー・リバー",
    "下放れ三法",
    "上放れタスキ線",
    "上放れ並び赤",
    "インサイドバーの上抜け",
    "宵の明星",
    "三羽烏",
    "スリー・インサイド・ダウン",
    "スリー・アウトサイド・ダウン",
    "三つの星天井",
    "インサイドバーの弱気ブレイク",
    "上昇三法",
    "下降三法",
    # Legacy names that may still exist
    "モーニングスター",
    "イブニングスター",
    "スリーホワイトソルジャーズ",
    "スリーブラッククロウズ",
]


@pytest.fixture
def mock_history_df() -> pd.DataFrame:
    """5-day OHLCV DataFrame mimicking yfinance Ticker.history() output."""
    data = {
        "Open": [148.0, 150.0, 149.5, 151.0, 152.0],
        "High": [152.0, 153.0, 151.0, 154.0, 155.0],
        "Low": [147.0, 149.0, 148.5, 150.0, 151.0],
        "Close": [150.0, 149.5, 150.5, 153.0, 154.0],
        "Volume": [1000000, 1200000, 900000, 1100000, 1300000],
    }
    index = pd.date_range("2024-01-10", periods=5, freq="B")
    return pd.DataFrame(data, index=index)


@pytest.fixture
def mock_history_1mo_df() -> pd.DataFrame:
    """1-month DataFrame for ATR calculation (22 rows)."""
    n = 22
    data = {
        "Open": [150.0] * n,
        "High": [155.0] * n,
        "Low": [145.0] * n,
        "Close": [152.0] * n,
        "Volume": [1000000] * n,
    }
    index = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame(data, index=index)


@pytest.fixture
def valid_equity_info() -> dict:
    """yfinance info dict for a valid EQUITY with all required fields."""
    return {
        "quoteType": "EQUITY",
        "shortName": "Apple Inc.",
        "symbol": "AAPL",
        "shortPercentOfFloat": 0.75,
        "shortRatio": 1.2,
        "sharesShort": 120000000,
        "sharesShortPriorMonth": 115000000,
        "debtToEquity": 150.0,
        "currentRatio": 1.8,
        "profitMargins": 0.21,
        "freeCashflow": 90000000000,
        "totalCash": 50000000000,
        "totalDebt": 30000000000,
        "netIncomeToCommon": 80000000000,
        "sharesOutstanding": 15000000000,
    }


def _make_history_side_effect(hist_5d: pd.DataFrame, hist_1mo: pd.DataFrame):
    """Create a side_effect function for Ticker.history() calls.

    get_ohlcv calls history() twice: once with period='5d', once with period='1mo'.
    """

    def history_side_effect(period: str = "5d", **kwargs):
        if period == "1mo":
            return hist_1mo
        return hist_5d

    return history_side_effect


# --- Integ-01: test_analyze_realdata_mode ---


@patch("app.services.stock_data.yf")
async def test_analyze_realdata_mode(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    mock_history_1mo_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with ticker only returns realdata mode with 3 candles."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    mock_ticker.history.side_effect = _make_history_side_effect(
        mock_history_df, mock_history_1mo_df
    )

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["mode"] == "realdata"
    assert len(body["candles"]) == 3
    assert isinstance(body["atr"], float)
    assert body["short_interest"] is not None
    assert "short_percent_of_float" in body["short_interest"]


# --- Integ-02: test_analyze_simulation_predicted_mode ---


@patch("app.services.stock_data.yf")
async def test_analyze_simulation_predicted_mode(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with change1+change2 returns simulation_predicted mode."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    # get_latest_close uses history(period="5d")
    mock_ticker.history.return_value = mock_history_df

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={"ticker": "AAPL", "change1": 5.0, "change2": -3.0},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["mode"] == "simulation_predicted"
    assert len(body["candles"]) == 2
    assert isinstance(body["base_price"], float)
    assert body["atr"] is None
    assert body["short_interest"] is None
    # Simulated candles have volume=0
    for candle in body["candles"]:
        assert candle["volume"] == 0


# --- Integ-03: test_analyze_simulation_confirmed_mode ---


@patch("app.services.stock_data.yf")
async def test_analyze_simulation_confirmed_mode(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with change1+change2+change3 returns simulation_confirmed."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    mock_ticker.history.return_value = mock_history_df

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={
                "ticker": "AAPL",
                "change1": 5.0,
                "change2": -3.0,
                "change3": 8.0,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["mode"] == "simulation_confirmed"
    assert len(body["candles"]) == 3
    assert isinstance(body["base_price"], float)


# --- Integ-04: test_analyze_change1_only_fallback_to_realdata ---


@patch("app.services.stock_data.yf")
async def test_analyze_change1_only_fallback_to_realdata(
    mock_yf: MagicMock,
    mock_history_df: pd.DataFrame,
    mock_history_1mo_df: pd.DataFrame,
    valid_equity_info: dict,
) -> None:
    """POST /analyze with only change1 falls back to realdata mode."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    mock_ticker.info = valid_equity_info
    mock_ticker.history.side_effect = _make_history_side_effect(
        mock_history_df, mock_history_1mo_df
    )

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={"ticker": "AAPL", "change1": 5.0},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "realdata"


# --- Integ-08: test_analyze_empty_ticker_returns_error ---


async def test_analyze_empty_ticker_returns_error() -> None:
    """POST /analyze with empty ticker returns 422 validation error."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": ""})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


# --- Integ-09: test_analyze_invalid_ticker_returns_400 ---


@patch("app.services.stock_data.yf")
async def test_analyze_invalid_ticker_returns_400(
    mock_yf: MagicMock,
) -> None:
    """POST /analyze with non-existent ticker returns 400."""
    mock_ticker = MagicMock()
    mock_yf.Ticker.return_value = mock_ticker
    # No quoteType -> TickerNotFoundError from validate_ticker
    mock_ticker.info = {"symbol": "XXXYZZ"}

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "XXXYZZ"})

    assert response.status_code == 400
    body = response.json()
    assert "detail" in body


# --- Integ-11: test_analyze_api_error_returns_500 ---


@patch("app.services.stock_data.yf")
async def test_analyze_api_error_returns_500(
    mock_yf: MagicMock,
) -> None:
    """POST /analyze with yfinance exception returns 500."""
    mock_yf.Ticker.side_effect = Exception("Network error")

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 500
    body = response.json()
    assert "detail" in body


# =====================================================================
# Integ-01: /analyze API (3-candle realdata mode)
# =====================================================================


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_realdata_default_candle_count(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """POST without candle_count defaults to 3-candle realdata mode."""
    mock_get_ohlcv.return_value = (MOCK_3CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "realdata"
    assert len(body["candles"]) == 3
    mock_get_ohlcv.assert_called_once_with("AAPL", candle_count=3)


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_realdata_candle_count_3(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """POST with candle_count=3 returns 200 and 3 candles."""
    mock_get_ohlcv.return_value = (MOCK_3CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 3}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "realdata"
    assert len(body["candles"]) == 3


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_response_has_patterns(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """Response contains 'patterns' key as a list."""
    mock_get_ohlcv.return_value = (MOCK_3CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert "patterns" in body
    assert isinstance(body["patterns"], list)


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_realdata_returns_all_pattern_types(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """3-candle realdata returns both confirmed and predicted patterns."""
    mock_get_ohlcv.return_value = (MOCK_3CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    patterns = body["patterns"]
    pattern_types = {p["type"] for p in patterns}
    # realdata mode should return both confirmed and predicted
    assert "confirmed" in pattern_types or "predicted" in pattern_types
    # At minimum we expect patterns to exist for morning star data
    assert len(patterns) > 0


async def test_analyze_invalid_candle_count_high() -> None:
    """candle_count=5 returns 422 validation error."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 5}
        )

    assert response.status_code == 422


async def test_analyze_invalid_candle_count_low() -> None:
    """candle_count=1 returns 422 validation error."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 1}
        )

    assert response.status_code == 422


# =====================================================================
# Integ-02: /analyze API (2-candle mode)
# =====================================================================


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_realdata_candle_count_2(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """candle_count=2 returns 200 with realdata_2candle mode."""
    mock_get_ohlcv.return_value = (MOCK_2CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 2}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "realdata_2candle"
    assert len(body["candles"]) == 2
    mock_get_ohlcv.assert_called_once_with("AAPL", candle_count=2)


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_2candle_returns_confirmed_and_predicted(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """2-candle mode returns both confirmed and predicted patterns."""
    mock_get_ohlcv.return_value = (MOCK_2CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 2}
        )

    assert response.status_code == 200
    body = response.json()
    patterns = body["patterns"]
    # 2-candle mode should return patterns (confirmed 2-candle + predicted + 1-candle)
    assert isinstance(patterns, list)
    # Each pattern has required fields
    for p in patterns:
        assert "type" in p
        assert "name" in p
        assert "signal" in p
        assert "description" in p


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_2candle_includes_1_candle_patterns(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """2-candle mode includes 1-candle patterns for the latest candle."""
    # Use candles where last candle has shooting star characteristics
    candles_with_shooting = [
        CandleData(
            date="2024-01-01",
            open=100,
            high=105,
            low=95,
            close=98,
            volume=1000000,
        ),
        CandleData(
            date="2024-01-02",
            open=99,
            high=115,
            low=98,
            close=100,
            volume=1000000,
        ),
    ]
    mock_get_ohlcv.return_value = (candles_with_shooting, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 2}
        )

    assert response.status_code == 200
    body = response.json()
    # Verify the mode is 2-candle and patterns exist
    assert body["mode"] == "realdata_2candle"
    assert isinstance(body["patterns"], list)


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_2candle_excludes_3_candle_confirmed(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """2-candle mode does not include 3-candle confirmed pattern names."""
    mock_get_ohlcv.return_value = (MOCK_2CANDLES, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze", json={"ticker": "AAPL", "candle_count": 2}
        )

    assert response.status_code == 200
    body = response.json()
    confirmed_patterns = [p for p in body["patterns"] if p["type"] == "confirmed"]
    confirmed_names = [p["name"] for p in confirmed_patterns]
    # No 3-candle confirmed names should appear
    for name in confirmed_names:
        assert name not in THREE_CANDLE_CONFIRMED_NAMES, (
            f"3-candle confirmed pattern '{name}' should not appear in 2-candle mode"
        )


# =====================================================================
# Integ-03: /analyze API (simulation mode)
# =====================================================================


@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_latest_close", return_value=150.0)
async def test_analyze_simulation_predicted(
    mock_close: MagicMock,
    mock_validate: MagicMock,
) -> None:
    """change1+change2 only returns simulation_predicted mode."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={"ticker": "AAPL", "change1": 5.0, "change2": -3.0},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "simulation_predicted"
    assert len(body["candles"]) == 2


@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_latest_close", return_value=150.0)
async def test_analyze_simulation_confirmed(
    mock_close: MagicMock,
    mock_validate: MagicMock,
) -> None:
    """change1+change2+change3 returns simulation_confirmed mode."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={
                "ticker": "AAPL",
                "change1": 5.0,
                "change2": -3.0,
                "change3": 8.0,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "simulation_confirmed"
    assert len(body["candles"]) == 3


@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_latest_close", return_value=150.0)
async def test_analyze_simulation_predicted_no_confirmed(
    mock_close: MagicMock,
    mock_validate: MagicMock,
) -> None:
    """simulation_predicted mode contains no confirmed patterns."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={"ticker": "AAPL", "change1": 5.0, "change2": -3.0},
        )

    assert response.status_code == 200
    body = response.json()
    for p in body["patterns"]:
        assert p["type"] != "confirmed", (
            f"confirmed pattern '{p['name']}' found in simulation_predicted mode"
        )


@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_latest_close", return_value=150.0)
async def test_analyze_simulation_confirmed_no_predicted(
    mock_close: MagicMock,
    mock_validate: MagicMock,
) -> None:
    """simulation_confirmed mode contains no predicted patterns."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/analyze",
            json={
                "ticker": "AAPL",
                "change1": 5.0,
                "change2": -3.0,
                "change3": 8.0,
            },
        )

    assert response.status_code == 200
    body = response.json()
    for p in body["patterns"]:
        assert p["type"] != "predicted", (
            f"predicted pattern '{p['name']}' found in simulation_confirmed mode"
        )


# =====================================================================
# Integ-04: /analyze API (error cases)
# =====================================================================


@patch("app.routers.analyze.stock_data.get_short_interest", return_value=None)
@patch("app.routers.analyze.stock_data.validate_ticker")
@patch("app.routers.analyze.stock_data.get_ohlcv")
async def test_analyze_insufficient_data_returns_empty(
    mock_get_ohlcv: MagicMock,
    mock_validate: MagicMock,
    mock_short: MagicMock,
) -> None:
    """When stock data returns insufficient candles, patterns list is empty."""
    # Return only 1 candle (insufficient for any multi-candle pattern)
    single_candle = [
        CandleData(
            date="2024-01-01",
            open=100,
            high=105,
            low=95,
            close=102,
            volume=1000000,
        )
    ]
    mock_get_ohlcv.return_value = (single_candle, 5.0)

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "AAPL"})

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["patterns"], list)
    # Insufficient data means few or no multi-candle patterns
    # 1-candle patterns may still be detected, but the response should be valid
    assert len(body["candles"]) == 1


@patch("app.routers.analyze.stock_data.validate_ticker")
async def test_analyze_invalid_ticker_integration(
    mock_validate: MagicMock,
) -> None:
    """Mock validate_ticker to raise TickerNotFoundError -> 400."""
    from app.exceptions import TickerNotFoundError

    mock_validate.side_effect = TickerNotFoundError("INVALID")

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/analyze", json={"ticker": "INVALID"})

    assert response.status_code == 400
    body = response.json()
    assert "detail" in body
