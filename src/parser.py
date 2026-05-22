"""File reading and validation for transaction data."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

REQUIRED_COLUMNS = frozenset({"date", "description", "amount"})
SUPPORTED_EXTENSIONS = frozenset({".csv", ".json"})


class TransactionParseError(ValueError):
    """Raised when a transaction file cannot be parsed or validated."""


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to lowercase stripped strings."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _validate_schema(df: pd.DataFrame) -> None:
    """Ensure required columns exist and data types are usable."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise TransactionParseError(
            f"Missing required columns: {sorted(missing)}. "
            f"Expected at least: {sorted(REQUIRED_COLUMNS)}"
        )
    if df.empty:
        raise TransactionParseError("Transaction file contains no rows.")


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce date, amount, and text fields to proper types."""
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    if out["date"].isna().any():
        bad = int(out["date"].isna().sum())
        raise TransactionParseError(f"Could not parse {bad} date value(s).")

    out["amount"] = pd.to_numeric(out["amount"], errors="coerce")
    if out["amount"].isna().any():
        bad = int(out["amount"].isna().sum())
        raise TransactionParseError(f"Could not parse {bad} amount value(s).")

    out["description"] = out["description"].astype(str).str.strip()
    if "merchant" not in out.columns:
        out["merchant"] = out["description"]
    else:
        out["merchant"] = out["merchant"].fillna(out["description"]).astype(str).str.strip()

    return out


def read_transactions(path: str | Path) -> pd.DataFrame:
    """
    Read and validate transactions from a CSV or JSON file.

    Args:
        path: Path to a ``.csv`` or ``.json`` transaction file.

    Returns:
        DataFrame with columns ``date``, ``description``, ``amount``, ``merchant``.

    Raises:
        TransactionParseError: If the file is missing, unsupported, or invalid.
        FileNotFoundError: If the path does not exist.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Transaction file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise TransactionParseError(
            f"Unsupported file type '{suffix}'. Use one of: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if suffix == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_json(file_path)

    df = _normalize_columns(df)
    _validate_schema(df)
    df = _coerce_types(df)
    return df.sort_values("date").reset_index(drop=True)


def detect_format(path: str | Path) -> Literal["csv", "json"]:
    """Return the detected file format based on extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    raise TransactionParseError(f"Cannot detect format for extension: {suffix}")
