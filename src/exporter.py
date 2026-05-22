"""Export analysis reports to CSV and PDF."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.analyzer import AnalysisResult, analyze_dataframe, prepare_dataframe
from src.parser import read_transactions

ExportFormat = Literal["csv", "pdf"]


def export_categorized_transactions(df: pd.DataFrame, output_path: str | Path) -> Path:
    """Write categorized transactions to CSV."""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prepared = prepare_dataframe(df)
    prepared["date"] = prepared["date"].dt.strftime("%Y-%m-%d")
    prepared.to_csv(out_path, index=False)
    return out_path


def export_summary_csv(result: AnalysisResult, output_path: str | Path) -> Path:
    """Export category totals and monthly trends as a summary CSV."""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = [
        {"section": "summary", "metric": "total_spent", "value": result.total_spent},
        {"section": "summary", "metric": "total_income", "value": result.total_income},
        {"section": "summary", "metric": "net_flow", "value": result.net_flow},
        {"section": "summary", "metric": "transaction_count", "value": result.transaction_count},
    ]
    for cat, total in result.category_totals.items():
        rows.append({
            "section": "category",
            "metric": cat,
            "value": total,
            "avg": result.avg_per_category.get(cat, 0.0),
        })
    for month, total in result.monthly_trends.items():
        rows.append({"section": "monthly", "metric": month, "value": total})

    pd.DataFrame(rows).to_csv(out_path, index=False)
    return out_path


def export_summary_pdf(result: AnalysisResult, output_path: str | Path) -> Path:
    """Export a human-readable PDF summary report."""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(out_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story: list[object] = [
        Paragraph("Transaction Analysis Report", styles["Title"]),
        Spacer(1, 0.25 * inch),
    ]

    summary_table = Table(
        [
            ["Metric", "Value"],
            ["Total spent", f"${result.total_spent:,.2f}"],
            ["Total income", f"${result.total_income:,.2f}"],
            ["Net flow", f"${result.net_flow:,.2f}"],
            ["Transactions", str(result.transaction_count)],
        ],
        colWidths=[2.5 * inch, 2.5 * inch],
    )
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ])
    )
    story.extend([summary_table, Spacer(1, 0.35 * inch)])

    story.append(Paragraph("Spending by Category", styles["Heading2"]))
    cat_rows = [["Category", "Total", "Average"]]
    for cat, total in sorted(result.category_totals.items(), key=lambda x: -x[1]):
        cat_rows.append([
            cat,
            f"${total:,.2f}",
            f"${result.avg_per_category.get(cat, 0):,.2f}",
        ])
    if len(cat_rows) == 1:
        cat_rows.append(["—", "—", "—"])
    cat_table = Table(cat_rows, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
    cat_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.extend([cat_table, Spacer(1, 0.35 * inch)])

    story.append(Paragraph("Top Merchants", styles["Heading2"]))
    merch_rows = [["Merchant", "Total spent", "Transactions"]]
    for m in result.top_merchants:
        merch_rows.append([
            m["merchant"],
            f"${m['total']:,.2f}",
            str(m.get("transactions", "")),
        ])
    if len(merch_rows) == 1:
        merch_rows.append(["—", "—", "—"])
    merch_table = Table(merch_rows, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
    merch_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    story.append(merch_table)

    doc.build(story)
    return out_path


def export_report(
    result: AnalysisResult,
    output_path: str | Path,
    fmt: ExportFormat,
) -> Path:
    """Export analysis in the requested format."""
    path = Path(output_path)
    if fmt == "pdf":
        return export_summary_pdf(result, path if path.suffix == ".pdf" else path.with_suffix(".pdf"))
    return export_summary_csv(result, path if path.suffix == ".csv" else path.with_suffix(".csv"))


def export_from_file(
    input_path: str | Path,
    output_path: str | Path,
    fmt: ExportFormat,
    *,
    include_transactions: bool = False,
) -> Path:
    """Analyze a file and export the report."""
    df = read_transactions(input_path)
    result = analyze_dataframe(df)
    if include_transactions and fmt == "csv":
        tx_path = Path(output_path).with_stem(Path(output_path).stem + "_transactions")
        export_categorized_transactions(df, tx_path)
    return export_report(result, output_path, fmt)
