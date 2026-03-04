"""Simulation service for generating simulated candlestick data."""

from app.models.candle import CandleData

HIGH_MARGIN = 1.005
LOW_MARGIN = 0.995
DATE_LABEL_TEMPLATE = "{day}日目 (シミュレーション)"


def generate_simulated_candles(
    base_price: float, changes: list[float]
) -> list[CandleData]:
    """Generate 2 or 3 simulated candles from base price and % changes.

    Args:
        base_price: The starting price for the first candle's open.
        changes: List of percentage changes for each day.

    Returns:
        List of CandleData representing simulated trading days.
    """
    candles: list[CandleData] = []
    current_open = base_price

    for i, change in enumerate(changes):
        close = current_open * (1 + change / 100)
        high = max(current_open, close) * HIGH_MARGIN
        low = min(current_open, close) * LOW_MARGIN
        date_label = DATE_LABEL_TEMPLATE.format(day=i + 1)

        candle = CandleData(
            date=date_label,
            open=current_open,
            high=high,
            low=low,
            close=close,
            volume=0,
        )
        candles.append(candle)
        current_open = close

    return candles
