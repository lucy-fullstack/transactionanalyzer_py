"""Tests for analysis and statistics."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.analyzer import analyze_dataframe, analyze_file, analysis_to_dict


def test_analyze_sample_file(sample_csv_path: Path) -> None:
    """Full file analysis returns expected structure."""
    result = analyze_file(str(sample_csv_path))
    assert result.transaction_count >= 100
    assert result.total_spent > 0
    assert isinstance(result.category_totals, dict)


def test_total_spent_excludes_income(minimal_df: pd.DataFrame) -> None:
    """Total spent sums only negative amounts."""
    result = analyze_dataframe(minimal_df)
    assert result.total_spent == pytest.approx(5.50 + 18.00 + 15.99)


def test_category_totals(minimal_df: pd.DataFrame) -> None:
    """Category totals aggregate expenses by category."""
    result = analyze_dataframe(minimal_df)
    assert "food" in result.category_totals
    assert "transport" in result.category_totals
    assert "entertainment" in result.category_totals


def test_monthly_trends(minimal_df: pd.DataFrame) -> None:
    """Monthly trends group spending by calendar month."""
    result = analyze_dataframe(minimal_df)
    assert "2024-06" in result.monthly_trends
    assert "2024-07" in result.monthly_trends


def test_top_merchants_limit(minimal_df: pd.DataFrame) -> None:
    """At most five merchants are returned."""
    result = analyze_dataframe(minimal_df)
    assert len(result.top_merchants) <= 5


def test_analysis_to_dict_serializable(minimal_df: pd.DataFrame) -> None:
    """Analysis dict contains chart payloads."""
    result = analyze_dataframe(minimal_df)
    data = analysis_to_dict(result)
    assert "category_chart" in data
    assert "monthly_chart" in data
    assert data["transaction_count"] == 4
