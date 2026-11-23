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
    # TODO implement



def get_tests_by_model(manifest: dict) -> dict[str, list[str]]:
    """Return a mapping of model name to the names of tests that run against it."""
    # TODO implement


def main() -> None:
    """Print each model's tests."""
    # TODO implement



if __name__ == "__main__":
    main()
