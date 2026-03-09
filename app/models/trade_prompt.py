"""Request/Response models for trade prompt generation."""

from pydantic import BaseModel, Field, field_validator


class TradePromptRequest(BaseModel):
    """Request model for trade prompt generation."""

    ticker: str = Field(min_length=1)

    @field_validator("ticker")
    @classmethod
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper().strip()


class TradePromptResponse(BaseModel):
    """Response model for trade prompt generation."""

    ticker: str
    prompt: str
