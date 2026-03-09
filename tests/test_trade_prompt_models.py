"""Tests for TradePromptRequest and TradePromptResponse models."""

import pytest
from pydantic import ValidationError


class TestTradePromptRequest:
    def test_ticker_uppercased(self) -> None:
        from app.models.trade_prompt import TradePromptRequest

        req = TradePromptRequest(ticker="aapl")
        assert req.ticker == "AAPL"

    def test_ticker_stripped(self) -> None:
        from app.models.trade_prompt import TradePromptRequest

        req = TradePromptRequest(ticker="  tsla  ")
        assert req.ticker == "TSLA"

    def test_empty_ticker_rejected(self) -> None:
        from app.models.trade_prompt import TradePromptRequest

        with pytest.raises(ValidationError):
            TradePromptRequest(ticker="")

    def test_valid_ticker(self) -> None:
        from app.models.trade_prompt import TradePromptRequest

        req = TradePromptRequest(ticker="GME")
        assert req.ticker == "GME"


class TestTradePromptResponse:
    def test_create_response(self) -> None:
        from app.models.trade_prompt import TradePromptResponse

        resp = TradePromptResponse(ticker="AAPL", prompt="Buy signal detected")
        assert resp.ticker == "AAPL"
        assert resp.prompt == "Buy signal detected"

    def test_serialization_round_trip(self) -> None:
        from app.models.trade_prompt import TradePromptResponse

        resp = TradePromptResponse(ticker="TSLA", prompt="Some prompt text")
        data = resp.model_dump()
        restored = TradePromptResponse(**data)
        assert restored == resp
