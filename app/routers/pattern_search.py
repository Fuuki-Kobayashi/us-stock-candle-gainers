"""Pattern search router for reverse-lookup by pattern."""

from fastapi import APIRouter, HTTPException

from app.models.pattern_search import (
    PatternListResponse,
    PatternSearchRequest,
    PatternSearchResponse,
)
from app.services.pattern_registry import get_all_patterns, validate_pattern_ids
from app.services.pattern_search_service import search_patterns

router = APIRouter()


@router.get("/api/patterns", response_model=PatternListResponse)
def list_patterns() -> PatternListResponse:
    """Return all available patterns."""
    patterns = get_all_patterns()
    return PatternListResponse(patterns=patterns, total=len(patterns))


@router.post("/api/pattern-search", response_model=PatternSearchResponse)
def pattern_search(request: PatternSearchRequest) -> PatternSearchResponse:
    """Search for patterns across tickers."""
    # Business validation: check pattern_ids against registry (400, not 422)
    try:
        validate_pattern_ids(request.pattern_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    results = search_patterns(
        tickers=request.tickers,
        pattern_ids=request.pattern_ids,
        candle_count=request.candle_count,
    )

    matched = sum(1 for r in results if r.error is None)
    errors = sum(1 for r in results if r.error is not None)

    return PatternSearchResponse(
        results=results,
        total=len(request.tickers),
        matched=matched,
        errors=errors,
    )
