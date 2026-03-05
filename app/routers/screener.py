"""Screener router for bulk ticker scanning."""

from fastapi import APIRouter

from app.models.screener import ScreenerRequest, ScreenerResponse
from app.services.screener_service import scan_tickers

router = APIRouter()


@router.post("/screener", response_model=ScreenerResponse)
def screener(request: ScreenerRequest) -> ScreenerResponse:
    """Scan multiple tickers for candlestick patterns."""
    results = scan_tickers(request.tickers, candle_count=request.candle_count)
    scanned = sum(1 for r in results if r.error is None)
    errors = sum(1 for r in results if r.error is not None)
    return ScreenerResponse(
        results=results,
        total=len(results),
        scanned=scanned,
        errors=errors,
    )
