"""Tests for generate_data.py.

Usage (from the project root, /Users/gzenkner/projects/de_assessment):
    "$(pwd)/.venv/bin/pytest" scripts/test_generate_data.py
"""

import random

import pandas as pd
from faker import Faker

from generate_data import (
    SEED,
    build_customers,
    build_order_items,
    build_orders,
    build_products,
    fake,
)


def _reseed():
    """Reset Faker/random to the generator's fixed seed."""
    Faker.seed(SEED)
    random.seed(SEED)
    fake.unique.clear()


def _fake_olist_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["cust_b", "cust_a", "cust_c"],
            "customer_state": ["SP", "RJ", "MG"],
        }
    )


def _fake_olist_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["ord_1", "ord_2"],
            "customer_id": ["cust_a", "cust_b"],
            "order_purchase_timestamp": ["2023-05-01 10:00:00", "2023-06-02 11:00:00"],
            "order_status": ["delivered", "canceled"],
        }
    )


def _fake_olist_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": ["prod_x", "prod_y"],
            "product_category_name": ["beleza_saude", "esporte_lazer"],
        }
    )


def _fake_olist_order_items(n: int = 300) -> pd.DataFrame:
    """Build enough rows for the 1%-chance bad-quantity injection to fire reliably."""
    return pd.DataFrame(
        {
            "order_id": ["ord_1" if i % 2 == 0 else "ord_2" for i in range(n)],
            "product_id": ["prod_x" if i % 2 == 0 else "prod_y" for i in range(n)],
            "price": [100.0 if i % 2 == 0 else 50.0 for i in range(n)],
        }
    )


def test_customers_are_reproducible_and_contain_duplicates():
    """Type: Proactive -- guards against the generator drifting if Faker/random usage changes.

    Why: the assessment's expected data-quality issues (duplicate customer
    rows) only exist because generation is deterministic under a fixed seed;
    if that broke, the dbt tests built around those issues would stop
    meaning anything.

    Expected: regenerating customers twice from the same real Olist rows
    gives identical output, and at least one customer_id appears more than
    once (the intentional duplicate-export bug).

    Unexpected: two runs produce different data, or no duplicate customer
    rows exist at all.
    """
    _reseed()
    first_run, _ = build_customers(_fake_olist_customers())
    _reseed()
    second_run, _ = build_customers(_fake_olist_customers())
    assert first_run == second_run

    customer_ids = [row["customer_id"] for row in first_run]
    assert len(customer_ids) != len(set(customer_ids))


def test_products_contain_one_negative_price():
    """Type: Proactive -- guards against the generator drifting if random usage changes.

    Why: stg_products filters out negative prices, and that filter is only
    exercised if the raw data actually contains one.

    Expected: exactly one product has a unit_price below zero, even though
    both real products' derived prices (from order_items) are positive.

    Unexpected: zero negative-priced products (the filter test becomes a
    no-op) or more than one.
    """
    _reseed()
    products, _ = build_products(_fake_olist_products(), _fake_olist_order_items())
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
    customers_raw = _fake_olist_customers()
    products_raw = _fake_olist_products()
    orders_raw = _fake_olist_orders()
    order_items_raw = _fake_olist_order_items()

    _, customer_id_map = build_customers(customers_raw)
    _, product_id_map = build_products(products_raw, order_items_raw)
    orders = build_orders(orders_raw, customer_id_map)
    order_items = build_order_items(order_items_raw, orders_raw, product_id_map)

    order_ids = {order["order_id"] for order in orders}
    orphaned = [item for item in order_items if item["order_id"] not in order_ids]
    assert len(orphaned) > 0

    invalid_quantity = [item for item in order_items if item["quantity"] <= 0]
    assert len(invalid_quantity) > 0
