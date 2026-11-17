# Data Engineering Assessment

A small dbt + DuckDB project with retail data (customers, products,
orders, order items) sourced from the real
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle.

## What you'll do

1. **Set up the environment.** Follow [Setup](#setup) below -- install
   Python, create the venv, install dependencies.
2. **Run `dbt seed`** (from `dbt/`: `dbt seed --profiles-dir .`) to load
   the raw CSVs into DuckDB.
3. **Write the logic for [`stg_products`](dbt/models/staging/stg_products.sql).**
   It's empty -- build it from scratch, reading from the `raw_products`
   seed: cast `unit_price` to a decimal, and filter out rows with a
   negative price (a known data-entry error upstream). See
   `dbt/models/staging/_staging.yml` for the tests it needs to pass.
4. **Run just that model**: from `dbt/`,
   `dbt run --select stg_products --profiles-dir .`
5. **Complete [the metadata macro](dbt/macros/add_metadata_columns.sql)**
   -- it's missing the `dbt_invocation_id` column -- and call it from
   inside `stg_products`'s select list.
6. **Run `stg_products` again**: `dbt run --select stg_products --profiles-dir .`
7. **Run the full build**: `dbt build --profiles-dir .` (runs every
   model and test, including `stg_products`, together).

If you get stuck anywhere in steps 3-6, `scripts/apply_solution.py`
restores the finished versions of those files -- see
[Recover a working state](#recover-a-working-state) below.

## Setup

Requires Python 3.12.6 (pinned in `.python-version`). This project
manages the Python version with [pyenv](https://github.com/pyenv/pyenv)
on macOS/Linux, or its Windows port
[pyenv-win](https://github.com/pyenv-win/pyenv-win) (same CLI, no
Homebrew/Unix shell required) on Windows -- plain `pyenv` itself does not
run on Windows. Either way, you don't need Python pre-installed: the
steps below install it from scratch, so every contributor builds on the
same interpreter regardless of what's on their system already.

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

**macOS, no Homebrew:** use the official installer script instead --
no admin rights needed, it installs entirely under `~/.pyenv`:

```bash
curl https://pyenv.run | bash
```

(If `curl | bash` is blocked on your machine, clone it directly instead:
`git clone https://github.com/pyenv/pyenv.git ~/.pyenv`.)

Then add it to your shell (zsh):

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**Windows** (PowerShell, requires [Git for Windows](https://git-scm.com/download/win)):

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Close and reopen PowerShell so the new `PYENV`/`PATH` environment
variables take effect, then confirm with `pyenv --version`.

> **Note (Windows):** if the script above fails with "running scripts is
> disabled on this system", PowerShell's default execution policy is
> blocking it -- run
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> first (no admin rights needed, since it's scoped to the current user),
> then retry.
>
> **Note (Windows):** every command in this README that invokes the venv
> directly uses its `.exe` wrapper (e.g. `dbt.exe`, `pytest.exe`) under
> `.venv\Scripts\` -- `pip` creates these automatically for every
> console-script package it installs, so nothing extra needs installing
> for them to exist.

### 2. Clone the repo and install Python 3.12.6

**macOS**:

Clone the repo, then `cd` into the cloned directory before continuing.

```bash
pyenv install 3.12.6  # skip if already installed
pyenv local 3.12.6    # reads/writes .python-version -- already pinned here
python3 --version     # confirm: Python 3.12.6
```

**Windows** (PowerShell):

```powershell
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

# Clean slate: remove any previous venv/DuckDB file/dbt artifacts so
# this always runs the same way, regardless of what a prior attempt
# left behind.
rm -rf "$VENV" dbt/dev.duckdb dbt/target dbt/logs dbt/dbt_packages

python3 -m venv "$VENV"
"$VENV/bin/pip" install -r requirements.txt

"$VENV/bin/python" scripts/generate_data.py

cd dbt
"$VENV/bin/dbt" deps --profiles-dir .
"$VENV/bin/dbt" seed --profiles-dir .
cd ..
```

Stop there -- don't run `dbt run`/`dbt test` yet. `stg_products` is
intentionally empty and the metadata macro intentionally incomplete, so
a full `dbt run` will fail until you've done the work in
[What you'll do](#what-youll-do) below.

**Windows** (PowerShell):

```powershell
# Run from the project root -- $Venv holds the virtualenv's fully
# qualified (absolute) path, so every command below is unambiguous
# regardless of what's on PATH or which shell/dir you call it from.
$Venv = "$PWD\.venv"

# Clean slate: remove any previous venv/DuckDB file/dbt artifacts so
# this always runs the same way, regardless of what a prior attempt
# left behind.
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $Venv, dbt\dev.duckdb, dbt\target, dbt\logs, dbt\dbt_packages

python -m venv $Venv
& "$Venv\Scripts\pip.exe" install -r requirements.txt

& "$Venv\Scripts\python.exe" scripts\generate_data.py

cd dbt
& "$Venv\Scripts\dbt.exe" deps --profiles-dir .
& "$Venv\Scripts\dbt.exe" seed --profiles-dir .
cd ..
```

Stop there -- don't run `dbt run`/`dbt test` yet. `stg_products` is
intentionally empty and the metadata macro intentionally incomplete, so
a full `dbt run` will fail until you've done the work in
[What you'll do](#what-youll-do) below.

Using the venv's own absolute binary path (rather than relying on an
activated shell's `python`/`dbt` resolved from `PATH`) avoids picking up
a different Python install (e.g. a system Python, or another pyenv
version) by accident.

`dbt seed` builds `dbt/dev.duckdb`, a self-contained DuckDB database
file, and loads the raw seed tables into it. `dbt run`/`dbt build` (once
you're ready for them) add the staging and mart models to the same
file.

## Explore the data

**macOS**:

```bash
"$(pwd)/.venv/bin/python" scripts/load_duckdb.py
```

**Windows** (PowerShell):

```powershell
& "$PWD\.venv\Scripts\python.exe" scripts\load_duckdb.py
```

## Query the data

`dbt/dev.duckdb` is a plain DuckDB file, so you can query it directly
without going through `load_duckdb.py`.

**Using the `duckdb` Python package (already in `requirements.txt`,
no extra install):**

**macOS**:

```bash
"$(pwd)/.venv/bin/python" -c "
import duckdb
con = duckdb.connect('dbt/dev.duckdb', read_only=True)
print(con.sql('select * from customer_order_summary limit 10'))
"
```

**Windows** (PowerShell):

```powershell
& "$PWD\.venv\Scripts\python.exe" -c "
import duckdb
con = duckdb.connect('dbt/dev.duckdb', read_only=True)
print(con.sql('select * from customer_order_summary limit 10'))
"
```

**Using the standalone DuckDB CLI** (if you have it installed --
see [duckdb.org/docs/installation](https://duckdb.org/docs/installation)):

```bash
duckdb dbt/dev.duckdb -c "select * from customer_order_summary limit 10;"
```

Open it in read-only mode (`-readonly`) if you also have `dbt` running
against the same file, since DuckDB only allows one writer at a time.
Tables available to query: the seeds (`customers`, `products`, `orders`,
`order_items`), the staging views (`stg_customers`, `stg_order_items`,
`stg_orders`, `stg_products`), and the marts
(`dim_customers`, `fct_order_items`, `customer_order_summary`). Run
`show tables;` inside either tool above to list them all.

## Recover a working state

If you get stuck completing [`stg_products.sql`](dbt/models/staging/stg_products.sql)
or [`add_metadata_columns.sql`](dbt/macros/add_metadata_columns.sql),
[`scripts/apply_solution.py`](scripts/apply_solution.py) overwrites both
with their finished solution so you can get back to a working state and
keep going.

**macOS**:

```bash
"$(pwd)/.venv/bin/python" scripts/apply_solution.py
```

**Windows** (PowerShell):

```powershell
& "$PWD\.venv\Scripts\python.exe" scripts\apply_solution.py
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
