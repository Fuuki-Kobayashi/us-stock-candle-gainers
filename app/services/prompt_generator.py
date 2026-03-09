"""Prompt generator service for AI trade plan generation.

Orchestrates data fetching and formats a comprehensive stock analysis prompt.
"""

from __future__ import annotations

import asyncio

from app.models.candle import CandleData, PatternResult, ShortInterest
from app.models.risk import FinancialHealth, OfferingRisk
from app.services.pattern_detector import detect_patterns
from app.services.risk_analyzer import analyze_risk
from app.services.stock_data import (
    get_news,
    get_ohlcv,
    get_short_interest_from_info,
    validate_ticker,
)

# Keys to extract from yfinance info dict
_PROFILE_KEYS = [
    "shortName",
    "sector",
    "industry",
    "country",
    "marketCap",
    "sharesOutstanding",
    "totalRevenue",
    "totalCash",
    "totalDebt",
    "bookValue",
    "priceToBook",
    "trailingPE",
    "forwardPE",
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "fiftyDayAverage",
    "twoHundredDayAverage",
    "beta",
    "earningsGrowth",
    "revenueGrowth",
]

# Japanese to English level translation map
_LEVEL_MAP = {
    "低": "Low",
    "中": "Medium",
    "高": "High",
}

# Japanese words to translate in summaries
_SUMMARY_TRANSLATIONS = {
    "低": "Low",
    "中": "Medium",
    "高": "High",
}


def _translate_level(level: str) -> str:
    """Translate Japanese risk level to English."""
    return _LEVEL_MAP.get(level, level)


def _translate_summary(text: str) -> str:
    """Translate Japanese level words in summary text to English."""
    result = text
    for jp, en in _SUMMARY_TRANSLATIONS.items():
        result = result.replace(jp, en)
    return result


def _extract_company_profile(info: dict) -> dict:
    """Extract company profile keys from yfinance info dict.

    Missing keys default to "N/A".
    """
    return {key: info.get(key, "N/A") for key in _PROFILE_KEYS}


def _format_company_section(profile: dict) -> str:
    """Format company profile as markdown section."""
    return (
        "## Company Profile\n"
        f"- Name: {profile['shortName']}\n"
        f"- Sector / Industry: {profile['sector']} / {profile['industry']}\n"
        f"- Country: {profile['country']}\n"
        f"- Market Cap: {profile['marketCap']}\n"
        f"- Shares Outstanding: {profile['sharesOutstanding']}\n"
        f"- Revenue: {profile['totalRevenue']} | Cash: {profile['totalCash']} | Debt: {profile['totalDebt']}\n"
        f"- Book Value: {profile['bookValue']} | P/B: {profile['priceToBook']} | "
        f"Trailing P/E: {profile['trailingPE']} | Forward P/E: {profile['forwardPE']}\n"
        f"- 52W High: {profile['fiftyTwoWeekHigh']} | 52W Low: {profile['fiftyTwoWeekLow']}\n"
        f"- 50-day MA: {profile['fiftyDayAverage']} | 200-day MA: {profile['twoHundredDayAverage']}\n"
        f"- Beta: {profile['beta']} | Earnings Growth: {profile['earningsGrowth']} | "
        f"Revenue Growth: {profile['revenueGrowth']}"
    )


def _format_technical_section(
    candles: list[CandleData],
    atr: float | None,
    patterns: list[PatternResult],
) -> str:
    """Format technical data as markdown section with OHLCV table, ATR, and patterns."""
    lines = ["## Technical Data", ""]

    # OHLCV table
    lines.append("### OHLCV (Recent Candles)")
    lines.append("| Date | Open | High | Low | Close | Volume |")
    lines.append("|------|------|------|-----|-------|--------|")
    for c in candles:
        lines.append(
            f"| {c.date} | {c.open} | {c.high} | {c.low} | {c.close} | {c.volume} |"
        )
    lines.append("")

    # ATR
    atr_str = f"{atr}" if atr is not None else "N/A"
    lines.append(f"### ATR(14): {atr_str}")
    lines.append("")

    # Patterns
    lines.append("### Candlestick Patterns")
    if not patterns:
        lines.append("No candlestick patterns detected")
    else:
        for p in patterns:
            lines.append(f"- **{p.name}** ({p.type}): {p.signal} - {p.description}")

    return "\n".join(lines)


def _format_risk_section(
    financial_health: FinancialHealth,
    offering_risk: OfferingRisk,
) -> str:
    """Format risk analysis as markdown section with translated levels."""
    lines = ["## Risk Analysis", ""]

    # Financial Health
    lines.append("### Financial Health")
    lines.append(f"- Overall: **{_translate_level(financial_health.overall_level)}**")
    lines.append(f"- Summary: {_translate_summary(financial_health.summary)}")
    for metric in [
        financial_health.de_ratio,
        financial_health.current_ratio,
        financial_health.profit_margin,
        financial_health.fcf,
    ]:
        lines.append(
            f"  - {metric.name}: {metric.value} "
            f"[{_translate_level(metric.level)}] - {_translate_summary(metric.description)}"
        )
    lines.append("")

    # Offering Risk
    lines.append("### Offering Risk")
    lines.append(f"- Overall: **{_translate_level(offering_risk.overall_level)}**")
    lines.append(f"- Summary: {_translate_summary(offering_risk.summary)}")
    for metric in [
        offering_risk.cash_runway,
        offering_risk.dilution,
        offering_risk.net_income,
        offering_risk.debt_cash_ratio,
    ]:
        lines.append(
            f"  - {metric.name}: {metric.value} "
            f"[{_translate_level(metric.level)}] - {_translate_summary(metric.description)}"
        )

    return "\n".join(lines)


def _format_short_interest_section(si: ShortInterest | None) -> str:
    """Format short interest as markdown section."""
    lines = ["## Short Interest"]
    if si is None:
        lines.append("Data not available")
    else:
        lines.append(f"- Short % of Float: {si.short_percent_of_float}")
        lines.append(f"- Short Ratio (Days to Cover): {si.short_ratio}")
        lines.append(f"- Shares Short: {si.shares_short}")
        lines.append(f"- Shares Short Prior Month: {si.shares_short_prior_month}")
    return "\n".join(lines)


def _format_news_section(news: list[dict]) -> str:
    """Format news as markdown section."""
    lines = ["## Recent News"]
    if not news:
        lines.append("No recent news found")
    else:
        for item in news:
            title = item.get("title", "")
            source = item.get("source", "")
            pub_date = item.get("pub_date", "")
            summary = item.get("summary", "")
            url = item.get("url", "")
            lines.append(f"- **{title}** ({source}, {pub_date})")
            if summary:
                lines.append(f"  {summary}")
            if url:
                lines.append(f"  URL: {url}")
    return "\n".join(lines)


def _format_instructions() -> str:
    """Return static instruction template for AI trade plan generation."""
    return (
        "# Trade Plan Instructions\n"
        "\n"
        "Based on the above data, provide a comprehensive trade plan with the following:\n"
        "\n"
        "1. **Direction**: LONG or SHORT (with confidence level: High/Medium/Low)\n"
        "2. **Entry Price**: Recommended entry price\n"
        "3. **Take Profit Targets**:\n"
        "   - TP1: Conservative target\n"
        "   - TP2: Moderate target\n"
        "   - TP3: Aggressive target\n"
        "4. **Stop Loss**: Recommended stop loss level\n"
        "5. **Catalyst Assessment**: Key catalysts that support the trade\n"
        "6. **Theme Strength**: How strong is the current market theme/narrative\n"
        "7. **Trade Rationale Summary**: Concise summary of why this trade makes sense"
    )


def _assemble_prompt(
    ticker: str,
    company: str,
    technical: str,
    risk: str,
    short_interest: str,
    news: str,
    instructions: str,
) -> str:
    """Assemble all sections into the final prompt."""
    return (
        f"# Stock Analysis Data: {ticker}\n"
        f"\n"
        f"{company}\n"
        f"\n"
        f"{technical}\n"
        f"\n"
        f"{risk}\n"
        f"\n"
        f"{short_interest}\n"
        f"\n"
        f"{news}\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{instructions}"
    )


async def generate_trade_prompt(ticker: str) -> str:
    """Generate a comprehensive trade analysis prompt for a given ticker.

    Orchestrates data fetching (with parallelism) and formats all sections.
    """
    # Step 1: Validate ticker (must run first)
    info = await asyncio.to_thread(validate_ticker, ticker)

    # Step 2: Parallel fetch of OHLCV and news
    async def _safe_get_news() -> list[dict]:
        try:
            return await asyncio.to_thread(get_news, ticker)
        except Exception:
            return []

    (candles, atr), news = await asyncio.gather(
        asyncio.to_thread(get_ohlcv, ticker, 3),
        _safe_get_news(),
    )

    # Step 3: Synchronous processing
    profile = _extract_company_profile(info)
    si = get_short_interest_from_info(info)
    fh, or_ = analyze_risk(info)
    patterns = detect_patterns(candles, "realdata")

    # Step 4: Format and assemble
    company_section = _format_company_section(profile)
    technical_section = _format_technical_section(candles, atr, patterns)
    risk_section = _format_risk_section(fh, or_)
    short_interest_section = _format_short_interest_section(si)
    news_section = _format_news_section(news)
    instructions_section = _format_instructions()

    return _assemble_prompt(
        ticker,
        company_section,
        technical_section,
        risk_section,
        short_interest_section,
        news_section,
        instructions_section,
    )
