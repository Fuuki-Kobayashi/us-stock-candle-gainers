from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request model for candlestick pattern analysis."""

    ticker: str = Field(min_length=1)
    change1: float | None = None
    change2: float | None = None
    change3: float | None = None
    candle_count: int | None = None

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator("candle_count")
    @classmethod
    def validate_candle_count(cls, v: int | None) -> int | None:
        if v is not None and v not in (2, 3):
            raise ValueError("candle_count must be 2 or 3")
        return v


class RiskRequest(BaseModel):
    """Request model for risk analysis."""

    ticker: str = Field(min_length=1)

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()
