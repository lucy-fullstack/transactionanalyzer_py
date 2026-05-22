"""Typer CLI for transaction analysis."""

from __future__ import annotations

import json
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from src.analyzer import analysis_to_dict, analyze_file
from src.exporter import ExportFormat, export_from_file
from src.parser import TransactionParseError

app = typer.Typer(name="txanalyze", help="Analyze bank transactions from CSV/JSON files.")
console = Console()


@app.command("analyze")
def analyze_command(
    file: Path = typer.Argument(..., help="Path to CSV or JSON transaction file."),
    json_output: bool = typer.Option(False, "--json", "-j", help="Print full analysis as JSON."),
) -> None:
    """Analyze a transaction file and print summary statistics."""
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(code=1)

    try:
        result = analyze_file(str(file))
    except (TransactionParseError, FileNotFoundError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        console.print_json(json.dumps(analysis_to_dict(result), indent=2))
        return

    console.print(f"\n[bold]Transaction Analysis[/bold] — {file.name}\n")
    console.print(f"  Transactions: [cyan]{result.transaction_count}[/cyan]")
    console.print(f"  Total spent:  [red]${result.total_spent:,.2f}[/red]")
    console.print(f"  Total income: [green]${result.total_income:,.2f}[/green]")
    console.print(f"  Net flow:     ${result.net_flow:,.2f}\n")

    if result.category_totals:
        table = Table(title="Spending by Category")
        table.add_column("Category", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Average", justify="right")
        for cat, total in sorted(result.category_totals.items(), key=lambda x: -x[1]):
            avg = result.avg_per_category.get(cat, 0.0)
            table.add_row(cat, f"${total:,.2f}", f"${avg:,.2f}")
        console.print(table)

    if result.monthly_trends:
        console.print("\n[bold]Monthly trends[/bold]")
        for month, amount in sorted(result.monthly_trends.items()):
            console.print(f"  {month}: ${amount:,.2f}")

    if result.top_merchants:
        console.print("\n[bold]Top 5 merchants[/bold]")
        for i, m in enumerate(result.top_merchants, 1):
            console.print(f"  {i}. {m['merchant']}: ${m['total']:,.2f}")


@app.command("serve")
def serve_command(
    host: str = typer.Option("127.0.0.1", help="Bind host."),
    port: int = typer.Option(8000, help="Bind port."),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload."),
) -> None:
    """Start the FastAPI web server and dashboard."""
    console.print(f"[green]Starting dashboard[/green] at http://{host}:{port}/")
    uvicorn.run("src.api:app", host=host, port=port, reload=reload)


@app.command("export")
def export_command(
    file: Path = typer.Argument(..., help="Input transaction file."),
    output: Path = typer.Option(Path("exports/report"), "--output", "-o", help="Output path."),
    fmt: ExportFormat = typer.Option("csv", "--format", "-f", help="Export format: csv or pdf."),
    include_transactions: bool = typer.Option(
        False, "--transactions", help="Also export categorized transactions CSV.",
    ),
) -> None:
    """Export analysis report to CSV or PDF."""
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(code=1)

    try:
        written = export_from_file(file, output, fmt, include_transactions=include_transactions)
    except (TransactionParseError, FileNotFoundError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Report written to:[/green] {written}")


@app.command("categories")
def categories_command() -> None:
    """List all supported transaction categories."""
    from src.categorizer import list_categories

    for cat in list_categories():
        console.print(f"  • {cat}")


def main() -> None:
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    main()
