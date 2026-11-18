# Data Engineering Assessment

A small dbt + DuckDB project with retail data (customers, products,
orders, order items) sourced from the real
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle.

**Run every command below from the project root** (the directory this
README is in), unless a `cd` tells you otherwise.

## What you'll do

1. Follow [Setup](#setup) below -- this also seeds the raw data into
   `dbt/dev.duckdb`.
2. Write the logic for [`stg_products`](dbt/models/staging/stg_products.sql):
   read from the `raw_products` seed, cast `unit_price` to a decimal, and
   filter out rows with a negative price. See
   [`dbt/models/staging/_staging.yml`](dbt/models/staging/_staging.yml) for
   the tests it needs to pass.
3. Run the model(s) then query `stg_products` (see [Query the data](#query-the-data)) to
   check your work.
4. Complete [the metadata macro](dbt/macros/add_metadata_columns.sql)
   (missing the `dbt_invocation_id` column) and call it from inside
   `stg_products`'s select list.
5. Run `cd dbt && dbt run --select stg_products --profiles-dir . && cd ..`
   again, then query `stg_products` (see [Query the data](#query-the-data))
   to check your work.
6. Run the full build: `cd dbt && dbt build --profiles-dir . && cd ..`,
   then query any of the resulting models (see
   [Query the data](#query-the-data)).

If you get stuck in steps 2-5, `scripts/apply_solution.py` restores the
finished versions of those files -- see
[Recover a working state](#recover-a-working-state).

## Setup

Requires Python 3.12.6 (pinned in `.python-version`), managed via
[pyenv](https://github.com/pyenv/pyenv) (macOS/Linux) or
[pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows).

### 1. Install pyenv

**macOS** (requires [Homebrew](https://brew.sh)):

```bash
brew install pyenv
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

**macOS, no Homebrew:**

```bash
curl https://pyenv.run | bash
```

(If blocked, clone directly: `git clone https://github.com/pyenv/pyenv.git ~/.pyenv`.)

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

Close and reopen PowerShell, then confirm with `pyenv --version`.

> If the script fails with "running scripts is disabled", run
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> first, then retry.

### 2. Install Python 3.12.6

**macOS**:

```bash
pyenv install 3.12.6  # skip if already installed
pyenv local 3.12.6
python3 --version      # confirm: Python 3.12.6
```

**Windows** (PowerShell):

```powershell
pyenv install 3.12.6  # skip if already installed
pyenv local 3.12.6
python --version       # confirm: Python 3.12.6
```

### 3. Create the virtualenv and install Python dependencies

Run from the project root (the directory this README is in):

**macOS**:

```bash
cd Data-Engineer-Assessment

rm -rf .venv

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python scripts/generate_data.py
```

**Windows** (PowerShell):

```powershell
cd Data-Engineer-Assessment

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .venv

python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt

.venv\Scripts\python.exe scripts\generate_data.py
```

### 4. Install dbt packages

Run from the project root; these commands `cd` into `dbt/` and back out
on their own:

**macOS**:

```bash
cd Data-Engineer-Assessment

rm -rf dbt/dev.duckdb dbt/target dbt/logs dbt/dbt_packages

cd dbt
../.venv/bin/dbt deps --profiles-dir .
cd ..
```

**Windows** (PowerShell):

```powershell
cd Data-Engineer-Assessment

Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dbt\dev.duckdb, dbt\target, dbt\logs, dbt\dbt_packages

cd dbt
..\.venv\Scripts\dbt.exe deps --profiles-dir .
cd ..
```

Now seed the raw seed files -- this builds `dbt/dev.duckdb`, a
self-contained DuckDB database file.

Check it loaded by listing the tables: `.venv/bin/python
scripts/load_duckdb.py` (macOS) or `.venv\Scripts\python.exe
scripts\load_duckdb.py` (Windows). See [Query the
data](#query-the-data) below for more.

Don't run `dbt run`/`dbt test` yet -- `stg_products` is intentionally
empty and the metadata macro intentionally incomplete until you've done
the work in [What you'll do](#what-youll-do). `dbt run`/`dbt build` add
the staging and mart models to the same `dbt/dev.duckdb` file.

## Query the data

[`scripts/load_duckdb.py`](scripts/load_duckdb.py) connects to
`dbt/dev.duckdb` and prints its tables. Pass one or more table names to
also print the first 10 rows of each.

Run from the project root:

**macOS**:

```bash
cd Data-Engineer-Assessment
.venv/bin/python scripts/load_duckdb.py stg_products dim_customers
```

**Windows** (PowerShell):

```powershell
cd Data-Engineer-Assessment
.venv\Scripts\python.exe scripts\load_duckdb.py stg_products dim_customers
```

Tables available grow as you progress: seeds first (`raw_customers`,
`raw_products`, `raw_orders`, `raw_order_items`), then staging views as
you build them (`stg_products`, ...), then marts after a full
`dbt build` (`dim_customers`, `fct_order_items`,
`customer_order_summary`). Run the script with no table name to just
list what's there.

## Recover a working state

[`scripts/apply_solution.py`](scripts/apply_solution.py) overwrites
[`stg_products.sql`](dbt/models/staging/stg_products.sql) and
[`add_metadata_columns.sql`](dbt/macros/add_metadata_columns.sql) with
their finished solution.

Run from the project root:

**macOS**:

```bash
cd Data-Engineer-Assessment
.venv/bin/python scripts/apply_solution.py
```

**Windows** (PowerShell):

```powershell
cd Data-Engineer-Assessment
.venv\Scripts\python.exe scripts\apply_solution.py
```
