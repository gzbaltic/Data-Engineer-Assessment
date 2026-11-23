"""Write the completed versions of the assessment's stub files.

Overwrites the stub model, macro, and script (stg_products.sql,
add_metadata_columns.sql, parse_manifest.py) with their finished
solution, so you can get back to a known-working state if something
goes wrong while building them out yourself.

Usage (from the project root, /Users/gzenkner/projects/Data-Engineer-Assessment):
    "$(pwd)/.venv/bin/python" scripts/apply_solution.py
"""

from pathlib import Path

DBT_DIR = Path("dbt")
SCRIPTS_DIR = Path("scripts")

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
    SCRIPTS_DIR / "parse_manifest.py": '''\
"""Summarize dbt test coverage from the compiled manifest.

Reads dbt/target/manifest.json (produced by `dbt build` or `dbt compile`)
and prints, for every model, the tests that run against it.

Usage (from the project root, /Users/gzenkner/projects/Data-Engineer-Assessment):
    "$(pwd)/.venv/bin/python" scripts/parse_manifest.py
"""

import json
from pathlib import Path

MANIFEST_PATH = Path("dbt/target/manifest.json")


def load_manifest() -> dict:
    """Load the dbt manifest JSON from disk."""
    return json.loads(MANIFEST_PATH.read_text())


def get_tests_by_model(manifest: dict) -> dict[str, list[str]]:
    """Return a mapping of model name to the names of tests that run against it."""
    tests_by_model: dict[str, list[str]] = {}
    for node in manifest["nodes"].values():
        if node["resource_type"] != "test":
            continue
        for dependency in node["depends_on"]["nodes"]:
            if not dependency.startswith("model."):
                continue
            model_name = dependency.split(".")[-1]
            tests_by_model.setdefault(model_name, []).append(node["name"])
    return tests_by_model


def main() -> None:
    """Print each model's tests."""
    manifest = load_manifest()
    tests_by_model = get_tests_by_model(manifest)
    for model, tests in sorted(tests_by_model.items()):
        print(f"{model}: {len(tests)} test(s)")
        for test in tests:
            print(f"  - {test}")


if __name__ == "__main__":
    main()
''',
}


def main() -> None:
    """Overwrite each stub file with its completed solution."""
    for path, contents in SOLUTIONS.items():
        path.write_text(contents)
        print(f"Wrote solution: {path}")


if __name__ == "__main__":
    main()
