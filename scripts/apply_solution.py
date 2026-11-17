"""Write the completed versions of the assessment's stub files.

Overwrites the stub model and macro (stg_products.sql,
add_metadata_columns.sql) with their finished solution, so you can get
back to a known-working state if something goes wrong while building
them out yourself.

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
    unit_price,
    {{ add_metadata_columns() }}
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
}


def main() -> None:
    """Overwrite each stub file with its completed solution."""
    for path, contents in SOLUTIONS.items():
        path.write_text(contents)
        print(f"Wrote solution: {path}")


if __name__ == "__main__":
    main()
