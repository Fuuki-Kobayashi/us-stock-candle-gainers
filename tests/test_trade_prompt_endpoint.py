"""Integration tests for the /trade-prompt endpoint."""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.exceptions import TickerNotEquityError, TickerNotFoundError
from app.main import app
from app.models.candle import CandleData, PatternResult, ShortInterest
from app.models.risk import FinancialHealth, OfferingRisk, RiskMetric

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

MOCK_INFO = {
    "quoteType": "EQUITY",
    "shortName": "Test Corp",
    "sector": "Technology",
    "industry": "Software",
    "country": "United States",
    "marketCap": 1000000000,
    "sharesOutstanding": 50000000,
    "totalRevenue": 500000000,
    "totalCash": 100000000,
    "totalDebt": 50000000,
    "bookValue": 10.0,
    "priceToBook": 2.5,
    "trailingPE": 15.0,
    "forwardPE": 12.0,
    "fiftyTwoWeekHigh": 30.0,
    "fiftyTwoWeekLow": 15.0,
    "fiftyDayAverage": 25.0,
    "twoHundredDayAverage": 22.0,
    "beta": 1.2,
    "earningsGrowth": 0.15,
    "revenueGrowth": 0.10,
    "shortPercentOfFloat": 0.05,
    "shortRatio": 2.0,
    "sharesShort": 500000,
    "sharesShortPriorMonth": 450000,
    "dateShortInterest": 1709251200,
    "sharesShortPreviousMonthDate": 1706659200,
}

SAMPLE_CANDLES = [
    CandleData(
        date="2024-01-10",
        open=100.0,
        high=105.0,
        low=98.0,
        close=103.0,
        volume=1000000,
    ),
    CandleData(
        date="2024-01-11",
        open=103.0,
        high=108.0,
        low=101.0,
        close=106.0,
        volume=1100000,
    ),
    CandleData(
        date="2024-01-12",
        open=106.0,
        high=110.0,
        low=104.0,
        close=109.0,
        volume=1200000,
    ),
]

SAMPLE_PATTERNS = [
    PatternResult(
        type="confirmed",
        name="Morning Star",
        signal="Bullish",
        description="Reversal pattern",
        direction="bullish",
        pattern_id="morning_star",
        pattern_candle_count=3,
    ),
]

SAMPLE_FH = FinancialHealth(
    de_ratio=RiskMetric(name="D/E", value=0.5, level="\u4f4e", description="d"),
    current_ratio=RiskMetric(name="CR", value=2.0, level="\u4f4e", description="d"),
    profit_margin=RiskMetric(name="PM", value=0.2, level="\u4f4e", description="d"),
    fcf=RiskMetric(name="FCF", value=1e6, level="\u4f4e", description="d"),
    overall_level="\u4f4e",
    summary="s",
)

SAMPLE_OR = OfferingRisk(
    cash_runway=RiskMetric(name="CR", value=36.0, level="\u4f4e", description="d"),
    dilution=RiskMetric(name="DI", value=0.0, level="\u4f4e", description="d"),
    net_income=RiskMetric(name="NI", value=1e5, level="\u4f4e", description="d"),
    debt_cash_ratio=RiskMetric(name="DC", value=0.5, level="\u4f4e", description="d"),
    overall_level="\u4f4e",
    summary="s",
)

SAMPLE_SI = ShortInterest(
    short_percent_of_float=5.0,
    short_ratio=2.0,
    shares_short=500000,
    shares_short_prior_month=450000,
)

SAMPLE_NEWS = [
    {
        "title": "Test Corp Q4 Earnings",
        "summary": "Revenue up",
        "pub_date": "2024-01-12T10:00:00Z",
        "source": "Reuters",
        "url": "https://example.com/1",
    },
]


# ---------------------------------------------------------------------------
# Integ-01: Valid ticker returns prompt
# ---------------------------------------------------------------------------


class TestTradePromptEndpoint:
    @pytest.mark.asyncio
    async def test_trade_prompt_endpoint_returns_prompt_for_valid_ticker(
        self,
    ) -> None:
        """Integ-01: POST /trade-prompt with valid ticker returns 200 with prompt."""
        with (
            patch(
                "app.services.prompt_generator.validate_ticker",
                return_value=MOCK_INFO,
            ),
            patch(
                "app.services.prompt_generator.get_ohlcv",
                return_value=(SAMPLE_CANDLES, 1.5),
            ),
            patch(
                "app.services.prompt_generator.get_news",
                return_value=SAMPLE_NEWS,
            ),
            patch(
                "app.services.prompt_generator.detect_patterns",
                return_value=SAMPLE_PATTERNS,
            ),
            patch(
                "app.services.prompt_generator.analyze_risk",
                return_value=(SAMPLE_FH, SAMPLE_OR),
            ),
            patch(
                "app.services.prompt_generator.get_short_interest_from_info",
                return_value=SAMPLE_SI,
            ),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/trade-prompt", json={"ticker": "TEST"})

        assert response.status_code == 200
        data = response.json()
        assert "ticker" in data
        assert "prompt" in data
        prompt = data["prompt"]
        # Check key section headers
        for section in [
            "Company Profile",
            "Technical Data",
            "Short Interest",
            "Recent News",
            "Instructions",
        ]:
            assert section in prompt, f"Missing section: {section}"

    # -----------------------------------------------------------------------
    # Integ-02: Invalid ticker returns 400
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_trade_prompt_endpoint_invalid_ticker(self) -> None:
        """Integ-02: POST /trade-prompt with invalid ticker returns 400."""
        with patch(
            "app.services.prompt_generator.validate_ticker",
            side_effect=TickerNotFoundError("TEST"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/trade-prompt", json={"ticker": "TEST"})

        assert response.status_code == 400

    # -----------------------------------------------------------------------
    # Integ-03: Non-equity ticker returns 400
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_trade_prompt_endpoint_non_equity_ticker(self) -> None:
        """Integ-03: POST /trade-prompt with ETF ticker returns 400."""
        with patch(
            "app.services.prompt_generator.validate_ticker",
            side_effect=TickerNotEquityError(ticker="SPY", quote_type="ETF"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post("/trade-prompt", json={"ticker": "SPY"})

        assert response.status_code == 400
