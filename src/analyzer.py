"""Statistics and aggregations for categorized transactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.categorizer import categorize_transactions
from src.parser import read_transactions


@dataclass(frozen=True)
class AnalysisResult:
    """Complete analysis output for API and export."""

    total_spent: float
    total_income: float
    net_flow: float
    transaction_count: int
    avg_per_category: dict[str, float]
    category_totals: dict[str, float]
    monthly_trends: dict[str, float]
    top_merchants: list[dict[str, Any]]
    category_chart: list[dict[str, Any]]
    monthly_chart: list[dict[str, Any]]


def _spending_mask(df: pd.DataFrame) -> pd.Series:
    """Boolean mask for expense rows (negative amounts)."""
    return df["amount"] < 0


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure categories are assigned and dates are datetime."""
    out = categorize_transactions(df)
    if not pd.api.types.is_datetime64_any_dtype(out["date"]):
        out["date"] = pd.to_datetime(out["date"])
    return out


def analyze_dataframe(df: pd.DataFrame) -> AnalysisResult:
    """
    Compute summary statistics and chart-ready series from transactions.

    Args:
        df: Validated transaction DataFrame.

    Returns:
        ``AnalysisResult`` with totals, trends, and chart payloads.
    """
    df = prepare_dataframe(df)
    expenses = df.loc[_spending_mask(df)].copy()
    expenses["spend"] = expenses["amount"].abs()

    income_df = df.loc[df["amount"] > 0]
    total_spent = float(expenses["spend"].sum()) if not expenses.empty else 0.0
    total_income = float(income_df["amount"].sum()) if not income_df.empty else 0.0
    net_flow = float(df["amount"].sum())

    if expenses.empty:
        avg_per_category: dict[str, float] = {}
        category_totals: dict[str, float] = {}
        monthly_trends: dict[str, float] = {}
        top_merchants: list[dict[str, Any]] = []
    else:
        by_cat = expenses.groupby("category")["spend"]
        category_totals = {k: float(v) for k, v in by_cat.sum().items()}
        avg_per_category = {k: float(v) for k, v in by_cat.mean().items()}

        expenses["month"] = expenses["date"].dt.to_period("M").astype(str)
        monthly = expenses.groupby("month")["spend"].sum()
        monthly_trends = {k: float(v) for k, v in monthly.items()}

        merchant_totals = (
            expenses.groupby("merchant")["spend"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        top_merchants = [
            {
                "merchant": m,
                "total": float(t),
                "transactions": int((expenses["merchant"] == m).sum()),
            }
            for m, t in merchant_totals.items()
        ]

    category_chart = [
        {"category": c, "amount": a}
        for c, a in sorted(category_totals.items(), key=lambda x: -x[1])
    ]
    monthly_chart = [{"month": m, "amount": a} for m, a in sorted(monthly_trends.items())]

    return AnalysisResult(
        total_spent=round(total_spent, 2),
        total_income=round(total_income, 2),
        net_flow=round(net_flow, 2),
        transaction_count=len(df),
        avg_per_category={k: round(v, 2) for k, v in avg_per_category.items()},
        category_totals={k: round(v, 2) for k, v in category_totals.items()},
        monthly_trends={k: round(v, 2) for k, v in monthly_trends.items()},
        top_merchants=top_merchants,
        category_chart=category_chart,
        monthly_chart=monthly_chart,
    )


def analyze_file(path: str) -> AnalysisResult:
    """Load transactions from disk and return analysis."""
    df = read_transactions(path)
    return analyze_dataframe(df)


def analysis_to_dict(result: AnalysisResult) -> dict[str, Any]:
    """Serialize ``AnalysisResult`` to a JSON-friendly dictionary."""
    return {
        "total_spent": result.total_spent,
        "total_income": result.total_income,
        "net_flow": result.net_flow,
        "transaction_count": result.transaction_count,
        "avg_per_category": result.avg_per_category,
        "category_totals": result.category_totals,
        "monthly_trends": result.monthly_trends,
        "top_merchants": result.top_merchants,
        "category_chart": result.category_chart,
        "monthly_chart": result.monthly_chart,
    }
