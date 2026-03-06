"""Pattern search request/response models."""

from typing import Literal

from pydantic import BaseModel, field_validator

from app.models.candle import PatternResult  # noqa: F401 - used in PatternSearchResult


class PatternEntry(BaseModel):
    """Single pattern in the registry."""

    id: str
    name: str
    direction: Literal["bullish", "bearish"]
    available_types: list[str]  # ["confirmed"] or ["confirmed", "predicted"]
    pattern_candle_count: Literal[1, 2, 3]


class PatternListResponse(BaseModel):
    """Response for GET /api/patterns."""

    patterns: list[PatternEntry]
    total: int


class PatternSearchRequest(BaseModel):
    """Request for POST /api/pattern-search."""

    tickers: list[str]
    pattern_ids: list[str]
    candle_count: Literal[2, 3] = 3

    @field_validator("tickers")
    @classmethod
    def validate_tickers(cls, v: list[str]) -> list[str]:
        if len(v) == 0:
            raise ValueError("tickers must not be empty")
        if len(v) > 50:
            raise ValueError("tickers must not exceed 50")
        return [t.strip().upper() for t in v]

    @field_validator("pattern_ids")
    @classmethod
    def validate_pattern_ids(cls, v: list[str]) -> list[str]:
        if len(v) == 0:
            raise ValueError("pattern_ids must not be empty")
        return v


class PatternSearchResult(BaseModel):
    """Single ticker result in pattern search."""

    ticker: str
    change_pct: float | None = None
    patterns: list[PatternResult]
    error: str | None = None


class PatternSearchResponse(BaseModel):
    """Response for POST /api/pattern-search."""

    results: list[PatternSearchResult]
    total: int
    matched: int
    errors: int
