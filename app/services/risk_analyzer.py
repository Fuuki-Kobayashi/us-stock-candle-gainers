"""Risk analysis service for financial health and offering risk assessment."""

from app.models.risk import FinancialHealth, OfferingRisk, RiskMetric

# Summary text constants
_FH_SUMMARY = {
    "低": "財務状態は健全です。主要指標に懸念はありません。",
    "中": "財務状態に一部注意が必要な指標があります。",
    "高": "財務状態に重大な懸念があります。投資判断には十分な注意が必要です。",
}

_OR_SUMMARY = {
    "低": "オファリングリスクは低いです。希薄化の懸念は少ないです。",
    "中": "オファリングリスクに注意が必要です。一部の指標を監視してください。",
    "高": "オファリングリスクが高いです。公募増資による希薄化に警戒が必要です。",
}


def _compute_overall(levels: list[str]) -> str:
    """Determine overall risk level from a list of individual levels."""
    if "高" in levels:
        return "高"
    if "中" in levels:
        return "中"
    return "低"


def _assess_de_ratio(info: dict) -> RiskMetric:
    """Assess debt-to-equity ratio risk."""
    raw = info.get("debtToEquity")
    if raw is None:
        return RiskMetric(
            name="D/Eレシオ",
            value=None,
            level="中",
            description="データ取得不可",
        )
    ratio = raw / 100.0
    if ratio < 1.0:
        level = "低"
        desc = f"D/Eレシオ {ratio:.2f}x: 負債水準は低いです。"
    elif ratio <= 2.0:
        level = "中"
        desc = f"D/Eレシオ {ratio:.2f}x: 負債水準に注意が必要です。"
    else:
        level = "高"
        desc = f"D/Eレシオ {ratio:.2f}x: 負債水準が高いです。"
    return RiskMetric(name="D/Eレシオ", value=ratio, level=level, description=desc)


def _assess_current_ratio(info: dict) -> RiskMetric:
    """Assess current ratio risk (inverted: higher value = lower risk)."""
    raw = info.get("currentRatio")
    if raw is None:
        return RiskMetric(
            name="流動比率",
            value=None,
            level="中",
            description="データ取得不可",
        )
    if raw > 1.5:
        level = "低"
        desc = f"流動比率 {raw:.2f}: 短期支払能力は十分です。"
    elif raw >= 1.0:
        level = "中"
        desc = f"流動比率 {raw:.2f}: 短期支払能力に注意が必要です。"
    else:
        level = "高"
        desc = f"流動比率 {raw:.2f}: 短期支払能力に懸念があります。"
    return RiskMetric(name="流動比率", value=raw, level=level, description=desc)


def _assess_profit_margin(info: dict) -> RiskMetric:
    """Assess profit margin risk."""
    raw = info.get("profitMargins")
    if raw is None:
        return RiskMetric(
            name="利益率",
            value=None,
            level="中",
            description="データ取得不可",
        )
    if raw > 0.10:
        level = "低"
        desc = f"利益率 {raw:.1%}: 収益性は良好です。"
    elif raw >= 0.0:
        level = "中"
        desc = f"利益率 {raw:.1%}: 収益性に注意が必要です。"
    else:
        level = "高"
        desc = f"利益率 {raw:.1%}: 収益性に懸念があります。"
    return RiskMetric(name="利益率", value=raw, level=level, description=desc)


def _assess_fcf(info: dict) -> RiskMetric:
    """Assess free cash flow risk."""
    raw = info.get("freeCashflow")
    if raw is None:
        return RiskMetric(
            name="フリーキャッシュフロー",
            value=None,
            level="中",
            description="データ取得不可",
        )
    if raw > 0:
        level = "低"
        desc = f"FCF {raw:,.0f}: キャッシュフローは正です。"
    elif raw == 0:
        level = "中"
        desc = "FCF 0: キャッシュフローはゼロです。"
    else:
        level = "高"
        desc = f"FCF {raw:,.0f}: キャッシュフローがマイナスです。"
    return RiskMetric(
        name="フリーキャッシュフロー", value=float(raw), level=level, description=desc
    )


def _assess_cash_runway(info: dict) -> RiskMetric:
    """Assess cash runway risk."""
    net_income = info.get("netIncomeToCommon")
    total_cash = info.get("totalCash")

    if net_income is None or net_income >= 0:
        return RiskMetric(
            name="キャッシュランウェイ",
            value=None if net_income is None else float(net_income),
            level="低",
            description="黒字企業のためキャッシュランウェイリスクは低いです。",
        )

    # net_income is negative
    if total_cash is None or total_cash == 0:
        return RiskMetric(
            name="キャッシュランウェイ",
            value=0.0,
            level="高",
            description="現金残高がないため、キャッシュランウェイリスクが高いです。",
        )

    months = total_cash / abs(net_income) * 12
    if months > 24:
        level = "低"
        desc = f"キャッシュランウェイ {months:.1f}ヶ月: 十分な余裕があります。"
    elif months >= 12:
        level = "中"
        desc = f"キャッシュランウェイ {months:.1f}ヶ月: 注意が必要です。"
    else:
        level = "高"
        desc = f"キャッシュランウェイ {months:.1f}ヶ月: 資金繰りに懸念があります。"
    return RiskMetric(
        name="キャッシュランウェイ", value=months, level=level, description=desc
    )


def _assess_dilution(info: dict) -> RiskMetric:
    """Assess dilution risk."""
    net_income = info.get("netIncomeToCommon")
    fcf = info.get("freeCashflow")
    de_raw = info.get("debtToEquity")

    if net_income is None or fcf is None:
        return RiskMetric(
            name="株式希薄化リスク",
            value=None,
            level="中",
            description="データ取得不可",
        )

    is_profitable = net_income > 0
    is_positive_fcf = fcf > 0
    is_high_debt = (de_raw is not None) and (de_raw / 100.0 > 2.0)

    if is_profitable and is_positive_fcf:
        level = "低"
        desc = "黒字かつFCF正のため、希薄化リスクは低いです。"
        signal_value = 0.0
    elif (not is_profitable) and (not is_positive_fcf) and is_high_debt:
        level = "高"
        desc = "赤字・FCFマイナス・高負債のため、希薄化リスクが高いです。"
        signal_value = 3.0
    else:
        level = "中"
        desc = "一部の指標にネガティブシグナルがあります。"
        signal_value = 1.0

    return RiskMetric(
        name="株式希薄化リスク",
        value=signal_value,
        level=level,
        description=desc,
    )


def _assess_net_income(info: dict) -> RiskMetric:
    """Assess net income risk."""
    raw = info.get("netIncomeToCommon")
    if raw is None:
        return RiskMetric(
            name="純利益",
            value=None,
            level="中",
            description="データ取得不可",
        )
    if raw > 0:
        level = "低"
        desc = f"純利益 {raw:,.0f}: 黒字です。"
    elif raw == 0:
        level = "中"
        desc = "純利益 0: 損益分岐点です。"
    else:
        level = "高"
        desc = f"純利益 {raw:,.0f}: 赤字です。"
    return RiskMetric(name="純利益", value=float(raw), level=level, description=desc)


def _assess_debt_cash_ratio(info: dict) -> RiskMetric:
    """Assess debt-to-cash ratio risk."""
    total_debt = info.get("totalDebt")
    total_cash = info.get("totalCash")

    if total_debt is None or total_cash is None:
        return RiskMetric(
            name="負債/現金比率",
            value=None,
            level="中",
            description="データ取得不可",
        )

    if total_cash == 0:
        return RiskMetric(
            name="負債/現金比率",
            value=None,
            level="高",
            description="現金残高がゼロのため、負債/現金比率が算出不可です。",
        )

    ratio = total_debt / total_cash
    if ratio < 1.0:
        level = "低"
        desc = f"負債/現金比率 {ratio:.2f}: 現金が負債を上回っています。"
    elif ratio <= 3.0:
        level = "中"
        desc = f"負債/現金比率 {ratio:.2f}: 負債と現金のバランスに注意が必要です。"
    else:
        level = "高"
        desc = f"負債/現金比率 {ratio:.2f}: 負債が現金を大幅に上回っています。"
    return RiskMetric(name="負債/現金比率", value=ratio, level=level, description=desc)


def analyze_risk(info: dict) -> tuple[FinancialHealth, OfferingRisk]:
    """Analyze financial health and offering risk from yfinance info dict."""
    # Financial health metrics
    de_ratio = _assess_de_ratio(info)
    current_ratio = _assess_current_ratio(info)
    profit_margin = _assess_profit_margin(info)
    fcf = _assess_fcf(info)

    fh_levels = [de_ratio.level, current_ratio.level, profit_margin.level, fcf.level]
    fh_overall = _compute_overall(fh_levels)

    financial_health = FinancialHealth(
        de_ratio=de_ratio,
        current_ratio=current_ratio,
        profit_margin=profit_margin,
        fcf=fcf,
        overall_level=fh_overall,
        summary=_FH_SUMMARY[fh_overall],
    )

    # Offering risk metrics
    cash_runway = _assess_cash_runway(info)
    dilution = _assess_dilution(info)
    net_income = _assess_net_income(info)
    debt_cash_ratio = _assess_debt_cash_ratio(info)

    or_levels = [
        cash_runway.level,
        dilution.level,
        net_income.level,
        debt_cash_ratio.level,
    ]
    or_overall = _compute_overall(or_levels)

    offering_risk = OfferingRisk(
        cash_runway=cash_runway,
        dilution=dilution,
        net_income=net_income,
        debt_cash_ratio=debt_cash_ratio,
        overall_level=or_overall,
        summary=_OR_SUMMARY[or_overall],
    )

    return financial_health, offering_risk
