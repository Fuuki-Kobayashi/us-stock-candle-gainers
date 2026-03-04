"""Custom exception classes for the candlestick pattern tool."""


class TickerNotFoundError(Exception):
    """Raised when ticker symbol cannot be found in yfinance."""


class TickerNotEquityError(Exception):
    """Raised when ticker exists but is not of type EQUITY."""

    def __init__(self, ticker: str, quote_type: str) -> None:
        self.ticker = ticker
        self.quote_type = quote_type
        super().__init__(f"'{ticker}' is not an equity (type: {quote_type})")


class DataFetchError(Exception):
    """Raised when yfinance API call fails due to network/timeout."""
