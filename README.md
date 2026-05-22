# Transaction Analyzer

A Python toolkit for analyzing personal and business bank transactions. Import CSV or JSON files, automatically categorize spending, view interactive charts in a web dashboard, and export summary reports.

## Features

- **CLI** (`typer`) — analyze files from the terminal with rich tables or JSON output
- **Auto-categorization** — keyword matching for food, transport, entertainment, shopping, utilities, healthcare, education, and income
- **Statistics** — total spent, income, net flow, per-category averages, monthly trends, top merchants
- **REST API** — FastAPI JSON endpoints for programmatic access
- **Dashboard** — HTML UI with Plotly.js pie and line charts plus a top-merchants table
- **Export** — summary reports to CSV or PDF
- **Sample data** — 120 realistic transactions in `data/sample_transactions.csv`
- **Tests** — 26 pytest cases covering parsing, categorization, analysis, export, and API

## Requirements

- Python 3.11+
- Dependencies: pandas, FastAPI, Plotly, Typer, ReportLab, Jinja2 (see `pyproject.toml`)

## Installation

```bash
cd transaction_analyzer
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Transaction file format

CSV or JSON files must include these columns:

| Column        | Type   | Required | Description                           |
|---------------|--------|----------|---------------------------------------|
| `date`        | date   | Yes      | Transaction date (`YYYY-MM-DD`)       |
| `description` | string | Yes      | Transaction description               |
| `amount`      | number | Yes      | Negative = expense, positive = income |
| `merchant`    | string | No       | Merchant name (defaults to description) |

**Example CSV:**

```csv
date,description,amount,merchant
2024-06-01,Starbucks coffee,-5.50,Starbucks
2024-06-15,Payroll deposit,3200.00,Employer Inc
```

## Usage

### CLI

Analyze the bundled sample data:

```bash
txanalyze analyze data/sample_transactions.csv
```

JSON output:

```bash
txanalyze analyze data/sample_transactions.csv --json
```

Start the web dashboard:

```bash
txanalyze serve
# Open http://127.0.0.1:8000/
```

Export a PDF report:

```bash
txanalyze export data/sample_transactions.csv -f pdf -o exports/monthly_report
```

List supported categories:

```bash
txanalyze categories
```

### API

| Endpoint            | Method | Description                               |
|---------------------|--------|-------------------------------------------|
| `/`                 | GET    | HTML dashboard (Plotly charts)            |
| `/health`           | GET    | Health check                              |
| `/api/analysis`     | GET    | Full analysis JSON (`?file=...` optional) |
| `/api/transactions` | GET    | Categorized rows (`?limit=100`)         |

Example:

```bash
curl http://127.0.0.1:8000/api/analysis
curl "http://127.0.0.1:8000/api/analysis?file=data/sample_transactions.csv"
```

### Python API

```python
from src.parser import read_transactions
from src.analyzer import analyze_dataframe, analysis_to_dict

df = read_transactions("data/sample_transactions.csv")
result = analyze_dataframe(df)
print(analysis_to_dict(result))
```

## Project structure

```
transaction_analyzer/
├── src/
│   ├── parser.py       # File reading and validation
│   ├── categorizer.py  # Keyword-based categorization
│   ├── analyzer.py     # Statistics and aggregations
│   ├── exporter.py     # CSV/PDF export
│   ├── api.py          # FastAPI application
│   └── cli.py          # Typer CLI
├── tests/
├── data/
│   └── sample_transactions.csv
├── templates/
│   └── dashboard.html
├── pyproject.toml
└── README.md
```

## Screenshots

> Add screenshots after running the dashboard locally.

| Dashboard overview | Category pie chart |
|--------------------|--------------------|
| _Run `txanalyze serve` and capture `/`_ | _Spending breakdown by category_ |

| Monthly trends | Top merchants |
|----------------|---------------|
| _Line chart of monthly spending_ | _Table of top 5 merchants_ |

## Running tests

```bash
pytest -v
```

## License

MIT
