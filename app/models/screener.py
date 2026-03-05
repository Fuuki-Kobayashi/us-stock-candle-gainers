"""Screener request/response models."""

from typing import Literal

from pydantic import BaseModel, field_validator

from app.models.candle import CandleData, PatternResult


class ScreenerRequest(BaseModel):
    """Request model for the screener endpoint."""

    tickers: list[str]
    candle_count: Literal[2, 3] = 3

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: list[str]) -> list[str]:
        if len(v) == 0:
            raise ValueError("tickers must not be empty")
        if len(v) > 50:
            raise ValueError("tickers must have at most 50 items")
        return v


class TickerScanResult(BaseModel):
    """Scan result for a single ticker."""

    ticker: str
    candles: list[CandleData] = []
    patterns: list[PatternResult] = []
    change_pct: float | None = None
    error: str | None = None


class ScreenerResponse(BaseModel):
    """Response model for the screener endpoint."""

    results: list[TickerScanResult]
    total: int
    scanned: int
    errors: int
