from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Request model for candlestick pattern analysis."""

    ticker: str = Field(min_length=1)
    change1: float | None = None
    change2: float | None = None
    change3: float | None = None

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()


class RiskRequest(BaseModel):
    """Request model for risk analysis."""

    ticker: str = Field(min_length=1)

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()
