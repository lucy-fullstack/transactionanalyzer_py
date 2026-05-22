"""Tests for transaction categorization."""

from __future__ import annotations

import pandas as pd

from src.categorizer import categorize_text, categorize_transactions, list_categories


def test_categorize_food() -> None:
    """Food keywords map to food category."""
    assert categorize_text("Starbucks downtown") == "food"
    assert categorize_text("Whole Foods grocery") == "food"


def test_categorize_transport() -> None:
    """Transport keywords map correctly."""
    assert categorize_text("Uber trip") == "transport"
    assert categorize_text("Shell gas station") == "transport"


def test_categorize_entertainment() -> None:
    """Entertainment keywords map correctly."""
    assert categorize_text("Netflix subscription") == "entertainment"
    assert categorize_text("Spotify premium") == "entertainment"


def test_categorize_unknown() -> None:
    """Unknown descriptions fall back to other."""
    assert categorize_text("Random payment XYZ") == "other"


def test_categorize_dataframe(minimal_df: pd.DataFrame) -> None:
    """DataFrame categorization adds category column."""
    result = categorize_transactions(minimal_df)
    assert "category" in result.columns
    assert result.loc[0, "category"] == "food"
    assert result.loc[3, "category"] == "entertainment"


def test_list_categories() -> None:
    """All built-in categories are listed."""
    cats = list_categories()
    assert "food" in cats
    assert "other" in cats
