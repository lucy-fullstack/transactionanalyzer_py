"""Automatic transaction categorization via keyword matching."""

from __future__ import annotations

import re
from typing import Final

import pandas as pd

CATEGORY_KEYWORDS: Final[dict[str, list[str]]] = {
    "food": [
        "restaurant", "cafe", "coffee", "starbucks", "mcdonald", "uber eats",
        "doordash", "grubhub", "grocery", "whole foods", "trader joe", "safeway",
        "kroger", "pizza", "sushi", "bakery", "supermarket", "food", "dining",
    ],
    "transport": [
        "uber", "lyft", "gas", "shell", "chevron", "exxon", "parking", "metro",
        "transit", "train", "airline", "delta", "united", "southwest", "toll",
        "car wash", "auto",
    ],
    "entertainment": [
        "netflix", "spotify", "hulu", "disney", "cinema", "movie", "theater",
        "concert", "steam", "playstation", "xbox", "game", "museum", "ticket",
    ],
    "shopping": [
        "amazon", "target", "walmart", "costco", "best buy", "apple store",
        "nike", "zara", "ikea", "ebay", "etsy", "mall", "retail",
    ],
    "utilities": [
        "electric", "water", "gas bill", "internet", "comcast", "verizon",
        "at&t", "phone", "utility", "insurance",
    ],
    "healthcare": [
        "pharmacy", "cvs", "walgreens", "hospital", "clinic", "doctor",
        "dental", "medical", "health",
    ],
    "education": [
        "university", "college", "tuition", "coursera", "udemy", "books",
        "library", "school",
    ],
    "income": [
        "payroll", "salary", "deposit", "refund", "interest", "dividend",
        "transfer in", "direct dep",
    ],
}

DEFAULT_CATEGORY: Final[str] = "other"


def _compile_patterns() -> list[tuple[str, re.Pattern[str]]]:
    """Compile keyword patterns for efficient matching."""
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        escaped = [re.escape(kw) for kw in keywords]
        patterns.append((category, re.compile("|".join(escaped), re.IGNORECASE)))
    return patterns


_COMPILED_PATTERNS = _compile_patterns()


def categorize_text(text: str) -> str:
    """
    Assign a category to a single transaction description.

    Args:
        text: Merchant name or transaction description.

    Returns:
        Category string (e.g. ``food``, ``transport``) or ``other``.
    """
    if not text or not str(text).strip():
        return DEFAULT_CATEGORY

    haystack = str(text).lower()
    for category, pattern in _COMPILED_PATTERNS:
        if pattern.search(haystack):
            return category
    return DEFAULT_CATEGORY


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a ``category`` column using keyword matching on merchant and description.

    Args:
        df: DataFrame with at least ``description`` and optionally ``merchant``.

    Returns:
        Copy of the DataFrame with a ``category`` column.
    """
    out = df.copy()
    if "category" in out.columns and out["category"].notna().all():
        return out

    combined = (
        out.get("merchant", out["description"]).astype(str)
        + " "
        + out["description"].astype(str)
    )
    out["category"] = combined.apply(categorize_text)
    return out


def list_categories() -> list[str]:
    """Return all known category names including ``other``."""
    return sorted(set(CATEGORY_KEYWORDS) | {DEFAULT_CATEGORY})
