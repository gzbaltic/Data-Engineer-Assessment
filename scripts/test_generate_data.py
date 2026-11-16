"""Tests for generate_data.py.

Usage (from the project root, /Users/gzenkner/projects/de_assessment):
    pytest scripts/test_generate_data.py
"""

import random

from faker import Faker

from generate_data import SEED, generate_customers, generate_orders_and_items, generate_products


def _reseed():
    """Reset Faker/random to the generator's fixed seed."""
    Faker.seed(SEED)
    random.seed(SEED)


def test_customers_are_reproducible_and_contain_duplicates():
    """Type: Proactive -- guards against the generator drifting if Faker/random usage changes.

    Why: the assessment's expected data-quality issues (duplicate customer
    rows) only exist because generation is deterministic under a fixed seed;
    if that broke, the dbt tests built around those issues would stop
    meaning anything.

    Expected: regenerating customers twice gives identical rows, and at
    least one customer_id appears more than once (the intentional
    duplicate-export bug).

    Unexpected: two runs produce different data, or no duplicate customer
    rows exist at all.
    """
    _reseed()
    first_run = generate_customers()
    _reseed()
    second_run = generate_customers()
    assert first_run == second_run

    customer_ids = [row["customer_id"] for row in first_run]
    assert len(customer_ids) != len(set(customer_ids))


def test_products_contain_one_negative_price():
    """Type: Proactive -- guards against the generator drifting if random usage changes.

    Why: stg_products filters out negative prices, and that filter is only
    exercised if the raw data actually contains one.

    Expected: exactly one product has a unit_price below zero.

    Unexpected: zero negative-priced products (the filter test becomes a
    no-op) or more than one.
    """
    _reseed()
    products = generate_products()
    negative_price_products = [p for p in products if p["unit_price"] < 0]
    assert len(negative_price_products) == 1


def test_order_items_contain_orphaned_and_invalid_rows():
    """Type: Proactive -- guards against the generator drifting if random usage changes.

    Why: the assessment's "late-arriving data" and "bad quantity" scenarios
    in stg_order_items only exist if the raw data actually contains them.

    Expected: at least one order_item references an order_id that doesn't
    exist in the generated orders, and at least one has a quantity of zero
    or less.

    Unexpected: every order_item has a valid order_id and a positive
    quantity.
    """
    _reseed()
    customer_ids = [row["customer_id"] for row in generate_customers()]
    product_ids = [row["product_id"] for row in generate_products()]
    orders, order_items = generate_orders_and_items(customer_ids, product_ids)

    order_ids = {order["order_id"] for order in orders}
    orphaned = [item for item in order_items if item["order_id"] not in order_ids]
    assert len(orphaned) > 0

    invalid_quantity = [item for item in order_items if item["quantity"] <= 0]
    assert len(invalid_quantity) > 0
