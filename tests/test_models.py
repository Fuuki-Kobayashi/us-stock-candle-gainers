"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError


# ============================================================
# CandleData
# ============================================================
class TestCandleData:
    def test_create_with_valid_data(self) -> None:
        from app.models.candle import CandleData

        candle = CandleData(
            date="2024-01-15",
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=1000000,
        )
        assert candle.date == "2024-01-15"
        assert candle.open == 150.0
        assert candle.high == 155.0
        assert candle.low == 148.0
        assert candle.close == 153.0
        assert candle.volume == 1000000

    def test_serialization_round_trip(self) -> None:
        from app.models.candle import CandleData

        candle = CandleData(
            date="2024-01-15",
            open=150.0,
            high=155.0,
            low=148.0,
            close=153.0,
            volume=500,
        )
        data = candle.model_dump()
        restored = CandleData(**data)
        assert restored == candle


# ============================================================
# PatternResult
# ============================================================
class TestPatternResult:
    def test_confirmed_pattern(self) -> None:
        from app.models.candle import PatternResult

        pattern = PatternResult(
            type="confirmed",
            name="モーニングスター",
            signal="🔼 強気シグナル",
            description="上昇転換の可能性があります。",
            direction="bullish",
            pattern_candle_count=3,
        )
        assert pattern.type == "confirmed"
        assert pattern.required_third is None
        assert pattern.direction == "bullish"
        assert pattern.pattern_candle_count == 3

    def test_predicted_pattern_with_required_third(self) -> None:
        from app.models.candle import PatternResult

        pattern = PatternResult(
            type="predicted",
            name="モーニングスター予測",
            signal="🔼 強気シグナル（予測）",
            description="条件付きパターンです。",
            required_third="3日目に大きな陽線が出現し、1日目の中間点を超えて引ける",
            direction="bullish",
            pattern_candle_count=3,
        )
        assert pattern.required_third is not None
        assert pattern.direction == "bullish"
        assert pattern.pattern_candle_count == 3

    def test_pattern_result_with_direction_bullish(self) -> None:
        from app.models.candle import PatternResult

        pattern = PatternResult(
            type="confirmed",
            name="テスト",
            signal="🔼 強気シグナル",
            description="テスト",
            direction="bullish",
            pattern_candle_count=1,
        )
        assert pattern.direction == "bullish"

    def test_pattern_result_with_direction_bearish(self) -> None:
        from app.models.candle import PatternResult

        pattern = PatternResult(
            type="confirmed",
            name="テスト",
            signal="🔽 弱気シグナル",
            description="テスト",
            direction="bearish",
            pattern_candle_count=1,
        )
        assert pattern.direction == "bearish"

    def test_pattern_result_with_pattern_candle_count(self) -> None:
        from app.models.candle import PatternResult

        for count in (1, 2, 3):
            pattern = PatternResult(
                type="confirmed",
                name="テスト",
                signal="🔼 強気シグナル",
                description="テスト",
                direction="bullish",
                pattern_candle_count=count,
            )
            assert pattern.pattern_candle_count == count

    def test_pattern_result_direction_required(self) -> None:
        from app.models.candle import PatternResult

        with pytest.raises(ValidationError):
            PatternResult(
                type="confirmed",
                name="テスト",
                signal="🔼 強気シグナル",
                description="テスト",
                pattern_candle_count=1,
            )

    def test_pattern_result_pattern_candle_count_required(self) -> None:
        from app.models.candle import PatternResult

        with pytest.raises(ValidationError):
            PatternResult(
                type="confirmed",
                name="テスト",
                signal="🔼 強気シグナル",
                description="テスト",
                direction="bullish",
            )

    def test_pattern_result_invalid_direction(self) -> None:
        from app.models.candle import PatternResult

        with pytest.raises(ValidationError):
            PatternResult(
                type="confirmed",
                name="テスト",
                signal="🔼 強気シグナル",
                description="テスト",
                direction="neutral",
                pattern_candle_count=1,
            )

    def test_pattern_result_invalid_candle_count(self) -> None:
        from app.models.candle import PatternResult

        with pytest.raises(ValidationError):
            PatternResult(
                type="confirmed",
                name="テスト",
                signal="🔼 強気シグナル",
                description="テスト",
                direction="bullish",
                pattern_candle_count=4,
            )


# ============================================================
# ShortInterest
# ============================================================
class TestShortInterest:
    def test_all_none_defaults(self) -> None:
        from app.models.candle import ShortInterest

        si = ShortInterest()
        assert si.short_percent_of_float is None
        assert si.short_ratio is None
        assert si.shares_short is None
        assert si.shares_short_prior_month is None

    def test_with_values(self) -> None:
        from app.models.candle import ShortInterest

        si = ShortInterest(
            short_percent_of_float=15.2,
            short_ratio=3.5,
            shares_short=10000000,
            shares_short_prior_month=9500000,
        )
        assert si.short_percent_of_float == 15.2
        assert si.shares_short == 10000000


# ============================================================
# RiskMetric
# ============================================================
class TestRiskMetric:
    def test_create_with_value(self) -> None:
        from app.models.risk import RiskMetric

        metric = RiskMetric(
            name="D/Eレシオ",
            value=1.5,
            level="中",
            description="負債比率はやや高めです。",
        )
        assert metric.name == "D/Eレシオ"
        assert metric.value == 1.5
        assert metric.level == "中"

    def test_create_with_none_value(self) -> None:
        from app.models.risk import RiskMetric

        metric = RiskMetric(
            name="D/Eレシオ",
            value=None,
            level="中",
            description="データ取得不可",
        )
        assert metric.value is None


# ============================================================
# FinancialHealth
# ============================================================
class TestFinancialHealth:
    def _make_metric(self, name: str = "test", level: str = "低"):
        from app.models.risk import RiskMetric

        return RiskMetric(name=name, value=1.0, level=level, description="desc")

    def test_create_financial_health(self) -> None:
        from app.models.risk import FinancialHealth

        fh = FinancialHealth(
            de_ratio=self._make_metric("D/Eレシオ"),
            current_ratio=self._make_metric("流動比率"),
            profit_margin=self._make_metric("利益率"),
            fcf=self._make_metric("フリーキャッシュフロー"),
            overall_level="低",
            summary="財務状態は健全です。主要指標に懸念はありません。",
        )
        assert fh.overall_level == "低"
        assert fh.de_ratio.name == "D/Eレシオ"


# ============================================================
# OfferingRisk
# ============================================================
class TestOfferingRisk:
    def _make_metric(self, name: str = "test", level: str = "低"):
        from app.models.risk import RiskMetric

        return RiskMetric(name=name, value=1.0, level=level, description="desc")

    def test_create_offering_risk(self) -> None:
        from app.models.risk import OfferingRisk

        risk = OfferingRisk(
            cash_runway=self._make_metric("キャッシュランウェイ"),
            dilution=self._make_metric("株式希薄化リスク"),
            net_income=self._make_metric("純利益"),
            debt_cash_ratio=self._make_metric("負債/現金比率"),
            overall_level="高",
            summary="オファリングリスクが高いです。",
        )
        assert risk.overall_level == "高"
        assert risk.cash_runway.name == "キャッシュランウェイ"


# ============================================================
# AnalyzeRequest
# ============================================================
class TestAnalyzeRequest:
    def test_ticker_uppercased(self) -> None:
        from app.models.request import AnalyzeRequest

        req = AnalyzeRequest(ticker="aapl")
        assert req.ticker == "AAPL"

    def test_ticker_stripped(self) -> None:
        from app.models.request import AnalyzeRequest

        req = AnalyzeRequest(ticker="  tsla  ")
        assert req.ticker == "TSLA"

    def test_empty_ticker_rejected(self) -> None:
        from app.models.request import AnalyzeRequest

        with pytest.raises(ValidationError):
            AnalyzeRequest(ticker="")

    def test_realdata_mode_defaults(self) -> None:
        from app.models.request import AnalyzeRequest

        req = AnalyzeRequest(ticker="AAPL")
        assert req.change1 is None
        assert req.change2 is None
        assert req.change3 is None

    def test_simulation_predicted_mode(self) -> None:
        from app.models.request import AnalyzeRequest

        req = AnalyzeRequest(ticker="GME", change1=5.0, change2=-3.0)
        assert req.change1 == 5.0
        assert req.change2 == -3.0
        assert req.change3 is None

    def test_simulation_confirmed_mode(self) -> None:
        from app.models.request import AnalyzeRequest

        req = AnalyzeRequest(ticker="GME", change1=5.0, change2=-3.0, change3=2.0)
        assert req.change3 == 2.0


# ============================================================
# RiskRequest
# ============================================================
class TestRiskRequest:
    def test_ticker_uppercased(self) -> None:
        from app.models.request import RiskRequest

        req = RiskRequest(ticker="msft")
        assert req.ticker == "MSFT"

    def test_ticker_stripped(self) -> None:
        from app.models.request import RiskRequest

        req = RiskRequest(ticker="  gme  ")
        assert req.ticker == "GME"

    def test_empty_ticker_rejected(self) -> None:
        from app.models.request import RiskRequest

        with pytest.raises(ValidationError):
            RiskRequest(ticker="")


# ============================================================
# AnalyzeResponse
# ============================================================
class TestAnalyzeResponse:
    def test_create_realdata_response(self) -> None:
        from app.models.candle import CandleData, ShortInterest
        from app.models.response import AnalyzeResponse

        resp = AnalyzeResponse(
            ticker="AAPL",
            mode="realdata",
            atr=2.45,
            candles=[
                CandleData(
                    date="2024-01-15",
                    open=150.0,
                    high=155.0,
                    low=148.0,
                    close=153.0,
                    volume=1000000,
                ),
            ],
            patterns=[],
            short_interest=ShortInterest(short_percent_of_float=15.0),
        )
        assert resp.mode == "realdata"
        assert resp.atr == 2.45
        assert resp.short_interest is not None

    def test_create_simulation_response(self) -> None:
        from app.models.response import AnalyzeResponse

        resp = AnalyzeResponse(
            ticker="GME",
            mode="simulation_predicted",
            base_price=25.0,
            candles=[],
            patterns=[],
        )
        assert resp.base_price == 25.0
        assert resp.atr is None
        assert resp.short_interest is None


# ============================================================
# RiskResponse
# ============================================================
class TestRiskResponse:
    def _make_metric(self, name: str = "test", level: str = "低"):
        from app.models.risk import RiskMetric

        return RiskMetric(name=name, value=1.0, level=level, description="desc")

    def test_create_risk_response(self) -> None:
        from app.models.response import RiskResponse
        from app.models.risk import FinancialHealth, OfferingRisk

        resp = RiskResponse(
            ticker="AAPL",
            financial_health=FinancialHealth(
                de_ratio=self._make_metric(),
                current_ratio=self._make_metric(),
                profit_margin=self._make_metric(),
                fcf=self._make_metric(),
                overall_level="低",
                summary="健全",
            ),
            offering_risk=OfferingRisk(
                cash_runway=self._make_metric(),
                dilution=self._make_metric(),
                net_income=self._make_metric(),
                debt_cash_ratio=self._make_metric(),
                overall_level="低",
                summary="低リスク",
            ),
        )
        assert resp.ticker == "AAPL"


# ============================================================
# ErrorResponse
# ============================================================
class TestErrorResponse:
    def test_create_error_response(self) -> None:
        from app.models.response import ErrorResponse

        err = ErrorResponse(detail="エラーが発生しました。")
        assert err.detail == "エラーが発生しました。"


# ============================================================
# __init__.py re-exports
# ============================================================
class TestModelsInit:
    def test_all_models_importable_from_init(self) -> None:
        from app.models import (
            AnalyzeRequest,
            AnalyzeResponse,
            CandleData,
            ErrorResponse,
            FinancialHealth,
            OfferingRisk,
            PatternResult,
            RiskMetric,
            RiskRequest,
            RiskResponse,
            ShortInterest,
        )

        # Verify they are the correct classes
        assert CandleData.__name__ == "CandleData"
        assert PatternResult.__name__ == "PatternResult"
        assert ShortInterest.__name__ == "ShortInterest"
        assert RiskMetric.__name__ == "RiskMetric"
        assert FinancialHealth.__name__ == "FinancialHealth"
        assert OfferingRisk.__name__ == "OfferingRisk"
        assert AnalyzeRequest.__name__ == "AnalyzeRequest"
        assert RiskRequest.__name__ == "RiskRequest"
        assert AnalyzeResponse.__name__ == "AnalyzeResponse"
        assert RiskResponse.__name__ == "RiskResponse"
        assert ErrorResponse.__name__ == "ErrorResponse"
