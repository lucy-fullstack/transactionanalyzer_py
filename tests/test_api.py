"""Tests for FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Health check returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analysis_api_default_sample() -> None:
    """Analysis API returns JSON for default sample data."""
    response = client.get("/api/analysis")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_count"] >= 100
    assert "category_totals" in data
    assert "monthly_chart" in data


def test_dashboard_html() -> None:
    """Dashboard route returns HTML with Plotly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "plotly" in response.text.lower()
    assert "pie-chart" in response.text


def test_analysis_missing_file() -> None:
    """Missing files return 404."""
    response = client.get("/api/analysis", params={"file": "missing.csv"})
    assert response.status_code == 404
