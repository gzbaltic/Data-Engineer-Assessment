"""Candidate task: query the DuckDB warehouse built by dbt.

Usage (from the project root, /Users/gzenkner/projects/de_assessment):
    python scripts/query_data.py

Fill in the TODOs below with SQL queries against the marts models
(`dim_customers`, `fct_order_items`, `customer_order_summary`).
"""

import duckdb
import pandas as pd

DB_PATH = "dbt/dev.duckdb"


def main() -> None:
    """Connect to the DuckDB warehouse and answer the assessment questions."""
    con = duckdb.connect(DB_PATH, read_only=True)

    customers: pd.DataFrame = con.sql("select * from dim_customers").df()
    order_items: pd.DataFrame = con.sql("select * from fct_order_items").df()
    order_summary: pd.DataFrame = con.sql("select * from customer_order_summary").df()

    # TODO: Who are the top 5 customers by lifetime value?

    # TODO: What is the total revenue per product?

    # TODO: How many orders were placed per month?

    con.close()


if __name__ == "__main__":
    main()
