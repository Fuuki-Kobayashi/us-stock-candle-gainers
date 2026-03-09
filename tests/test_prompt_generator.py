"""Tests for prompt_generator service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.models.candle import CandleData, PatternResult, ShortInterest
from app.models.risk import FinancialHealth, OfferingRisk, RiskMetric

# --- Module-level mock data ---

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

# --- Helper fixtures ---


@pytest.fixture
def sample_info() -> dict:
    return {
        "shortName": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "country": "United States",
        "marketCap": 3000000000000,
        "sharesOutstanding": 15000000000,
        "totalRevenue": 400000000000,
        "totalCash": 60000000000,
        "totalDebt": 120000000000,
        "bookValue": 3.95,
        "priceToBook": 48.0,
        "trailingPE": 30.0,
        "forwardPE": 28.0,
        "fiftyTwoWeekHigh": 200.0,
        "fiftyTwoWeekLow": 140.0,
        "fiftyDayAverage": 185.0,
        "twoHundredDayAverage": 175.0,
        "beta": 1.2,
        "earningsGrowth": 0.15,
        "revenueGrowth": 0.08,
    }


@pytest.fixture
def sample_candles() -> list[CandleData]:
    return [
        CandleData(
            date="2024-01-01",
            open=100.0,
            high=105.0,
            low=99.0,
            close=104.0,
            volume=1000000,
        ),
        CandleData(
            date="2024-01-02",
            open=104.0,
            high=108.0,
            low=103.0,
            close=107.0,
            volume=1200000,
        ),
        CandleData(
            date="2024-01-03",
            open=107.0,
            high=110.0,
            low=106.0,
            close=109.0,
            volume=900000,
        ),
    ]


@pytest.fixture
def sample_pattern() -> PatternResult:
    return PatternResult(
        type="confirmed",
        name="三兵 (Three White Soldiers)",
        signal="Bullish",
        description="Three consecutive bullish candles",
        direction="bullish",
        pattern_id="three_white_soldiers",
        pattern_candle_count=3,
    )


@pytest.fixture
def sample_financial_health() -> FinancialHealth:
    return FinancialHealth(
        de_ratio=RiskMetric(name="D/E", value=0.5, level="低", description="Low debt"),
        current_ratio=RiskMetric(
            name="Current", value=2.0, level="低", description="Good"
        ),
        profit_margin=RiskMetric(
            name="Margin", value=0.25, level="低", description="Good"
        ),
        fcf=RiskMetric(name="FCF", value=100000.0, level="低", description="Positive"),
        overall_level="低",
        summary="財務状態は健全です。主要指標に懸念はありません。",
    )


@pytest.fixture
def sample_offering_risk() -> OfferingRisk:
    return OfferingRisk(
        cash_runway=RiskMetric(name="Runway", value=36.0, level="低", description="OK"),
        dilution=RiskMetric(name="Dilution", value=0.0, level="低", description="Low"),
        net_income=RiskMetric(
            name="NI", value=100000.0, level="低", description="Profit"
        ),
        debt_cash_ratio=RiskMetric(name="D/C", value=0.5, level="低", description="OK"),
        overall_level="低",
        summary="オファリングリスクは低いです。希薄化の懸念は少ないです。",
    )


@pytest.fixture
def sample_short_interest() -> ShortInterest:
    return ShortInterest(
        short_percent_of_float=2.5,
        short_ratio=1.8,
        shares_short=50000000,
        shares_short_prior_month=48000000,
    )


# --- _extract_company_profile ---


class TestExtractCompanyProfile:
    def test_extracts_all_keys(self, sample_info: dict) -> None:
        from app.services.prompt_generator import _extract_company_profile

        profile = _extract_company_profile(sample_info)
        assert profile["shortName"] == "Apple Inc."
        assert profile["sector"] == "Technology"
        assert profile["marketCap"] == 3000000000000

    def test_missing_keys_default_na(self) -> None:
        from app.services.prompt_generator import _extract_company_profile

        profile = _extract_company_profile({})
        assert profile["shortName"] == "N/A"
        assert profile["sector"] == "N/A"
        assert profile["marketCap"] == "N/A"

    def test_partial_info(self) -> None:
        from app.services.prompt_generator import _extract_company_profile

        profile = _extract_company_profile({"shortName": "Test Corp"})
        assert profile["shortName"] == "Test Corp"
        assert profile["industry"] == "N/A"

    def test_extract_company_profile_with_complete_data(self) -> None:
        """Unit-01: All keys present with correct values from MOCK_INFO."""
        from app.services.prompt_generator import _extract_company_profile

        profile = _extract_company_profile(MOCK_INFO)
        assert profile["shortName"] == "Test Corp"
        assert profile["sector"] == "Technology"
        assert profile["industry"] == "Software"
        assert profile["country"] == "United States"
        assert profile["marketCap"] == 1000000000
        assert profile["sharesOutstanding"] == 50000000
        assert profile["totalRevenue"] == 500000000
        assert profile["totalCash"] == 100000000
        assert profile["totalDebt"] == 50000000
        assert profile["bookValue"] == 10.0
        assert profile["priceToBook"] == 2.5
        assert profile["trailingPE"] == 15.0
        assert profile["forwardPE"] == 12.0
        assert profile["fiftyTwoWeekHigh"] == 30.0
        assert profile["fiftyTwoWeekLow"] == 15.0
        assert profile["fiftyDayAverage"] == 25.0
        assert profile["twoHundredDayAverage"] == 22.0
        assert profile["beta"] == 1.2
        assert profile["earningsGrowth"] == 0.15
        assert profile["revenueGrowth"] == 0.10

    def test_extract_company_profile_with_missing_fields(self) -> None:
        """Unit-02: Missing fields default to 'N/A'."""
        from app.services.prompt_generator import _extract_company_profile

        profile = _extract_company_profile({"shortName": "Minimal Corp"})
        assert profile["shortName"] == "Minimal Corp"
        assert profile["sector"] == "N/A"
        assert profile["industry"] == "N/A"
        assert profile["country"] == "N/A"
        assert profile["marketCap"] == "N/A"
        assert profile["sharesOutstanding"] == "N/A"
        assert profile["totalRevenue"] == "N/A"
        assert profile["totalCash"] == "N/A"
        assert profile["totalDebt"] == "N/A"
        assert profile["bookValue"] == "N/A"
        assert profile["priceToBook"] == "N/A"
        assert profile["trailingPE"] == "N/A"
        assert profile["forwardPE"] == "N/A"
        assert profile["fiftyTwoWeekHigh"] == "N/A"
        assert profile["fiftyTwoWeekLow"] == "N/A"
        assert profile["fiftyDayAverage"] == "N/A"
        assert profile["twoHundredDayAverage"] == "N/A"
        assert profile["beta"] == "N/A"
        assert profile["earningsGrowth"] == "N/A"
        assert profile["revenueGrowth"] == "N/A"


# --- _format_company_section ---


class TestFormatCompanySection:
    def test_contains_header(self, sample_info: dict) -> None:
        from app.services.prompt_generator import (
            _extract_company_profile,
            _format_company_section,
        )

        profile = _extract_company_profile(sample_info)
        result = _format_company_section(profile)
        assert "## Company Profile" in result

    def test_contains_company_name(self, sample_info: dict) -> None:
        from app.services.prompt_generator import (
            _extract_company_profile,
            _format_company_section,
        )

        profile = _extract_company_profile(sample_info)
        result = _format_company_section(profile)
        assert "Apple Inc." in result

    def test_contains_all_fields(self, sample_info: dict) -> None:
        from app.services.prompt_generator import (
            _extract_company_profile,
            _format_company_section,
        )

        profile = _extract_company_profile(sample_info)
        result = _format_company_section(profile)
        assert "Sector / Industry" in result
        assert "Market Cap" in result
        assert "52W High" in result
        assert "Beta" in result


# --- _translate_level ---


class TestTranslateLevel:
    def test_translate_low(self) -> None:
        from app.services.prompt_generator import _translate_level

        assert _translate_level("低") == "Low"

    def test_translate_medium(self) -> None:
        from app.services.prompt_generator import _translate_level

        assert _translate_level("中") == "Medium"

    def test_translate_high(self) -> None:
        from app.services.prompt_generator import _translate_level

        assert _translate_level("高") == "High"

    def test_passthrough_english(self) -> None:
        from app.services.prompt_generator import _translate_level

        assert _translate_level("Low") == "Low"


# --- _format_technical_section ---


class TestFormatTechnicalSection:
    def test_contains_ohlcv_header(self, sample_candles: list[CandleData]) -> None:
        from app.services.prompt_generator import _format_technical_section

        result = _format_technical_section(sample_candles, 2.5, [])
        assert "## Technical Data" in result

    def test_contains_candle_data(self, sample_candles: list[CandleData]) -> None:
        from app.services.prompt_generator import _format_technical_section

        result = _format_technical_section(sample_candles, 2.5, [])
        assert "2024-01-01" in result
        assert "100.0" in result or "100.00" in result

    def test_contains_atr(self, sample_candles: list[CandleData]) -> None:
        from app.services.prompt_generator import _format_technical_section

        result = _format_technical_section(sample_candles, 2.5, [])
        assert "ATR" in result
        assert "2.5" in result

    def test_no_patterns_message(self, sample_candles: list[CandleData]) -> None:
        from app.services.prompt_generator import _format_technical_section

        result = _format_technical_section(sample_candles, 2.5, [])
        assert "No candlestick patterns detected" in result

    def test_with_patterns(
        self, sample_candles: list[CandleData], sample_pattern: PatternResult
    ) -> None:
        from app.services.prompt_generator import _format_technical_section

        result = _format_technical_section(sample_candles, 2.5, [sample_pattern])
        assert "Three White Soldiers" in result or "三兵" in result

    def test_atr_none(self, sample_candles: list[CandleData]) -> None:
        from app.services.prompt_generator import _format_technical_section

        result = _format_technical_section(sample_candles, None, [])
        assert "N/A" in result

    def test_format_technical_section_with_candles_and_atr(self) -> None:
        """Unit-03: 3 CandleData, ATR=1.5, empty patterns."""
        from app.services.prompt_generator import _format_technical_section

        candles = [
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
        result = _format_technical_section(candles, atr=1.5, patterns=[])
        for c in candles:
            assert c.date in result
        assert "ATR(14): 1.5" in result

    def test_format_technical_section_with_patterns(self) -> None:
        """Unit-04: Bullish confirmed + bearish predicted patterns present."""
        from app.services.prompt_generator import _format_technical_section

        candles = [
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
        patterns = [
            PatternResult(
                type="confirmed",
                name="Morning Star",
                signal="Bullish",
                description="Reversal",
                direction="bullish",
                pattern_id="morning_star",
                pattern_candle_count=3,
            ),
            PatternResult(
                type="predicted",
                name="Evening Star",
                signal="Bearish",
                description="Reversal",
                required_third="Close below midpoint",
                direction="bearish",
                pattern_id="evening_star",
                pattern_candle_count=3,
            ),
        ]
        result = _format_technical_section(candles, atr=1.5, patterns=patterns)
        assert "Morning Star" in result
        assert "Evening Star" in result
        assert "bullish" in result.lower() or "Bullish" in result
        assert "bearish" in result.lower() or "Bearish" in result

    def test_format_technical_section_no_patterns(self) -> None:
        """Unit-05: Empty patterns shows no-patterns message."""
        from app.services.prompt_generator import _format_technical_section

        candles = [
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
        result = _format_technical_section(candles, atr=1.5, patterns=[])
        assert "No candlestick patterns detected" in result


# --- _format_risk_section ---


class TestFormatRiskSection:
    def test_contains_header(
        self,
        sample_financial_health: FinancialHealth,
        sample_offering_risk: OfferingRisk,
    ) -> None:
        from app.services.prompt_generator import _format_risk_section

        result = _format_risk_section(sample_financial_health, sample_offering_risk)
        assert "## Risk Analysis" in result

    def test_translates_levels(
        self,
        sample_financial_health: FinancialHealth,
        sample_offering_risk: OfferingRisk,
    ) -> None:
        from app.services.prompt_generator import _format_risk_section

        result = _format_risk_section(sample_financial_health, sample_offering_risk)
        assert "Low" in result
        # Japanese levels should be translated
        assert "低" not in result

    def test_format_risk_section_mixed_levels(self) -> None:
        """Unit-06: FinancialHealth and OfferingRisk with mixed levels."""
        from app.services.prompt_generator import _format_risk_section

        fh = FinancialHealth(
            de_ratio=RiskMetric(
                name="D/E Ratio", value=0.5, level="低", description="d"
            ),
            current_ratio=RiskMetric(
                name="Current Ratio", value=1.2, level="中", description="d"
            ),
            profit_margin=RiskMetric(
                name="Profit Margin", value=-0.1, level="高", description="d"
            ),
            fcf=RiskMetric(name="FCF", value=1000000.0, level="低", description="d"),
            overall_level="中",
            summary="summary",
        )
        or_ = OfferingRisk(
            cash_runway=RiskMetric(
                name="Cash Runway", value=18.0, level="低", description="d"
            ),
            dilution=RiskMetric(
                name="Dilution", value=1.0, level="中", description="d"
            ),
            net_income=RiskMetric(
                name="Net Income", value=-500000.0, level="高", description="d"
            ),
            debt_cash_ratio=RiskMetric(
                name="Debt/Cash", value=0.5, level="低", description="d"
            ),
            overall_level="高",
            summary="summary",
        )
        result = _format_risk_section(fh, or_)
        # Check metric names
        assert "D/E" in result
        assert "Current" in result or "current" in result.lower()
        # Check English levels
        assert "Low" in result
        assert "Medium" in result
        assert "High" in result

    def test_high_risk_translated(self) -> None:
        from app.services.prompt_generator import _format_risk_section

        fh = FinancialHealth(
            de_ratio=RiskMetric(
                name="D/E", value=3.0, level="高", description="高い負債水準です。"
            ),
            current_ratio=RiskMetric(
                name="Current", value=0.5, level="高", description="Short term risk"
            ),
            profit_margin=RiskMetric(
                name="Margin", value=-0.1, level="高", description="Loss"
            ),
            fcf=RiskMetric(
                name="FCF", value=-500.0, level="高", description="Negative"
            ),
            overall_level="高",
            summary="財務状態に重大な懸念があります。投資判断には十分な注意が必要です。",
        )
        or_ = OfferingRisk(
            cash_runway=RiskMetric(
                name="Runway", value=6.0, level="高", description="Short"
            ),
            dilution=RiskMetric(
                name="Dilution", value=3.0, level="高", description="High risk"
            ),
            net_income=RiskMetric(
                name="NI", value=-100.0, level="高", description="Loss"
            ),
            debt_cash_ratio=RiskMetric(
                name="D/C", value=5.0, level="高", description="Bad"
            ),
            overall_level="高",
            summary="オファリングリスクが高いです。公募増資による希薄化に警戒が必要です。",
        )
        result = _format_risk_section(fh, or_)
        assert "High" in result


# --- _format_short_interest_section ---


class TestFormatShortInterestSection:
    def test_with_data(self, sample_short_interest: ShortInterest) -> None:
        from app.services.prompt_generator import _format_short_interest_section

        result = _format_short_interest_section(sample_short_interest)
        assert "## Short Interest" in result
        assert "2.5" in result

    def test_none_data(self) -> None:
        from app.services.prompt_generator import _format_short_interest_section

        result = _format_short_interest_section(None)
        assert "Data not available" in result

    def test_format_short_interest_section_with_all_values(self) -> None:
        """Unit-07: ShortInterest with all fields present in output."""
        from app.services.prompt_generator import _format_short_interest_section

        si = ShortInterest(
            short_percent_of_float=5.0,
            short_ratio=2.0,
            shares_short=500000,
            shares_short_prior_month=450000,
        )
        result = _format_short_interest_section(si)
        assert "5.0" in result or "5.00" in result
        assert "2.0" in result or "2.00" in result
        assert "500000" in result or "500,000" in result
        assert "450000" in result or "450,000" in result

    def test_format_short_interest_section_none(self) -> None:
        """Unit-08: None input shows 'Data not available'."""
        from app.services.prompt_generator import _format_short_interest_section

        result = _format_short_interest_section(None)
        assert "Data not available" in result


# --- _format_news_section ---


class TestFormatNewsSection:
    def test_with_news(self) -> None:
        from app.services.prompt_generator import _format_news_section

        news = [
            {
                "title": "Stock rises",
                "summary": "Good earnings",
                "pub_date": "2024-01-03",
                "source": "Reuters",
                "url": "https://example.com",
            },
        ]
        result = _format_news_section(news)
        assert "## Recent News" in result
        assert "Stock rises" in result

    def test_empty_news(self) -> None:
        from app.services.prompt_generator import _format_news_section

        result = _format_news_section([])
        assert "No recent news found" in result

    def test_format_news_section_with_3_items(self) -> None:
        """Unit-15: 3 news items - all titles, dates, sources present."""
        from app.services.prompt_generator import _format_news_section

        news = [
            {
                "title": "Q4 Earnings Beat",
                "summary": "s1",
                "pub_date": "2024-01-12T10:00:00Z",
                "source": "Reuters",
                "url": "https://example.com/1",
            },
            {
                "title": "Expansion to Asia",
                "summary": "s2",
                "pub_date": "2024-01-11T08:00:00Z",
                "source": "Bloomberg",
                "url": "https://example.com/2",
            },
            {
                "title": "Sector Rally",
                "summary": "s3",
                "pub_date": "2024-01-10T14:00:00Z",
                "source": "CNBC",
                "url": "https://example.com/3",
            },
        ]
        result = _format_news_section(news)
        for item in news:
            assert item["title"] in result
            assert item["pub_date"] in result or item["pub_date"][:10] in result
            assert item["source"] in result

    def test_format_news_section_empty(self) -> None:
        """Unit-16: Empty list shows no-news message."""
        from app.services.prompt_generator import _format_news_section

        result = _format_news_section([])
        assert "No recent news found" in result


# --- _format_instructions ---


class TestFormatInstructions:
    def test_contains_direction(self) -> None:
        from app.services.prompt_generator import _format_instructions

        result = _format_instructions()
        assert "Direction" in result or "LONG" in result

    def test_contains_entry_price(self) -> None:
        from app.services.prompt_generator import _format_instructions

        result = _format_instructions()
        assert "Entry Price" in result

    def test_contains_take_profit(self) -> None:
        from app.services.prompt_generator import _format_instructions

        result = _format_instructions()
        assert "Take Profit" in result or "TP1" in result

    def test_contains_stop_loss(self) -> None:
        from app.services.prompt_generator import _format_instructions

        result = _format_instructions()
        assert "Stop Loss" in result

    def test_format_instructions_contains_required_sections(self) -> None:
        """Unit-12: Instructions contain all required output section terms."""
        from app.services.prompt_generator import _format_instructions

        result = _format_instructions()
        required_terms = [
            "Direction",
            "Entry Price",
            "TP1",
            "TP2",
            "TP3",
            "Stop Loss",
            "Catalyst Assessment",
            "Theme Strength",
            "Trade Rationale Summary",
        ]
        for term in required_terms:
            assert term in result, f"Missing required term: {term}"


# --- Risk level translation (Unit-17) ---


class TestRiskLevelTranslation:
    def test_risk_level_translation_japanese_to_english(self) -> None:
        """Unit-17: Japanese levels translated to English; originals absent."""
        from app.services.prompt_generator import _format_risk_section

        fh = FinancialHealth(
            de_ratio=RiskMetric(name="D/E", value=0.5, level="低", description="d"),
            current_ratio=RiskMetric(name="CR", value=1.8, level="中", description="d"),
            profit_margin=RiskMetric(name="PM", value=0.2, level="高", description="d"),
            fcf=RiskMetric(name="FCF", value=1e6, level="低", description="d"),
            overall_level="中",
            summary="test",
        )
        or_ = OfferingRisk(
            cash_runway=RiskMetric(name="CR", value=18.0, level="低", description="d"),
            dilution=RiskMetric(name="DI", value=1.0, level="中", description="d"),
            net_income=RiskMetric(name="NI", value=-5e5, level="高", description="d"),
            debt_cash_ratio=RiskMetric(
                name="DC", value=0.5, level="低", description="d"
            ),
            overall_level="高",
            summary="test",
        )
        result = _format_risk_section(fh, or_)
        # English levels must be present
        assert "Low" in result
        assert "Medium" in result
        assert "High" in result
        # Japanese levels must NOT be present
        assert "\u4f4e" not in result  # 低
        assert "\u4e2d" not in result  # 中
        assert "\u9ad8" not in result  # 高


# --- _assemble_prompt ---


class TestAssemblePrompt:
    def test_contains_ticker(self) -> None:
        from app.services.prompt_generator import _assemble_prompt

        result = _assemble_prompt(
            "AAPL", "company", "technical", "risk", "short", "news", "instructions"
        )
        assert "AAPL" in result

    def test_contains_all_sections(self) -> None:
        from app.services.prompt_generator import _assemble_prompt

        result = _assemble_prompt(
            "AAPL",
            "company_sec",
            "tech_sec",
            "risk_sec",
            "short_sec",
            "news_sec",
            "instr_sec",
        )
        assert "company_sec" in result
        assert "tech_sec" in result
        assert "risk_sec" in result
        assert "short_sec" in result
        assert "news_sec" in result
        assert "instr_sec" in result

    def test_has_separator(self) -> None:
        from app.services.prompt_generator import _assemble_prompt

        result = _assemble_prompt("AAPL", "c", "t", "r", "s", "n", "i")
        assert "---" in result


# --- generate_trade_prompt (integration with mocks) ---


class TestGenerateTradePrompt:
    @pytest.mark.asyncio
    async def test_returns_string(
        self,
        sample_info: dict,
        sample_candles: list[CandleData],
        sample_short_interest: ShortInterest,
        sample_financial_health: FinancialHealth,
        sample_offering_risk: OfferingRisk,
    ) -> None:
        from app.services.prompt_generator import generate_trade_prompt

        with (
            patch(
                "app.services.prompt_generator.validate_ticker",
                return_value=sample_info,
            ),
            patch(
                "app.services.prompt_generator.get_ohlcv",
                return_value=(sample_candles, 2.5),
            ),
            patch("app.services.prompt_generator.get_news", return_value=[]),
            patch(
                "app.services.prompt_generator.get_short_interest_from_info",
                return_value=sample_short_interest,
            ),
            patch(
                "app.services.prompt_generator.analyze_risk",
                return_value=(sample_financial_health, sample_offering_risk),
            ),
            patch("app.services.prompt_generator.detect_patterns", return_value=[]),
        ):
            result = await generate_trade_prompt("AAPL")
            assert isinstance(result, str)
            assert "AAPL" in result

    @pytest.mark.asyncio
    async def test_news_failure_graceful(
        self,
        sample_info: dict,
        sample_candles: list[CandleData],
        sample_financial_health: FinancialHealth,
        sample_offering_risk: OfferingRisk,
    ) -> None:
        from app.services.prompt_generator import generate_trade_prompt

        with (
            patch(
                "app.services.prompt_generator.validate_ticker",
                return_value=sample_info,
            ),
            patch(
                "app.services.prompt_generator.get_ohlcv",
                return_value=(sample_candles, 2.5),
            ),
            patch(
                "app.services.prompt_generator.get_news",
                side_effect=Exception("Network error"),
            ),
            patch(
                "app.services.prompt_generator.get_short_interest_from_info",
                return_value=None,
            ),
            patch(
                "app.services.prompt_generator.analyze_risk",
                return_value=(sample_financial_health, sample_offering_risk),
            ),
            patch("app.services.prompt_generator.detect_patterns", return_value=[]),
        ):
            result = await generate_trade_prompt("AAPL")
            assert isinstance(result, str)
            assert "No recent news found" in result

    @pytest.mark.asyncio
    async def test_generate_trade_prompt_orchestration(self) -> None:
        """Unit-18: All section headers present in orchestrated prompt."""
        from app.services.prompt_generator import generate_trade_prompt

        candles = [
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
        patterns = [
            PatternResult(
                type="confirmed",
                name="Morning Star",
                signal="Bullish",
                description="Rev",
                direction="bullish",
                pattern_id="morning_star",
                pattern_candle_count=3,
            ),
        ]
        fh = FinancialHealth(
            de_ratio=RiskMetric(name="D/E", value=0.5, level="低", description="d"),
            current_ratio=RiskMetric(name="CR", value=2.0, level="低", description="d"),
            profit_margin=RiskMetric(name="PM", value=0.2, level="低", description="d"),
            fcf=RiskMetric(name="FCF", value=1e6, level="低", description="d"),
            overall_level="低",
            summary="s",
        )
        or_ = OfferingRisk(
            cash_runway=RiskMetric(name="CR", value=36.0, level="低", description="d"),
            dilution=RiskMetric(name="DI", value=0.0, level="低", description="d"),
            net_income=RiskMetric(name="NI", value=1e5, level="低", description="d"),
            debt_cash_ratio=RiskMetric(
                name="DC", value=0.5, level="低", description="d"
            ),
            overall_level="低",
            summary="s",
        )
        si = ShortInterest(
            short_percent_of_float=5.0,
            short_ratio=2.0,
            shares_short=500000,
            shares_short_prior_month=450000,
        )
        news = [
            {
                "title": "Good news",
                "summary": "s",
                "pub_date": "2024-01-12",
                "source": "Reuters",
                "url": "http://x.com",
            },
        ]

        with (
            patch(
                "app.services.prompt_generator.validate_ticker", return_value=MOCK_INFO
            ),
            patch(
                "app.services.prompt_generator.get_ohlcv", return_value=(candles, 1.5)
            ),
            patch("app.services.prompt_generator.get_news", return_value=news),
            patch(
                "app.services.prompt_generator.detect_patterns", return_value=patterns
            ),
            patch("app.services.prompt_generator.analyze_risk", return_value=(fh, or_)),
            patch(
                "app.services.prompt_generator.get_short_interest_from_info",
                return_value=si,
            ),
        ):
            result = await generate_trade_prompt("TEST")

        expected_sections = [
            "Company Profile",
            "Technical Data",
            "Financial Health",
            "Offering Risk",
            "Short Interest",
            "Recent News",
            "Instructions",
        ]
        for section in expected_sections:
            assert section in result, f"Missing section: {section}"

    @pytest.mark.asyncio
    async def test_generate_trade_prompt_news_failure_graceful(self) -> None:
        """Unit-19: News failure handled gracefully, prompt still generated."""
        from app.services.prompt_generator import generate_trade_prompt

        candles = [
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
        fh = FinancialHealth(
            de_ratio=RiskMetric(name="D/E", value=0.5, level="低", description="d"),
            current_ratio=RiskMetric(name="CR", value=2.0, level="低", description="d"),
            profit_margin=RiskMetric(name="PM", value=0.2, level="低", description="d"),
            fcf=RiskMetric(name="FCF", value=1e6, level="低", description="d"),
            overall_level="低",
            summary="s",
        )
        or_ = OfferingRisk(
            cash_runway=RiskMetric(name="CR", value=36.0, level="低", description="d"),
            dilution=RiskMetric(name="DI", value=0.0, level="低", description="d"),
            net_income=RiskMetric(name="NI", value=1e5, level="低", description="d"),
            debt_cash_ratio=RiskMetric(
                name="DC", value=0.5, level="低", description="d"
            ),
            overall_level="低",
            summary="s",
        )
        si = ShortInterest(
            short_percent_of_float=5.0,
            short_ratio=2.0,
            shares_short=500000,
            shares_short_prior_month=450000,
        )

        with (
            patch(
                "app.services.prompt_generator.validate_ticker", return_value=MOCK_INFO
            ),
            patch(
                "app.services.prompt_generator.get_ohlcv", return_value=(candles, 1.5)
            ),
            patch(
                "app.services.prompt_generator.get_news",
                side_effect=Exception("News API down"),
            ),
            patch("app.services.prompt_generator.detect_patterns", return_value=[]),
            patch("app.services.prompt_generator.analyze_risk", return_value=(fh, or_)),
            patch(
                "app.services.prompt_generator.get_short_interest_from_info",
                return_value=si,
            ),
        ):
            result = await generate_trade_prompt("TEST")

        assert result is not None
        assert "No recent news found" in result

    @pytest.mark.asyncio
    async def test_generate_trade_prompt_partial_info_fields(self) -> None:
        """Unit-20: Minimal info produces prompt with N/A for missing fields."""
        from app.services.prompt_generator import generate_trade_prompt

        minimal_info = {"quoteType": "EQUITY", "shortName": "Minimal Corp"}
        candles = [
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
        fh = FinancialHealth(
            de_ratio=RiskMetric(name="D/E", value=None, level="中", description="d"),
            current_ratio=RiskMetric(
                name="CR", value=None, level="中", description="d"
            ),
            profit_margin=RiskMetric(
                name="PM", value=None, level="中", description="d"
            ),
            fcf=RiskMetric(name="FCF", value=None, level="中", description="d"),
            overall_level="中",
            summary="s",
        )
        or_ = OfferingRisk(
            cash_runway=RiskMetric(name="CR", value=None, level="中", description="d"),
            dilution=RiskMetric(name="DI", value=None, level="中", description="d"),
            net_income=RiskMetric(name="NI", value=None, level="中", description="d"),
            debt_cash_ratio=RiskMetric(
                name="DC", value=None, level="中", description="d"
            ),
            overall_level="中",
            summary="s",
        )

        with (
            patch(
                "app.services.prompt_generator.validate_ticker",
                return_value=minimal_info,
            ),
            patch(
                "app.services.prompt_generator.get_ohlcv", return_value=(candles, 1.5)
            ),
            patch("app.services.prompt_generator.get_news", return_value=[]),
            patch("app.services.prompt_generator.detect_patterns", return_value=[]),
            patch("app.services.prompt_generator.analyze_risk", return_value=(fh, or_)),
            patch(
                "app.services.prompt_generator.get_short_interest_from_info",
                return_value=None,
            ),
        ):
            result = await generate_trade_prompt("TEST")

        assert result is not None
        assert "N/A" in result


# --- Router tests ---


class TestTradePromptRouter:
    def test_router_import(self) -> None:
        from app.routers.trade_prompt import router

        assert router is not None

    @pytest.mark.asyncio
    async def test_endpoint_calls_generator(self) -> None:
        from app.models.trade_prompt import TradePromptRequest
        from app.routers.trade_prompt import trade_prompt

        with patch("app.routers.trade_prompt.prompt_generator") as mock_gen:
            mock_gen.generate_trade_prompt = AsyncMock(return_value="test prompt")
            req = TradePromptRequest(ticker="AAPL")
            resp = await trade_prompt(req)
            assert resp.ticker == "AAPL"
            assert resp.prompt == "test prompt"
            mock_gen.generate_trade_prompt.assert_awaited_once_with("AAPL")
