"""Load and inspect the DuckDB warehouse built by dbt.

Usage (from the project root, /Users/gzenkner/projects/Data-Engineer-Assessment):
    "$(pwd)/.venv/bin/python" scripts/load_duckdb.py [table_name]

With no argument, prints the list of tables. With a table name, also
prints the first 10 rows of that table.
"""

import sys

import duckdb

DB_PATH = "dbt/dev.duckdb"


def main() -> None:
    """Connect to the DuckDB warehouse and print its tables (and optionally a sample)."""
    con = duckdb.connect(DB_PATH, read_only=True)
    print(con.sql("show tables"))

    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        print(con.sql(f"select * from {table_name} limit 10"))

    con.close()


if __name__ == "__main__":
    main()
