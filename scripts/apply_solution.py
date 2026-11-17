"""Write the completed versions of the assessment's stub files.

Overwrites the stub models/macros (stg_products.sql,
add_metadata_columns.sql, fct_order_items.sql) with their finished
solution, so you can get back to a known-working state if something
goes wrong while building them out yourself.

Usage (from the project root, /Users/gzenkner/projects/Data-Engineer-Assessment):
    "$(pwd)/.venv/bin/python" scripts/apply_solution.py
"""

from pathlib import Path

DBT_DIR = Path("dbt")

SOLUTIONS = {
    DBT_DIR / "models" / "staging" / "stg_products.sql": """\
with raw_products as (

    select
        product_id,
        product_name,
        category,
        cast(unit_price as decimal(10, 2)) as unit_price
    from {{ ref('raw_products') }}

)

select
    product_id,
    product_name,
    category,
    unit_price
from raw_products
-- A negative unit_price is a known data-entry error upstream, not a valid price.
where unit_price >= 0
""",
    DBT_DIR / "macros" / "add_metadata_columns.sql": """\
{% macro add_metadata_columns() %}
    current_timestamp as dbt_loaded_at,
    '{{ invocation_id }}' as dbt_invocation_id
{% endmacro %}
""",
    DBT_DIR / "models" / "marts" / "fct_order_items.sql": """\
with order_items as (

    select order_item_id, order_id, product_id, quantity
    from {{ ref('stg_order_items') }}

),

orders as (

    select order_id, customer_id, order_date, status
    from {{ ref('stg_orders') }}

)

select
    order_items.order_item_id,
    order_items.order_id,
    orders.customer_id,
    orders.order_date,
    orders.status,
    order_items.product_id,
    order_items.quantity,
    {{ add_metadata_columns() }}
from order_items
inner join orders on order_items.order_id = orders.order_id
""",
}


def main() -> None:
    """Overwrite each stub file with its completed solution."""
    for path, contents in SOLUTIONS.items():
        path.write_text(contents)
        print(f"Wrote solution: {path}")


if __name__ == "__main__":
    main()
