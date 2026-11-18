"""Load and inspect the DuckDB warehouse built by dbt.

Usage (from the project root, /Users/gzenkner/projects/Data-Engineer-Assessment):
    "$(pwd)/.venv/bin/python" scripts/load_duckdb.py [table_name ...]

With no arguments, prints the list of tables. With one or more table
names, also prints the first 10 rows of each.
"""

import sys

import duckdb

DB_PATH = "dbt/dev.duckdb"


def main() -> None:
    """Connect to the DuckDB warehouse and print its tables (and optionally samples)."""
    con = duckdb.connect(DB_PATH, read_only=True)

    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(query)
        print(con.sql(f"{query}"))

    else:
        print(con.sql("show tables"))

    con.close()


if __name__ == "__main__":
    main()
