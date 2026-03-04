"""Risk router for financial risk analysis."""

from fastapi import APIRouter

from app.models.request import RiskRequest
from app.models.response import RiskResponse
from app.services import risk_analyzer, stock_data

router = APIRouter()


@router.post("/risk", response_model=RiskResponse)
def risk(request: RiskRequest) -> RiskResponse:
    """Analyze financial risk for a given ticker."""
    info = stock_data.get_financial_info(request.ticker)
    financial_health, offering_risk = risk_analyzer.analyze_risk(info)
    return RiskResponse(
        ticker=request.ticker,
        financial_health=financial_health,
        offering_risk=offering_risk,
    )
