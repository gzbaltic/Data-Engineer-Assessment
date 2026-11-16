# Data Engineering Assessment

A small dbt + DuckDB project with retail data (customers, products,
orders, order items) sourced from the real
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle. See `docs/pipeline_diagram.html` for an overview of how the
pieces fit together.

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
# Run from the project root -- VENV sets the virtualenv's fully qualified
# (absolute) path, so every command below is unambiguous regardless of
# what's on PATH or which shell/dir you call it from.
VENV="$(pwd)/.venv"

python3 -m venv "$VENV"
"$VENV/bin/pip" install -r requirements.txt

"$VENV/bin/python" scripts/generate_data.py

cd dbt
"$VENV/bin/dbt" deps --profiles-dir .
"$VENV/bin/dbt" seed --profiles-dir .
"$VENV/bin/dbt" run --profiles-dir .
"$VENV/bin/dbt" test --profiles-dir .
cd ..
```

**Windows** (PowerShell):

```powershell
# Run from the project root -- $Venv holds the virtualenv's fully
# qualified (absolute) path, so every command below is unambiguous
# regardless of what's on PATH or which shell/dir you call it from.
$Venv = "$PWD\.venv"

python -m venv $Venv
& "$Venv\Scripts\pip.exe" install -r requirements.txt

& "$Venv\Scripts\python.exe" scripts\generate_data.py

cd dbt
& "$Venv\Scripts\dbt.exe" deps --profiles-dir .
& "$Venv\Scripts\dbt.exe" seed --profiles-dir .
& "$Venv\Scripts\dbt.exe" run --profiles-dir .
& "$Venv\Scripts\dbt.exe" test --profiles-dir .
cd ..
```

Using the venv's own absolute binary path (rather than relying on an
activated shell's `python`/`dbt` resolved from `PATH`) avoids picking up
a different Python install (e.g. a system Python, or another pyenv
version) by accident.

This builds `dbt/dev.duckdb`, a self-contained DuckDB database file.

## Explore the data

**macOS**:

```bash
"$(pwd)/.venv/bin/python" scripts/load_duckdb.py
```

**Windows** (PowerShell):

```powershell
& "$PWD\.venv\Scripts\python.exe" scripts\load_duckdb.py
```

## Tests

**macOS**:

```bash
"$(pwd)/.venv/bin/pytest" scripts/
```

**Windows** (PowerShell):

```powershell
& "$PWD\.venv\Scripts\pytest.exe" scripts\
```

## Project layout

- `scripts/generate_data.py` -- downloads a sample of the real Olist
  dataset from Kaggle (no account/API key needed) and writes it out as the
  raw CSVs, with some intentional data-quality issues layered on top
- `dbt/seeds/` -- raw CSVs loaded as dbt seeds
- `dbt/models/staging/` -- cleaned, typed staging models
- `dbt/models/marts/` -- customer and order fact/dim models
- `scripts/load_duckdb.py` -- loads/queries the resulting DuckDB file
