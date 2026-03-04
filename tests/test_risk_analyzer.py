"""Unit tests for risk_analyzer service (Unit-40 through Unit-60)."""

from app.models.risk import FinancialHealth, OfferingRisk
from app.services.risk_analyzer import analyze_risk


def make_info(**overrides: object) -> dict:
    """Build a healthy baseline info dict with optional overrides."""
    base: dict = {
        "debtToEquity": 50.0,  # 0.5x -> low
        "currentRatio": 2.0,  # > 1.5 -> low
        "profitMargins": 0.20,  # > 0.10 -> low
        "freeCashflow": 1_000_000_000,  # > 0 -> low
        "totalCash": 10_000_000_000,
        "totalDebt": 3_000_000_000,
        "netIncomeToCommon": 5_000_000_000,  # > 0 -> low
        "sharesOutstanding": 1_000_000_000,
    }
    base.update(overrides)
    return base


# ------------------------------------------------------------------
# Unit-40: Return type
# ------------------------------------------------------------------
class TestUnit40ReturnType:
    def test_analyze_risk_returns_two_categories(self) -> None:
        info = make_info()
        result = analyze_risk(info)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], FinancialHealth)
        assert isinstance(result[1], OfferingRisk)


# ------------------------------------------------------------------
# Unit-41: All fields present
# ------------------------------------------------------------------
class TestUnit41AllFieldsPresent:
    def test_analyze_risk_with_all_fields_present(self) -> None:
        info = make_info()
        fh, ofr = analyze_risk(info)
        # Every metric should have a non-None value
        for metric in [fh.de_ratio, fh.current_ratio, fh.profit_margin, fh.fcf]:
            assert metric.value is not None
        for metric in [
            ofr.cash_runway,
            ofr.dilution,
            ofr.net_income,
            ofr.debt_cash_ratio,
        ]:
            assert metric.value is not None


# ------------------------------------------------------------------
# Unit-42: D/E ratio low
# ------------------------------------------------------------------
class TestUnit42DeRatioLow:
    def test_financial_health_de_ratio_low(self) -> None:
        info = make_info(debtToEquity=80.0)  # 0.8x < 1.0
        fh, _ = analyze_risk(info)
        assert fh.de_ratio.level == "\u4f4e"


# ------------------------------------------------------------------
# Unit-43: D/E ratio high
# ------------------------------------------------------------------
class TestUnit43DeRatioHigh:
    def test_financial_health_de_ratio_high(self) -> None:
        info = make_info(debtToEquity=250.0)  # 2.5x > 2.0
        fh, _ = analyze_risk(info)
        assert fh.de_ratio.level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-44: Current ratio low risk
# ------------------------------------------------------------------
class TestUnit44CurrentRatioLowRisk:
    def test_financial_health_current_ratio_low_risk(self) -> None:
        info = make_info(currentRatio=2.0)  # > 1.5
        fh, _ = analyze_risk(info)
        assert fh.current_ratio.level == "\u4f4e"


# ------------------------------------------------------------------
# Unit-45: Profit margin negative
# ------------------------------------------------------------------
class TestUnit45ProfitMarginNegative:
    def test_financial_health_profit_margin_negative(self) -> None:
        info = make_info(profitMargins=-0.05)  # < 0
        fh, _ = analyze_risk(info)
        assert fh.profit_margin.level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-46: Cash runway under 12 months
# ------------------------------------------------------------------
class TestUnit46CashRunwayUnder12:
    def test_offering_risk_cash_runway_under_12_months(self) -> None:
        info = make_info(totalCash=1_000_000, netIncomeToCommon=-2_000_000)
        # months = 1_000_000 / 2_000_000 * 12 = 6
        _, ofr = analyze_risk(info)
        assert ofr.cash_runway.level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-47: Cash runway profitable
# ------------------------------------------------------------------
class TestUnit47CashRunwayProfitable:
    def test_offering_risk_cash_runway_profitable(self) -> None:
        info = make_info(netIncomeToCommon=5_000_000_000)
        _, ofr = analyze_risk(info)
        assert ofr.cash_runway.level == "\u4f4e"


# ------------------------------------------------------------------
# Unit-48: Dilution high
# ------------------------------------------------------------------
class TestUnit48DilutionHigh:
    def test_offering_risk_dilution_high(self) -> None:
        info = make_info(
            netIncomeToCommon=-1_000_000,
            freeCashflow=-500_000,
            debtToEquity=250.0,  # 2.5x > 2.0
        )
        _, ofr = analyze_risk(info)
        assert ofr.dilution.level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-49: Debt/cash ratio over 3
# ------------------------------------------------------------------
class TestUnit49DebtCashRatioOver3:
    def test_offering_risk_debt_cash_ratio_over_3(self) -> None:
        info = make_info(totalDebt=4_000_000, totalCash=1_000_000)
        _, ofr = analyze_risk(info)
        assert ofr.debt_cash_ratio.level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-50: All low -> overall low
# ------------------------------------------------------------------
class TestUnit50AllLow:
    def test_risk_level_all_low(self) -> None:
        info = make_info()
        fh, ofr = analyze_risk(info)
        assert fh.overall_level == "\u4f4e"
        assert ofr.overall_level == "\u4f4e"


# ------------------------------------------------------------------
# Unit-51: One medium -> overall medium
# ------------------------------------------------------------------
class TestUnit51OneMediumOverallMedium:
    def test_risk_level_one_medium_overall_medium(self) -> None:
        # D/E = 1.0 -> medium, rest low
        info = make_info(debtToEquity=100.0)
        fh, _ = analyze_risk(info)
        assert fh.overall_level == "\u4e2d"


# ------------------------------------------------------------------
# Unit-52: One high -> overall high
# ------------------------------------------------------------------
class TestUnit52OneHighOverallHigh:
    def test_risk_level_one_high_overall_high(self) -> None:
        # profitMargins negative -> high, rest low
        info = make_info(profitMargins=-0.05)
        fh, _ = analyze_risk(info)
        assert fh.overall_level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-53: Financial health summary text
# ------------------------------------------------------------------
class TestUnit53FinancialHealthSummary:
    def test_financial_health_summary_text_by_level(self) -> None:
        # Low
        info_low = make_info()
        fh_low, _ = analyze_risk(info_low)
        assert (
            fh_low.summary
            == "\u8ca1\u52d9\u72b6\u614b\u306f\u5065\u5168\u3067\u3059\u3002\u4e3b\u8981\u6307\u6a19\u306b\u61f8\u5ff5\u306f\u3042\u308a\u307e\u305b\u3093\u3002"
        )

        # Medium
        info_med = make_info(debtToEquity=100.0)
        fh_med, _ = analyze_risk(info_med)
        assert (
            fh_med.summary
            == "\u8ca1\u52d9\u72b6\u614b\u306b\u4e00\u90e8\u6ce8\u610f\u304c\u5fc5\u8981\u306a\u6307\u6a19\u304c\u3042\u308a\u307e\u3059\u3002"
        )

        # High
        info_high = make_info(profitMargins=-0.05)
        fh_high, _ = analyze_risk(info_high)
        assert (
            fh_high.summary
            == "\u8ca1\u52d9\u72b6\u614b\u306b\u91cd\u5927\u306a\u61f8\u5ff5\u304c\u3042\u308a\u307e\u3059\u3002\u6295\u8cc7\u5224\u65ad\u306b\u306f\u5341\u5206\u306a\u6ce8\u610f\u304c\u5fc5\u8981\u3067\u3059\u3002"
        )


# ------------------------------------------------------------------
# Unit-54: Offering risk summary text
# ------------------------------------------------------------------
class TestUnit54OfferingRiskSummary:
    def test_offering_risk_summary_text_by_level(self) -> None:
        # Low
        info_low = make_info()
        _, ofr_low = analyze_risk(info_low)
        assert (
            ofr_low.summary
            == "\u30aa\u30d5\u30a1\u30ea\u30f3\u30b0\u30ea\u30b9\u30af\u306f\u4f4e\u3044\u3067\u3059\u3002\u5e0c\u8584\u5316\u306e\u61f8\u5ff5\u306f\u5c11\u306a\u3044\u3067\u3059\u3002"
        )

        # Medium - net income zero (medium) + dilution medium, rest low
        info_med = make_info(netIncomeToCommon=0, freeCashflow=1_000_000_000)
        _, ofr_med = analyze_risk(info_med)
        assert (
            ofr_med.summary
            == "\u30aa\u30d5\u30a1\u30ea\u30f3\u30b0\u30ea\u30b9\u30af\u306b\u6ce8\u610f\u304c\u5fc5\u8981\u3067\u3059\u3002\u4e00\u90e8\u306e\u6307\u6a19\u3092\u76e3\u8996\u3057\u3066\u304f\u3060\u3055\u3044\u3002"
        )

        # High
        info_high = make_info(
            netIncomeToCommon=-2_000_000,
            totalCash=1_000_000,
            freeCashflow=-500_000,
            debtToEquity=250.0,
        )
        _, ofr_high = analyze_risk(info_high)
        assert (
            ofr_high.summary
            == "\u30aa\u30d5\u30a1\u30ea\u30f3\u30b0\u30ea\u30b9\u30af\u304c\u9ad8\u3044\u3067\u3059\u3002\u516c\u52df\u5897\u8cc7\u306b\u3088\u308b\u5e0c\u8584\u5316\u306b\u8b66\u6212\u304c\u5fc5\u8981\u3067\u3059\u3002"
        )


# ------------------------------------------------------------------
# Unit-55: None value -> medium with description
# ------------------------------------------------------------------
class TestUnit55NoneValueMedium:
    def test_risk_metric_none_value_returns_medium(self) -> None:
        info = make_info(debtToEquity=None)
        fh, _ = analyze_risk(info)
        assert fh.de_ratio.level == "\u4e2d"
        assert "\u30c7\u30fc\u30bf\u53d6\u5f97\u4e0d\u53ef" in fh.de_ratio.description


# ------------------------------------------------------------------
# Unit-56: D/E boundary 1.0
# ------------------------------------------------------------------
class TestUnit56DeRatioBoundary1:
    def test_de_ratio_boundary_1_0(self) -> None:
        info = make_info(debtToEquity=100.0)  # 1.0x
        fh, _ = analyze_risk(info)
        assert fh.de_ratio.level == "\u4e2d"


# ------------------------------------------------------------------
# Unit-57: D/E boundary 2.0
# ------------------------------------------------------------------
class TestUnit57DeRatioBoundary2:
    def test_de_ratio_boundary_2_0(self) -> None:
        info = make_info(debtToEquity=200.0)  # 2.0x
        fh, _ = analyze_risk(info)
        assert fh.de_ratio.level == "\u4e2d"


# ------------------------------------------------------------------
# Unit-58: Current ratio boundary 1.0
# ------------------------------------------------------------------
class TestUnit58CurrentRatioBoundary1:
    def test_current_ratio_boundary_1_0(self) -> None:
        info = make_info(currentRatio=1.0)
        fh, _ = analyze_risk(info)
        assert fh.current_ratio.level == "\u4e2d"


# ------------------------------------------------------------------
# Unit-59: Debt/cash ratio zero cash
# ------------------------------------------------------------------
class TestUnit59DebtCashRatioZeroCash:
    def test_debt_cash_ratio_zero_cash(self) -> None:
        info = make_info(totalCash=0)
        _, ofr = analyze_risk(info)
        assert ofr.debt_cash_ratio.level == "\u9ad8"


# ------------------------------------------------------------------
# Unit-60: Profit margin zero
# ------------------------------------------------------------------
class TestUnit60ProfitMarginZero:
    def test_profit_margin_zero(self) -> None:
        info = make_info(profitMargins=0.0)
        fh, _ = analyze_risk(info)
        assert fh.profit_margin.level == "\u4e2d"
