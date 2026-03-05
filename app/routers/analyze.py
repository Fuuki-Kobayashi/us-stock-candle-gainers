"""Analyze router for candlestick pattern analysis."""

from fastapi import APIRouter

from app.models.request import AnalyzeRequest
from app.models.response import AnalyzeResponse
from app.services import pattern_detector, simulation, stock_data

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze candlestick patterns.

    Mode determination:
    - change1 + change2 + change3 all provided -> simulation_confirmed
    - change1 + change2 provided -> simulation_predicted
    - otherwise (no changes or only change1) -> realdata
    """
    if (
        request.change1 is not None
        and request.change2 is not None
        and request.change3 is not None
    ):
        mode = "simulation_confirmed"
    elif request.change1 is not None and request.change2 is not None:
        mode = "simulation_predicted"
    else:
        mode = "realdata"

    # Validate ticker for all modes
    stock_data.validate_ticker(request.ticker)

    if mode == "realdata":
        count = request.candle_count or 3
        candles, atr = stock_data.get_ohlcv(request.ticker, candle_count=count)
        short_interest = stock_data.get_short_interest(request.ticker)
        detect_mode = "realdata_2candle" if count == 2 else "realdata"
        patterns = pattern_detector.detect_patterns(candles, mode=detect_mode)
        return AnalyzeResponse(
            ticker=request.ticker,
            mode=detect_mode,
            atr=atr,
            candles=candles,
            patterns=patterns,
            short_interest=short_interest,
        )

    if mode == "simulation_predicted":
        base_price = stock_data.get_latest_close(request.ticker)
        changes = [request.change1, request.change2]
        candles = simulation.generate_simulated_candles(base_price, changes)
        patterns = pattern_detector.detect_patterns(
            candles, mode="simulation_predicted"
        )
        return AnalyzeResponse(
            ticker=request.ticker,
            mode="simulation_predicted",
            base_price=base_price,
            candles=candles,
            patterns=patterns,
        )

    # simulation_confirmed
    base_price = stock_data.get_latest_close(request.ticker)
    changes = [request.change1, request.change2, request.change3]
    candles = simulation.generate_simulated_candles(base_price, changes)
    patterns = pattern_detector.detect_patterns(candles, mode="simulation_confirmed")
    return AnalyzeResponse(
        ticker=request.ticker,
        mode="simulation_confirmed",
        base_price=base_price,
        candles=candles,
        patterns=patterns,
    )
