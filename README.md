# Data Engineering Assessment

A small dbt + DuckDB project with retail data (customers, products,
orders, order items) sourced from the real
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
on Kaggle.

**Run every command below from the project root** (the directory this
README is in), unless a `cd` tells you otherwise.

If you are in the parent directory, run `cd Data-Engineer-Assessment`
once before starting. After reopening a terminal, return to this project
root before continuing. Windows examples use PowerShell (Windows
PowerShell 5.1 or PowerShell 7), rather than Command Prompt or Git Bash.

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
5. Run dbt run again, then query `stg_products` (see [Query the data](#query-the-data))
to check your work.
6. Run the full build in dbt, including tests,
then query any of the resulting models (see
[Query the data](#query-the-data)).
7. Complete [`get_tests_by_model`](scripts/parse_manifest.py) in
`scripts/parse_manifest.py`: given the dbt manifest produced by step 6,
return a mapping of model name to the names of tests that run against
it. Run it with
`.venv/bin/python scripts/parse_manifest.py` (macOS) or
`.\.venv\Scripts\python.exe .\scripts\parse_manifest.py` (Windows) and
check the output against `dbt/models/staging/_staging.yml` and
`dbt/models/marts/_marts.yml`.

If you get stuck in steps 2-5 or 7, `scripts/apply_solution.py` restores
the finished versions of those files -- see
[Recover a working state](#recover-a-working-state).

## Setup

Requires Python 3.12.6 (pinned in `.python-version`), managed via
[pyenv](https://github.com/pyenv/pyenv) (macOS/Linux) or
[pyenv-win](https://github.com/pyenv-win/pyenv-win) (Windows).

The macOS instructions install pyenv directly into `$HOME/.pyenv`.

### 1. Install pyenv

For a clean reinstall, first remove the existing pyenv directory. This
also deletes the Python versions installed inside it.

**macOS/Linux (Bash or Zsh)**:

Do not prefix these commands with `sudo` -- `.zshrc` is a file in your own
home directory, so it never needs elevated permissions. If you get
`permission denied` writing to `~/.zshrc`, it means the file's ownership
got changed (often by a past accidental `sudo` write); fix that first:

```bash
[ -O ~/.zshrc ] || sudo chown "$(whoami)":staff ~/.zshrc
```

```bash
rm -rf "$HOME/.pyenv"
```

**Windows (PowerShell)**:

```powershell
if (Test-Path -LiteralPath "$env:USERPROFILE\.pyenv") {
Remove-Item -LiteralPath "$env:USERPROFILE\.pyenv" -Recurse -Force -ErrorAction Stop
}
```

**macOS (Zsh)**:

```bash
curl https://pyenv.run | bash
```

(If blocked, clone directly: `git clone https://github.com/pyenv/pyenv.git ~/.pyenv`.)

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$("$PYENV_ROOT/bin/pyenv" init - zsh)"' >> ~/.zshrc
source ~/.zshrc
"$HOME/.pyenv/bin/pyenv" --version
```

**Windows (PowerShell)**:

Use 64-bit Python on x64 Windows for the pinned dependencies; the pinned
[DuckDB](https://pypi.org/project/duckdb/1.1.3/#files) and
[pandas](https://pypi.org/project/pandas/2.2.3/#files) releases provide
CPython 3.12 Windows x64 wheels. The
[official PowerShell installer](https://pyenv-win.github.io/pyenv-win/docs/installation.html#powershell)
installs pyenv-win and updates your user environment variables; this
installation method does not require Git.

```powershell
$pyenvInstaller = Join-Path $env:TEMP "install-pyenv-win.ps1"
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile $pyenvInstaller -ErrorAction Stop
& $pyenvInstaller
```

Close the terminal application and reopen PowerShell so it picks up the
updated environment. For an integrated terminal, restart its host
application (for example, VS Code), then return to the project root.
Confirm the installation:

```powershell
pyenv --version
Get-Command pyenv
```

> If the script fails with "running scripts is disabled", run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`
> in that PowerShell session, then retry `& $pyenvInstaller`. This change
> lasts only for the current session. See [Windows troubleshooting](#windows-cannot-find-pyenv-or-runs-the-wrong-python)
> if pyenv or Python is still not found.

### 2. Install Python 3.12.6

**macOS**:

```bash
"$HOME/.pyenv/bin/pyenv" install -s 3.12.6
"$HOME/.pyenv/bin/pyenv" local 3.12.6
"$HOME/.pyenv/bin/pyenv" exec python --version # confirm: Python 3.12.6
```

**Windows** (PowerShell):

```powershell
pyenv install 3.12.6 # skip if already installed
pyenv rehash
pyenv local 3.12.6
pyenv which python
pyenv exec python --version # confirm: Python 3.12.6
```

### 3. Create the virtualenv and install Python dependencies

Run from the project root (the directory this README is in):

Use `pyenv exec python` to create the environment with the selected
Python version, even if `python3` or `python` on your PATH points to
another installation. An existing `.venv` keeps the Python version it
was created with, so recreate it after changing Python versions.
The macOS commands use the full path to the directly installed pyenv
to ensure another installation is not selected.

**macOS**:

```bash
rm -rf .venv

"$HOME/.pyenv/bin/pyenv" exec python -m venv .venv
.venv/bin/python --version # confirm: Python 3.12.6
.venv/bin/python -m pip install -r requirements.txt

.venv/bin/python scripts/generate_data.py
```

**Windows** (PowerShell):

```powershell
if (Test-Path -LiteralPath ".venv") {
Remove-Item -LiteralPath ".venv" -Recurse -Force -ErrorAction Stop
}

pyenv exec python -m venv .venv
.\.venv\Scripts\python.exe --version # confirm: Python 3.12.6
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe .\scripts\generate_data.py
```

These commands call the virtualenv directly, so activation is not needed.

### 4. Install dbt packages and load seeds

Run from the project root; these commands `cd` into `dbt/` and back out
on their own:

Close any DuckDB connection before cleanup, including a database viewer
or a Python session with the database open. Windows cannot delete files
that another process is using.

**macOS**:

```bash
rm -rf dbt/dev.duckdb dbt/dev.duckdb.wal dbt/target dbt/logs dbt/dbt_packages

cd dbt
../.venv/bin/dbt deps --profiles-dir .
cd ..
```

**Windows** (PowerShell):

```powershell
Get-Item -LiteralPath ".\dbt\dev.duckdb", ".\dbt\dev.duckdb.wal", ".\dbt\target", ".\dbt\logs", ".\dbt\dbt_packages" -ErrorAction SilentlyContinue |
Remove-Item -Recurse -Force -ErrorAction Stop

cd dbt
..\.venv\Scripts\dbt.exe deps --profiles-dir .
cd ..
```

The `dbt seed` command above loads the raw seed files into
`dbt/dev.duckdb`, a self-contained DuckDB database file.

Check it loaded by listing the tables: `.venv/bin/python
scripts/load_duckdb.py` (macOS) or `.\.venv\Scripts\python.exe
.\scripts\load_duckdb.py` (Windows). See [Query the
data](#query-the-data) below for more.

Don't run `dbt run`/`dbt test` yet -- `stg_products` is intentionally
empty and the metadata macro intentionally incomplete until you've done
the work in [What you'll do](#what-youll-do). `dbt run`/`dbt build` add
the staging and mart models to the same `dbt/dev.duckdb` file.

## Run models and tests

Once you have completed the model and macro, use the commands below
when prompted by [What you'll do](#what-youll-do). `run` builds models,
`test` checks them, and `build` runs seeds, models, and tests together.
Run from the project root:

**macOS**:

```bash
cd dbt
../.venv/bin/dbt <cmd> --profiles-dir .
cd ..
```

**Windows (PowerShell)**:

```powershell
cd dbt
..\.venv\Scripts\dbt.exe <cmd> --profiles-dir .
cd ..
```

## Query the data

[`scripts/load_duckdb.py`](scripts/load_duckdb.py) connects to
`dbt/dev.duckdb` and prints its tables when called without arguments.
To inspect data, pass one quoted SQL query. Include `limit 10` to show
only the first 10 rows.

Run from the project root:

**macOS**:

```bash
.venv/bin/python scripts/load_duckdb.py
.venv/bin/python scripts/load_duckdb.py "select * from stg_products limit 10"
```

**Windows** (PowerShell):

```powershell
.\.venv\Scripts\python.exe .\scripts\load_duckdb.py
.\.venv\Scripts\python.exe .\scripts\load_duckdb.py "select * from stg_products limit 10"
```

Tables available grow as you progress: seeds first (`raw_customers`,
`raw_products`, `raw_orders`, `raw_order_items`), then staging views as
you build them (`stg_products`, ...), then marts after a full
`dbt build` (`dim_customers`, `fct_order_items`,
`customer_order_summary`). Run the script with no arguments to just
list what's there.

## Recover a working state

[`scripts/apply_solution.py`](scripts/apply_solution.py) overwrites
[`stg_products.sql`](dbt/models/staging/stg_products.sql),
[`add_metadata_columns.sql`](dbt/macros/add_metadata_columns.sql), and
[`parse_manifest.py`](scripts/parse_manifest.py) with their finished
solution.

Run from the project root:

**macOS**:

```bash
.venv/bin/python scripts/apply_solution.py
```

**Windows** (PowerShell):

```powershell
.\.venv\Scripts\python.exe .\scripts\apply_solution.py
```

## Troubleshooting

### dbt fails with the wrong Python version

Check the virtualenv's interpreter from the project root:

**macOS**:

```bash
.venv/bin/python --version
```

**Windows (PowerShell)**:

```powershell
.\.venv\Scripts\python.exe --version
```

It must report `Python 3.12.6`. The version shown in your terminal
prompt does not confirm which Python an existing virtualenv uses.
If the version differs, repeat steps 2 and 3 to select Python 3.12.6,
recreate `.venv`, and reinstall dependencies. Then retry step 4.

### Windows cannot find pyenv or runs the wrong Python

Restart the terminal application (or VS Code for an integrated
terminal), return to the project root, and run:

```powershell
Get-Command pyenv -All
pyenv which python
pyenv exec python --version
```

The pyenv command should come from
`%USERPROFILE%\.pyenv\pyenv-win\bin`, and the selected Python should
come from `%USERPROFILE%\.pyenv\pyenv-win\versions\3.12.6`.
If pyenv is not found, check that its `bin` and `shims` directories
are on your user PATH using the
[official environment-variable instructions](https://pyenv-win.github.io/pyenv-win/docs/installation.html#add-system-settings).

If typing `python` opens the Microsoft Store or selects the Windows
App Installer instead, open **Manage app execution aliases** from the
Start menu and turn off the App Installer aliases for `python.exe` and
`python3.exe`. Then reopen the terminal. See the
[pyenv-win installation notes](https://pyenv-win.github.io/pyenv-win/docs/installation.html).

### Windows cleanup reports a file is in use

Close Python, dbt, and any database viewers that use this project, and
make sure your terminal is outside the directory being removed. If
you activated `.venv`, run `deactivate` first. Retry the cleanup;
do not continue if it failed to remove the old environment or database.

### Using Bash instead of Zsh

Step 1's pyenv setup is written for Zsh and wires `pyenv` into
`~/.zshrc`. On Bash, append the same three lines to `~/.bashrc` instead,
and change `init - zsh` to `init - bash`:

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$("$PYENV_ROOT/bin/pyenv" init - bash)"' >> ~/.bashrc
source ~/.bashrc
"$HOME/.pyenv/bin/pyenv" --version
```

Every other command in this README calls `.venv`/`dbt` binaries
directly rather than activating the environment, so nothing else
differs between Bash and Zsh.
