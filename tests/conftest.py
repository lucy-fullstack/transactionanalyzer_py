"""Pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_CSV = PROJECT_ROOT / "data" / "sample_transactions.csv"


@pytest.fixture
def sample_csv_path() -> Path:
    """Path to bundled sample transactions."""
    return SAMPLE_CSV


@pytest.fixture
def sample_df(sample_csv_path: Path) -> pd.DataFrame:
    """Loaded sample transactions."""
    from src.parser import read_transactions

    return read_transactions(sample_csv_path)


@pytest.fixture
def minimal_df() -> pd.DataFrame:
    """Small in-memory transaction set for unit tests."""
    return pd.DataFrame(
        {
            "date": ["2024-06-01", "2024-06-02", "2024-06-15", "2024-07-01"],
            "description": [
                "Starbucks coffee",
                "Uber ride downtown",
                "Payroll deposit",
                "Netflix monthly",
            ],
            "amount": [-5.50, -18.00, 2500.00, -15.99],
            "merchant": ["Starbucks", "Uber", "Employer Inc", "Netflix"],
        }
    )
