"""Load and inspect the DuckDB warehouse built by dbt.

Usage (from the project root, /Users/gzenkner/projects/de_assessment):
    python scripts/load_duckdb.py
"""

import duckdb

DB_PATH = "dbt/dev.duckdb"


def main() -> None:
    """Connect to the DuckDB warehouse and print its tables."""
    con = duckdb.connect(DB_PATH, read_only=True)
    print(con.sql("show tables"))

    # TODO: load table(s) into a DataFrame, e.g.
    # df = con.sql("select * from customer_order_summary").df()

    con.close()


if __name__ == "__main__":
    main()
