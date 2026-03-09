"""Trade prompt router for AI trade plan generation."""

from fastapi import APIRouter

from app.models.trade_prompt import TradePromptRequest, TradePromptResponse
from app.services import prompt_generator

router = APIRouter()


@router.post("/trade-prompt", response_model=TradePromptResponse)
async def trade_prompt(request: TradePromptRequest) -> TradePromptResponse:
    """Generate a trade analysis prompt for the given ticker."""
    prompt = await prompt_generator.generate_trade_prompt(request.ticker)
    return TradePromptResponse(ticker=request.ticker, prompt=prompt)
