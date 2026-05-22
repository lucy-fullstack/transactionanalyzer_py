"""Tests for report export."""

from __future__ import annotations

from pathlib import Path

from src.analyzer import analyze_file
from src.exporter import export_from_file, export_summary_csv, export_summary_pdf


def test_export_csv(tmp_path: Path, sample_csv_path: Path) -> None:
    """CSV export creates a non-empty file."""
    out = tmp_path / "report.csv"
    written = export_from_file(sample_csv_path, out, "csv")
    assert written.exists()
    assert written.stat().st_size > 0


def test_export_pdf(tmp_path: Path, sample_csv_path: Path) -> None:
    """PDF export creates a valid PDF file."""
    out = tmp_path / "report.pdf"
    written = export_from_file(sample_csv_path, out, "pdf")
    assert written.suffix == ".pdf"
    assert written.read_bytes()[:4] == b"%PDF"


def test_export_summary_helpers(tmp_path: Path, sample_csv_path: Path) -> None:
    """Direct summary exporters write files."""
    result = analyze_file(str(sample_csv_path))
    assert export_summary_csv(result, tmp_path / "summary.csv").exists()
    assert export_summary_pdf(result, tmp_path / "summary.pdf").exists()
