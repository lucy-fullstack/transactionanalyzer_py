"""FastAPI application — JSON API and HTML dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.analyzer import analysis_to_dict, analyze_file, prepare_dataframe
from src.parser import TransactionParseError, read_transactions

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DEFAULT_DATA = PROJECT_ROOT / "data" / "sample_transactions.csv"

app = FastAPI(
    title="Transaction Analyzer API",
    description="Analyze bank transactions and serve dashboard visualizations.",
    version="1.0.0",
)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _resolve_data_path(file: str | None) -> Path:
    """Resolve analysis file path with safe defaults."""
    if file is None:
        return DEFAULT_DATA
    candidate = Path(file)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/analysis")
def get_analysis(
    file: str | None = Query(default=None, description="CSV/JSON path relative to project root."),
) -> dict[str, Any]:
    """Return full transaction analysis as JSON."""
    path = _resolve_data_path(file)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    try:
        result = analyze_file(str(path))
    except TransactionParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return analysis_to_dict(result)


@app.get("/api/transactions")
def get_transactions(
    file: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict[str, Any]]:
    """Return categorized transaction rows."""
    path = _resolve_data_path(file)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    try:
        df = prepare_dataframe(read_transactions(path)).head(limit)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        return df.to_dict(orient="records")
    except TransactionParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, file: str | None = Query(default=None)) -> HTMLResponse:
    """Serve the Plotly.js dashboard."""
    path = _resolve_data_path(file)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    try:
        result = analyze_file(str(path))
    except TransactionParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "analysis": analysis_to_dict(result),
            "source_file": path.name,
        },
    )
