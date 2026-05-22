"""Tests for transaction file parsing."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.parser import TransactionParseError, detect_format, read_transactions


def test_read_sample_csv(sample_csv_path: Path) -> None:
    """Sample CSV loads with required columns."""
    df = read_transactions(sample_csv_path)
    assert len(df) >= 100
    assert {"date", "description", "amount", "merchant"}.issubset(df.columns)


def test_read_json_file(tmp_path: Path, minimal_df: pd.DataFrame) -> None:
    """JSON transaction files are supported."""
    path = tmp_path / "tx.json"
    minimal_df.to_json(path, orient="records", date_format="iso")
    df = read_transactions(path)
    assert len(df) == 4


def test_missing_file_raises() -> None:
    """Missing paths raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_transactions("/nonexistent/file.csv")


def test_unsupported_extension(tmp_path: Path) -> None:
    """Unsupported extensions raise TransactionParseError."""
    bad = tmp_path / "data.txt"
    bad.write_text("hello")
    with pytest.raises(TransactionParseError, match="Unsupported"):
        read_transactions(bad)


def test_missing_required_columns(tmp_path: Path) -> None:
    """Files without required columns are rejected."""
    path = tmp_path / "bad.csv"
    path.write_text("date,amount\n2024-01-01,-10\n")
    with pytest.raises(TransactionParseError, match="Missing required"):
        read_transactions(path)


def test_detect_format_csv(sample_csv_path: Path) -> None:
    """CSV extension is detected correctly."""
    assert detect_format(sample_csv_path) == "csv"


def test_invalid_dates_rejected(tmp_path: Path) -> None:
    """Unparseable dates raise TransactionParseError."""
    path = tmp_path / "bad_dates.csv"
    path.write_text("date,description,amount\nnot-a-date,Coffee,-5\n")
    with pytest.raises(TransactionParseError, match="date"):
        read_transactions(path)
