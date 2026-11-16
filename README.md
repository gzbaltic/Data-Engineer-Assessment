# Data Engineering Assessment

A small dbt + DuckDB project with synthetic retail data (customers,
products, orders, order items). See `docs/pipeline_diagram.html` for an
overview of how the pieces fit together.

## Setup

Requires Python 3.12.6 (pinned in `.python-version`). This project uses
[pyenv](https://github.com/pyenv/pyenv) to manage the Python version, so
every contributor builds on the same interpreter regardless of what's on
their system already.

You don't need Python pre-installed -- these steps install it from
scratch via [pyenv](https://github.com/pyenv/pyenv) (macOS) or
[pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows), so every
contributor builds on the same interpreter regardless of what's on their
system already.

### 1. Install pyenv

**macOS** (requires [Homebrew](https://brew.sh)):

```bash
brew install pyenv
```

Add pyenv to your shell (zsh):

```bash
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**Windows** (PowerShell, requires [Git for Windows](https://git-scm.com/download/win)):

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Close and reopen PowerShell so the new `PYENV`/`PATH` environment
variables take effect, then confirm with `pyenv --version`.

### 2. Clone the repo and install Python 3.12.6

**macOS**:

```bash
git clone <this repo> && cd de_assessment

pyenv install 3.12.6  # skip if already installed
pyenv local 3.12.6    # reads/writes .python-version -- already pinned here
python3 --version     # confirm: Python 3.12.6
```

**Windows** (PowerShell):

```powershell
git clone <this repo>; cd de_assessment

pyenv install 3.12.6  # skip if already installed
pyenv local 3.12.6    # reads/writes .python-version -- already pinned here
python --version      # confirm: Python 3.12.6
```

### 3. Create the virtualenv and install dependencies

**macOS**:

```bash
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

**Windows** (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts\generate_data.py

cd dbt
dbt deps --profiles-dir .
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

This builds `dbt/dev.duckdb`, a self-contained DuckDB database file.

## Explore the data

**macOS**:

```bash
cd ..
python scripts/load_duckdb.py
```

**Windows** (PowerShell):

```powershell
cd ..
python scripts\load_duckdb.py
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
