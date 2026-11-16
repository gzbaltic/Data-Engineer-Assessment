"""Generate synthetic raw CSVs for the data engineering assessment.

Produces a small retail dataset (customers, products, orders, order items)
with deliberately realistic data-quality issues -- duplicate rows, missing
emails, orphaned foreign keys, and a few out-of-range quantities/prices --
so the dbt models built on top of it have real cleaning/testing work to do.

Usage (from the project root, /Users/gzenkner/projects/de_assessment):
    python scripts/generate_data.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

SEED = 42
N_CUSTOMERS = 500
N_PRODUCTS = 120
N_ORDERS = 2000
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "dbt" / "seeds"

fake = Faker()
Faker.seed(SEED)
random.seed(SEED)

PRODUCT_CATEGORIES = [
    "Electronics",
    "Home & Kitchen",
    "Sports & Outdoors",
    "Books",
    "Toys & Games",
    "Beauty",
]


def generate_customers() -> list[dict]:
    """Build the raw customers rows, including a handful of duplicates and blank emails."""
    rows = []
    for customer_id in range(1, N_CUSTOMERS + 1):
        rows.append(
            {
                "customer_id": customer_id,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                # ~4% of emails missing, as would happen with an optional signup field.
                "email": fake.email() if random.random() > 0.04 else "",
                "signup_date": fake.date_between(start_date="-3y", end_date="-1d").isoformat(),
                "country": fake.country(),
            }
        )
    # Duplicate a handful of customer rows verbatim, simulating an upstream export bug.
    duplicates = random.sample(rows, k=15)
    rows.extend(duplicates)
    random.shuffle(rows)
    return rows


def generate_products() -> list[dict]:
    """Build the raw products rows, including one negative price typo."""
    rows = []
    for product_id in range(1, N_PRODUCTS + 1):
        price = round(random.uniform(5, 500), 2)
        rows.append(
            {
                "product_id": product_id,
                "product_name": fake.word().capitalize() + " " + fake.word().capitalize(),
                "category": random.choice(PRODUCT_CATEGORIES),
                "unit_price": price,
            }
        )
    # One data-entry typo: a negative price that should never happen downstream.
    rows[random.randrange(len(rows))]["unit_price"] = -19.99
    return rows


def generate_orders_and_items(
    customer_ids: list[int], product_ids: list[int]
) -> tuple[list[dict], list[dict]]:
    """Build raw orders and order_items, including a few orphaned/duplicate rows."""
    orders = []
    order_items = []
    item_id = 1
    start = date(2023, 1, 1)
    end = date(2024, 12, 31)

    for order_id in range(1, N_ORDERS + 1):
        order_date = start + timedelta(days=random.randrange((end - start).days))
        status = random.choices(
            ["completed", "shipped", "cancelled", "pending"],
            weights=[0.7, 0.15, 0.1, 0.05],
        )[0]
        orders.append(
            {
                "order_id": order_id,
                "customer_id": random.choice(customer_ids),
                "order_date": order_date.isoformat(),
                "status": status,
            }
        )

        for _ in range(random.randint(1, 5)):
            quantity = random.randint(1, 4)
            # Rare bad record: a zero/negative quantity that slipped through upstream.
            if random.random() < 0.01:
                quantity = random.choice([0, -1])
            order_items.append(
                {
                    "order_item_id": item_id,
                    "order_id": order_id,
                    "product_id": random.choice(product_ids),
                    "quantity": quantity,
                }
            )
            item_id += 1

    # A handful of order_items pointing at an order_id that doesn't exist --
    # simulates a late-arriving/out-of-order upstream load.
    for _ in range(8):
        order_items.append(
            {
                "order_item_id": item_id,
                "order_id": N_ORDERS + random.randint(1000, 9999),
                "product_id": random.choice(product_ids),
                "quantity": random.randint(1, 3),
            }
        )
        item_id += 1

    return orders, order_items


def write_csv(rows: list[dict], path: Path) -> None:
    """Write rows to a CSV file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Generate all raw seed CSVs under dbt/seeds/."""
    customers = generate_customers()
    products = generate_products()
    customer_ids = [c["customer_id"] for c in customers]
    product_ids = [p["product_id"] for p in products]
    orders, order_items = generate_orders_and_items(customer_ids, product_ids)

    write_csv(customers, OUTPUT_DIR / "raw_customers.csv")
    write_csv(products, OUTPUT_DIR / "raw_products.csv")
    write_csv(orders, OUTPUT_DIR / "raw_orders.csv")
    write_csv(order_items, OUTPUT_DIR / "raw_order_items.csv")

    print(f"Wrote {len(customers)} customers, {len(products)} products, "
          f"{len(orders)} orders, {len(order_items)} order_items to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
