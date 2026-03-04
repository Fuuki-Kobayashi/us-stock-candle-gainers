from pydantic import BaseModel


class RiskMetric(BaseModel):
    """Single risk metric with level assessment."""

    name: str  # Japanese metric name
    value: float | None = None
    level: str  # "低", "中", or "高"
    description: str  # Japanese explanation


class FinancialHealth(BaseModel):
    """Financial health assessment with 4 metrics."""

    de_ratio: RiskMetric
    current_ratio: RiskMetric
    profit_margin: RiskMetric
    fcf: RiskMetric
    overall_level: str  # "低", "中", or "高"
    summary: str  # Japanese summary


class OfferingRisk(BaseModel):
    """Offering risk assessment with 4 metrics."""

    cash_runway: RiskMetric
    dilution: RiskMetric
    net_income: RiskMetric
    debt_cash_ratio: RiskMetric
    overall_level: str  # "低", "中", or "高"
    summary: str  # Japanese summary
