# Data Engineering Assessment

A small dbt + DuckDB project with synthetic retail data (customers,
products, orders, order items). See `docs/pipeline_diagram.html` for an
overview of how the pieces fit together.

## Setup

```bash
git clone <this repo> && cd de_assessment

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/generate_data.py

cd dbt
dbt deps --profiles-dir .
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

This builds `dbt/dev.duckdb`, a self-contained DuckDB database file.

## Explore the data

```bash
cd ..
python scripts/load_duckdb.py
```

## Tests

```bash
pytest scripts/
```

## Project layout

- `scripts/generate_data.py` -- generates the raw CSVs (with some
  intentional data-quality issues)
- `dbt/seeds/` -- raw CSVs loaded as dbt seeds
- `dbt/models/staging/` -- cleaned, typed staging models
- `dbt/models/marts/` -- customer and order fact/dim models
- `scripts/load_duckdb.py` -- loads/queries the resulting DuckDB file
