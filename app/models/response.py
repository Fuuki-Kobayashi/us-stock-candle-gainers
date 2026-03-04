from pydantic import BaseModel

from app.models.candle import CandleData, PatternResult, ShortInterest
from app.models.risk import FinancialHealth, OfferingRisk


class AnalyzeResponse(BaseModel):
    """Response model for candlestick pattern analysis."""

    ticker: str
    mode: str
    atr: float | None = None
    base_price: float | None = None
    candles: list[CandleData]
    patterns: list[PatternResult]
    short_interest: ShortInterest | None = None


class RiskResponse(BaseModel):
    """Response model for risk analysis."""

    ticker: str
    financial_health: FinancialHealth
    offering_risk: OfferingRisk


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
